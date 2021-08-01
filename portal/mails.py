from typing import Any

from django.template.loader import render_to_string

from portal.models import WaitlistApplicant
import datetime
from django.core import mail
from mrsp.settings import DEFAULT_FROM_EMAIL

from threading import Thread


def mail_function(applicant: WaitlistApplicant, subject: str, template: str, context: Any):
    def fn():
        try:
            mail.send_mail(
                subject,
                '',
                DEFAULT_FROM_EMAIL,
                [applicant.email],
                html_message=render_to_string(template, context)
            )
        except:
            pass

    Thread(target=fn).start()


def mail_registered(applicant: WaitlistApplicant):
    mail_function(applicant, 'MRSP: Successful Registration', 'mails/registered.html', {
        'applicant': applicant
    })


def mail_waitlisted(applicant: WaitlistApplicant):
    mail_function(applicant, 'MRSP: Academic Details and Supporting Documents Verified', 'mails/waitlisted.html', {
        'applicant': applicant
    })


def mail_shortlisted(applicant: WaitlistApplicant):
    mail_function(applicant,
                  f'MRSP: IMPORTANT: Shortlisted for {applicant.hostel_radio_choices[int(applicant.offer)][1]}',
                  'mails/shortlisted.html', {
                      'applicant': applicant,
                      'offered': applicant.hostel_radio_choices[int(applicant.offer)][1],
                      'expiry': (applicant.offered_on + datetime.timedelta(days=7)).strftime("%d/%m/%Y")
                  })


def mail_occupied(applicant: WaitlistApplicant):
    mail_function(applicant, f'MRSP: Occupying {applicant.hostel_radio_choices[applicant.occupying][1]}',
                  'mails/occupied.html', {
                      'applicant': applicant,
                      'occupying': applicant.hostel_radio_choices[applicant.occupying][1],
                      'occupied_on': applicant.occupied_on.strftime("%d/%m/%Y")
                  })


def mail_vacated(applicant: WaitlistApplicant):
    mail_function(applicant, f'MRSP: Vacated {applicant.hostel_radio_choices[applicant.vacated][1]}',
                  'mails/vacated.html', {
                      'applicant': applicant,
                      'vacated': applicant.hostel_radio_choices[applicant.vacated][1],
                      'vacated_on': applicant.vacated_on.strftime("%d/%m/%Y")
                  })


def mail_acad_feedback(applicant: WaitlistApplicant):
    mail_function(applicant, f'MRSP: IMPORTANT: Feedback from the Academic Section',
                  'mails/acad_feedback.html', {
                      'applicant': applicant
                  })


def mail_hcu_feedback(applicant: WaitlistApplicant):
    mail_function(applicant, f'MRSP: IMPORTANT: Feedback from the HCU Office',
                  'mails/hcu_feedback.html', {
                      'applicant': applicant
                  })
