from django import forms
from portal.models import WaitlistApplicant


class ApplicantDetailsFormAcad(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ApplicantDetailsFormAcad, self).__init__(*args, **kwargs)
        self.label_suffix = ''

    class Meta:
        model = WaitlistApplicant
        exclude = ['waitlist_t1', 'waitlist_mt', 'acad_verified',
                   'marriage_certificate_verified', 'photograph_verified', 'grade_sheet_verified',
                   'recommendation_verified', 'occupying', 'offer', 'hcu_feedback', 'occupied_on',
                   'vacated', 'vacated_on', 'offered_on', 'marriage_certificate', 'photograph',
                   'grade_sheet', 'recommendation', 'form_updated']


class HCUVerificationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HCUVerificationForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''

    class Meta:
        model = WaitlistApplicant
        fields = ['marriage_certificate_verified', 'photograph_verified', 'grade_sheet_verified',
                  'recommendation_verified', 'hcu_feedback']
        widgets = {
            'marriage_certificate_verified': forms.RadioSelect(),
            'photograph_verified': forms.RadioSelect(),
            'grade_sheet_verified': forms.RadioSelect(),
            'recommendation_verified': forms.RadioSelect()
        }


class HCUSeatOfferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HCUSeatOfferForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''

    class Meta:
        model = WaitlistApplicant
        fields = ['offer']
        widgets = {
            'offer': forms.RadioSelect()
        }


class HCUApplicantDetailsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HCUApplicantDetailsForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''

    class Meta:
        model = WaitlistApplicant
        exclude = ['acad_verified', 'marriage_certificate_verified', 'photograph_verified', 'grade_sheet_verified',
                   'recommendation_verified', 'acad_feedback', 'hcu_feedback', 'offer', 'offered_on', 'occupying',
                   'form_updated']
