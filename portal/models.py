from django.db import models
from django.core.validators import RegexValidator, FileExtensionValidator
from django.contrib.auth.models import User
import datetime
from . import db_lock


class ApplicantBase(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return self.roll_number

    name = models.CharField(max_length=128, default='')
    roll_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=128, default='')
    phone_number = models.CharField(max_length=10, validators=[RegexValidator(
        regex='^[0-9]{10}$',
        message='Enter a 10-digit number without the country code, e.g., 9876543210.'
    )], default='')
    department = models.CharField(max_length=128, help_text='Example: \'Electrical Engineering\'', default='')
    permanent_address = models.TextField(default='')

    fellowship = models.CharField(max_length=15, choices=[
        ('Institute', 'Institute'),
        ('CSIR', 'CSIR'),
        ('UGC', 'UGC')
    ], default='', help_text='Select one.')

    fellowship_date = models.DateField(verbose_name='Date from which fellowship is awarded', null=True)
    course_work_completes_on = models.DateField(help_text='Enter the expected date.', null=True)

    spouse_name = models.CharField(max_length=128, default='')
    spouse_roll_number = models.CharField(max_length=128, help_text='Leave blank if inapplicable', blank=True,
                                          null=True, default='')
    spouse_designation = models.CharField(max_length=128, help_text='Leave blank if inapplicable', blank=True,
                                          null=True, default='')

    pdf_validator = FileExtensionValidator(allowed_extensions=['pdf'])

    marriage_certificate = models.FileField(upload_to='marriage_certificates/', default='',
                                            help_text='PDF only', validators=[pdf_validator])
    photograph = models.FileField(upload_to='photographs', verbose_name='Joint photograph with spouse', default='',
                                  help_text='PDF only', validators=[pdf_validator])
    grade_sheet = models.FileField(upload_to='grade_sheets', verbose_name='Coursework grade-sheet', default='',
                                   help_text='PDF only', validators=[pdf_validator])
    recommendation = models.FileField(upload_to='recommendations',
                                      verbose_name='Recommendation from the guide for accommodation', default='',
                                      help_text='PDF only', validators=[pdf_validator])


class WaitlistApplicant(ApplicantBase):
    class Meta:
        abstract = False

    waitlist_t1 = models.IntegerField(default=-1,
                                      verbose_name='Waitlist Number (Type 1)')
    # -1 = removed/not applied; -2 = prompted; 0 = occupied
    waitlist_mt = models.IntegerField(default=-1, verbose_name='Waitlist Number (Manas-Tulsi)')

    acad_verified = models.BooleanField(default=False)
    marriage_certificate_verified = models.BooleanField(default=False,
                                                        choices=((True, 'Verified'), (False, 'Not verified')),
                                                        verbose_name='Marriage Certificate')
    photograph_verified = models.BooleanField(default=False, choices=((True, 'Verified'), (False, 'Not verified')),
                                              verbose_name='Photograph')
    grade_sheet_verified = models.BooleanField(default=False, choices=((True, 'Verified'), (False, 'Not verified')),
                                               verbose_name='Grade sheet')
    recommendation_verified = models.BooleanField(default=False, choices=((True, 'Verified'), (False, 'Not verified')),
                                                  verbose_name='Recommendations from the guide for accommodation')

    acad_feedback = models.TextField(default='', help_text='In case any information provided is invalid.',
                                     null=True, blank=True, verbose_name='Feedback')
    hcu_feedback = models.TextField(default='', help_text='In case any information provided is invalid.',
                                    null=True, blank=True, verbose_name='Feedback')

    hostel_radio_choices = ((0, 'None'), (1, 'Type 1'), (2, 'Manas'), (3, 'Tulsi'))

    offer = models.IntegerField(default=0, choices=hostel_radio_choices, verbose_name='Shortlisting for')
    occupying = models.IntegerField(default=0, choices=hostel_radio_choices)
    vacated = models.IntegerField(default=0, choices=hostel_radio_choices)

    offered_on = models.DateField(null=True)
    occupied_on = models.DateField(null=True)
    vacated_on = models.DateField(null=True)

    form_updated = models.BooleanField(default=True)

    def all_verified(self):
        return self.acad_verified and self.marriage_certificate_verified and self.photograph_verified and self.grade_sheet_verified and self.recommendation_verified

    def refresh_waitlist_mock(self):
        if not self.all_verified():
            return -1, -1

        if self.pk is None:
            ls = reversed(WaitlistApplicant.objects.all())
        else:
            ls = reversed(WaitlistApplicant.objects.filter(id__lt=self.id))

        waitlist_t1 = 1
        waitlist_mt = 1

        t1_set = False
        t2_set = False
        for prev_instance in ls:
            if prev_instance.waitlist_t1 > 0 and not t1_set:
                waitlist_t1 = prev_instance.waitlist_t1 + 1
                t1_set = True
            if prev_instance.waitlist_mt > 0 and not t2_set:
                waitlist_mt = prev_instance.waitlist_mt + 1
                t2_set = True
            if t1_set and t2_set:
                break

        return waitlist_t1, waitlist_mt

    def refresh_waitlist(self):
        self.waitlist_t1, self.waitlist_mt = self.refresh_waitlist_mock()
        self.save()

    def get_status_id(self):
        if not self.acad_verified:
            return 0

        if self.occupying > 0:
            if self.occupying == 1:
                if self.waitlist_mt == -2:
                    return 6
                else:
                    return 5
            return 1

        if self.offer > 0:
            return 2

        if self.vacated == 1:
            return 7
        elif self.vacated > 1:
            return 8

        if self.marriage_certificate_verified and self.photograph_verified and self.grade_sheet_verified and \
                self.recommendation_verified:
            return 3
        else:
            return 4

    def get_status_string(self):
        offer = self.hostel_radio_choices[self.offer][1]
        occupying = self.hostel_radio_choices[self.occupying][1]
        vacated = self.hostel_radio_choices[self.vacated][1]

        return ['Academic verification pending',
                f'Occupying {occupying}',
                f'Shortlisted for {offer}',
                'Documents verified', 'HCU verification pending',
                f'Occupying {occupying}' + (f' and shortlisted for {offer}' if self.offer > 0 else ''),
                'Occupying Type 1, seat locked',
                f'Vacated {vacated}' + (f' and shortlisted for {offer}' if self.offer > 0 else ''),
                f'Vacated {vacated}'][self.get_status_id()]

    def get_offer_expiry_date(self):
        try:
            return self.offered_on + datetime.timedelta(days=7)
        except TypeError:
            return None

    def refresh_waitlist_ahead(self, offset_t1, offset_mt):

        db_lock.obtain_lock()

        try:
            waitlist_ahead = WaitlistApplicant.objects.filter(id__gt=self.id)
            waitlist_t1, waitlist_mt = self.refresh_waitlist_mock()
            waitlist_t1 += offset_t1
            waitlist_mt += offset_mt
            for row in waitlist_ahead:
                if row.waitlist_t1 > 0:
                    waitlist_t1 += 1
                    row.waitlist_t1 = waitlist_t1
                if row.waitlist_mt > 0:
                    waitlist_mt += 1
                    row.waitlist_mt = waitlist_mt
                row.save()
        except:
            pass

        db_lock.release_lock()

    def decline_offer(self):
        if self.offer == 1:
            self.waitlist_t1 = -2
            self.offer = 0
            self.save()
            self.refresh_waitlist_ahead(-1, 0)
        elif self.offer > 1:
            self.offer = 0
            if self.occupying != 1:
                self.waitlist_mt = self.waitlist_t1 = -2
                self.refresh_waitlist_ahead(-1, -1)
                self.delete()
                self.id = None
            else:
                self.waitlist_mt = -2
                self.refresh_waitlist_ahead(0, -1)
            self.save()
