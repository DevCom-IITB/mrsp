from django.forms import model_to_dict
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .forms import ApplicantForm, EditDocsForm
from oauth.decorators import redirect_if_authenticated, students_only
from .models import WaitlistApplicant
import datetime
from django.db.models import Q

from .mails import mail_registered, mail_occupied, mail_vacated

lock = False


@redirect_if_authenticated
def login(request):
    return render(request, 'portal/index0.html')


@login_required
@students_only
def index(request):
    try:
        applicant = WaitlistApplicant.objects.get(roll_number=str(request.user.username))
    except ObjectDoesNotExist:
        return render(request, 'portal/index1.html', {
            'user': request.user
        })

    if request.method == 'POST':
        if request.POST.get('post') == 'decline':
            applicant.decline_offer()

        elif request.POST.get('post') == 'accept':
            applicant.occupying = applicant.offer
            applicant.occupied_on = datetime.date.today()
            applicant.offer = 0
            if applicant.occupying == 1:
                applicant.waitlist_t1 = 0
                applicant.waitlist_t = -1
                applicant.waitlist_m = -1
                applicant.save()
                
            elif applicant.occupying == 2 :
                applicant.waitlist_t1 = -1
                applicant.waitlist_m = 0
                applicant.waitlist_t = -1
                applicant.save()
                #applicant.refresh_waitlist_ahead(0, -1, 0)
            elif applicant.occupying ==3 :
                applicant.waitlist_t1 = -1
                applicant.waitlist_t = 0
                applicant.waitlist_m = -1
                applicant.save()
                #applicant.refresh_waitlist_ahead(0, 0, -1)
            applicant.refresh_waitlist_ahead(-1, -1, -1)
            mail_occupied(applicant)

        elif request.POST.get('post') == 'vacate':
            applicant.vacated = applicant.occupying
            applicant.vacated_on = datetime.date.today()
            if applicant.occupying == 1:
                applicant.waitlist_t1 = -3
                applicant.refresh_waitlist_behind(0,+1,+1)
                applicant.waitlist_m = 1
                applicant.waitlist_t = 1
            elif applicant.occupying == 2:
                applicant.waitlist_m = -3
                applicant.refresh_waitlist_behind(+1,0,+1)
                applicant.waitlist_t1 = 1
                applicant.waitlist_t = 1
            elif applicant.occupying == 3:
                applicant.waitlist_t = -3
                applicant.refresh_waitlist_behind(+1,+1,0)
                applicant.waitlist_m = 1
                applicant.waitlist_t1 = 1
            applicant.occupying = 0
            applicant.delete()
            # applicant.id = None
            #applicant.save()

            #mail_vacated(applicant)

        elif request.POST.get('post') == 'reapply':
            applicant.offer = applicant.occupying = applicant.vacated = 0
            applicant.refresh_waitlist()
            applicant.refresh_waitlist_ahead(0, 0, 0)

        return redirect(reverse('index'))
    else:
        return render(request, 'portal/index2.html', {
            'user': request.user,
            'instance': applicant,
            'status': [1, 3, 3, 3, 2, 3, 3, 3, 4][applicant.get_status_id()],
            'offered_hostel': applicant.hostel_radio_choices[applicant.offer][1],
            'expiry': applicant.get_offer_expiry_date() if applicant.offer != 0 else None,
            'occupying': applicant.hostel_radio_choices[applicant.occupying][1],
            'vacated': applicant.hostel_radio_choices[applicant.vacated][1],
            'occupied_on': applicant.occupied_on,
            'vacated_on': applicant.vacated_on
        })

def waitlist(request):
    arr = [WaitlistApplicant.objects.filter(
        (Q(marriage_certificate_verified=False) | Q(photograph_verified=False) | Q(grade_sheet_verified=False)
         | Q(recommendation_verified=False)) & Q(acad_verified=True)),

        WaitlistApplicant.objects.filter(Q(waitlist_t1__gt=0)).order_by("waitlist_t1"),
        WaitlistApplicant.objects.filter(Q(waitlist_m__gt=0)).order_by("waitlist_m"),
        WaitlistApplicant.objects.filter(Q(waitlist_t__gt=0)).order_by("waitlist_t"),
        WaitlistApplicant.objects.filter(Q(occupying=1) & Q(acad_verified=True)).order_by("-application_date"),
        WaitlistApplicant.objects.filter(Q(occupying=2) & Q(acad_verified=True)).order_by("-application_date"),
        WaitlistApplicant.objects.filter(Q(occupying=3) & Q(acad_verified=True)).order_by("-application_date"),

        WaitlistApplicant.objects.filter(Q(waitlist_t1=-3) |  Q(waitlist_m=-3) | Q(waitlist_t=-3))]

    tab = int(request.GET.get('tab') or '1')
    return render(request, 'portal/waitlist.html', {
        'arr': arr[tab],
        'tab': tab,
    })
@login_required
@students_only
def rules(request):
    return render(request, 'portal/rules.html')


@login_required
@students_only
def thanks(request):
    return render(request, 'portal/thanks.html', {
        'form': ApplicantForm()
    })


@login_required
@students_only
def apply(request):
    try:
        instance = WaitlistApplicant.objects.get(roll_number=request.user.username)
        if (instance.vacated == 0 and (instance.waitlist_m > -2 or instance.waitlist_t > -2)) and (
                instance.acad_verified or instance.acad_feedback == ''):
            return redirect(reverse('index'))
    except ObjectDoesNotExist:
        instance = None

    form_data = dict()
    retrying = False

    if request.method == 'POST':
        retrying = True
        form_data = request.POST.copy()

    form_data['name'] = request.user.get_full_name()
    form_data['roll_number'] = request.user.username
    form_data['email'] = request.user.email

    form = ApplicantForm(form_data, files=request.FILES)

    if request.method == 'POST':
        if instance:
            #instance.delete()
            if not form.is_valid():
                instance.save()
        else:
            if form.is_valid():
                form.instance.save()
                mail_registered(applicant=form.instance)
                return redirect(reverse('thanks'))

    return render(request, 'portal/form.html', {
        'form': form,
        'undertaking_fields': {'spouse_name': True, 'spouse_roll_number': False, 'spouse_designation': False},
        'retrying': retrying
    })


def edit_docs(request):
    try:
        instance = WaitlistApplicant.objects.get(roll_number=request.user.username)
    except ObjectDoesNotExist:
        return redirect(reverse('index'))

    retrying = False
    vf_indices = []
    if not instance.marriage_certificate_verified:
        instance.marriage_certificate = ''
        vf_indices.append(0)
    if not instance.photograph_verified:
        instance.photograph = ''
        vf_indices.append(1)
    if not instance.grade_sheet_verified:
        instance.grade_sheet = ''
        vf_indices.append(2)
    if not instance.recommendation_verified:
        instance.recommendation = ''
        vf_indices.append(3)

    if instance.get_status_id() != 4 or instance.hcu_feedback == '':
        return redirect(reverse('index'))

    form = EditDocsForm(instance=instance)

    if request.method == 'POST':
        form = EditDocsForm(instance=instance, files=request.FILES)
        if form.is_valid():
            form.save()
            instance.form_updated = True
            instance.save()
            return redirect(reverse('index'))
        else:
            retrying = True

    return render(request, 'portal/edit_docs.html', {
        'form': form,
        'retrying': retrying,
        'indices': vf_indices
    })
