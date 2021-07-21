from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .forms import ApplicantForm
from oauth.decorators import redirect_if_authenticated, students_only
from .models import WaitlistApplicant
import datetime

lock = False


@redirect_if_authenticated
def login(request):
    return render(request, 'portal/index0.html')


@login_required
@students_only
def index(request):
    print(request.user.username)
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
                applicant.save()
                applicant.refresh_waitlist_ahead(-1, 0)
            elif applicant.occupying > 1:
                applicant.waitlist_t1 = -1
                applicant.waitlist_mt = 0
                applicant.save()
                applicant.refresh_waitlist_ahead(-1, -1)

        elif request.POST.get('post') == 'vacate':
            applicant.vacated = applicant.occupying
            applicant.vacated_on = datetime.date.today()
            if applicant.occupying == 1:
                applicant.waitlist_t1 = -3
            else:
                applicant.waitlist_mt = -3
            applicant.occupying = 0
            if applicant.waitlist_mt > 0:
                applicant.refresh_waitlist_ahead(-1, 0)
            else:
                applicant.refresh_waitlist_ahead(-1, -1)
            applicant.delete()
            applicant.id = None
            applicant.save()

        elif request.POST.get('post') == 'reapply':
            applicant.offer = applicant.occupying = applicant.vacated = 0
            applicant.refresh_waitlist()
            applicant.refresh_waitlist_ahead(0, 0)

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
    instance = None
    try:
        instance = WaitlistApplicant.objects.get(roll_number=request.user.username)
        if instance.vacated == 0 and instance.waitlist_mt > -2:
            return redirect(reverse('index'))
    except ObjectDoesNotExist:
        pass

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
            instance.delete()
        if form.is_valid():
            form.instance.save()
            return redirect(reverse('thanks'))
        else:
            instance.save()

    return render(request, 'portal/form.html', {
        'form': form,
        'undertaking_fields': {'spouse_name': True, 'spouse_roll_number': False, 'spouse_designation': False},
        'retrying': retrying
    })
