from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from portal.models import WaitlistApplicant
from django.forms.models import model_to_dict
from django.db.models import Q
from .forms import ApplicantDetailsFormAcad, HCUVerificationForm, HCUSeatOfferForm, HCUApplicantDetailsForm

from oauth.decorators import acad_only, hcu_only, super_admins
from portal.mails import mail_waitlisted, mail_shortlisted, mail_hcu_feedback, mail_acad_feedback

import datetime


@login_required
@acad_only
def acad_admin(request):
    return render(request, 'admin2/acad.html', {
        'user': request.user,
        'unverified_arr': WaitlistApplicant.objects.filter(acad_verified=False),
        'super_admins': super_admins
    })


@login_required
@acad_only
def acad_details(request):
    if request.method == 'POST':
        applicant = WaitlistApplicant.objects.get(id=request.POST.get('id'))
        applicant.acad_feedback = request.POST.get('acad_feedback')
        applicant.acad_verified = request.POST.get('verification_status') == 'verified'

        applicant.save()

        if not applicant.acad_verified and applicant.acad_feedback:
            mail_acad_feedback(applicant)

        return redirect(reverse('admin_acad'))
    else:
        applicant = WaitlistApplicant.objects.get(roll_number=request.GET.get('roll_number'))
        form = ApplicantDetailsFormAcad(instance=applicant)

        return render(request, 'admin2/acad_details.html', {
            'applicant': form,
            'super_admins': super_admins
        })


@login_required
@hcu_only
def hcu_admin(request):
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
    return render(request, 'admin2/hcu.html', {
        'arr': arr[tab],
        'tab': tab,
        'super_admins': super_admins
    })


@login_required
@hcu_only
def hcu_details(request):
    if request.method == 'GET':
        applicant = WaitlistApplicant.objects.get(roll_number=request.GET.get('roll_number'))
        details_form = HCUApplicantDetailsForm(instance=applicant)
        verification_form = HCUVerificationForm(instance=applicant)
        seat_form = HCUSeatOfferForm(instance=applicant)

        status_id = applicant.get_status_id()

        return render(request, 'admin2/hcu_details.html', {
            'instance': applicant,
            'details_form': details_form,
            'positive_only': ['waitlist_t1', 'waitlist_m', 'waitlist_t'],
            'verification_form': verification_form,
            'seat_form': seat_form,
            'expiry': applicant.get_offer_expiry_date() if applicant.offer != 0 else None,
            'status': [0, 3, 2, 2, 1, 2, 3, 2, 4][status_id],
            'currently_occupying': applicant.hostel_radio_choices[applicant.occupying][1],
            'vacated': applicant.hostel_radio_choices[applicant.vacated][1],
            'super_admins': super_admins
        })

    elif request.method == 'POST':

        applicant_id = request.POST.get('id')
        status = request.POST.get('status')
        applicant = WaitlistApplicant.objects.get(id=applicant_id)

        # if request.POST.get('file_index'):
        #     file = [applicant.marriage_certificate, applicant.photograph,
        #             applicant.grade_sheet, applicant.recommendation][int(request.POST.get('file_index'))]
        #
        #     filename = file.name.split('/')[-1]
        #     response = HttpResponse(file.file, content_type='text/plain')
        #     response['Content-Disposition'] = 'attachment; filename=%s' % filename
        #
        #     return response

        if status == '1':
            applicant.marriage_certificate_verified = eval(request.POST.get('marriage_certificate_verified'))
            applicant.photograph_verified = eval(request.POST.get('photograph_verified'))
            applicant.grade_sheet_verified = eval(request.POST.get('grade_sheet_verified'))
            applicant.recommendation_verified = eval(request.POST.get('recommendation_verified'))
            applicant.hcu_feedback = request.POST.get('hcu_feedback')
            applicant.form_updated = False
            applicant.save()

            if applicant.get_status_id() == 3:
                applicant.refresh_waitlist()
                applicant.refresh_waitlist_ahead(0, 0, 0)
                mail_waitlisted(applicant)
            elif applicant.hcu_feedback:
                mail_hcu_feedback(applicant)

        elif status == '2':
            applicant.offer = request.POST.get('offer')
            applicant.offered_on = datetime.date.today()
            applicant.save()
            mail_shortlisted(applicant)

        return redirect("admin_hcu")


@login_required
@hcu_only
def view_file(request):
    if request.method == 'GET':
        roll_number = request.GET.get('roll_number')
        applicant = WaitlistApplicant.objects.get(roll_number=roll_number)

        doc_id = request.GET.get('doc')

        if doc_id.endswith('verified'):
            t = doc_id.split('_')
            t.pop()
            doc_id = '_'.join(t)

        file = model_to_dict(applicant)[doc_id]

        return HttpResponse(file.read(), content_type="application/pdf")
