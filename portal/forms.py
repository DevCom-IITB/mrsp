from django import forms
from .models import WaitlistApplicant


class DateInput(forms.DateInput):
    input_type = 'date'


class ReadonlyTextInput(forms.TextInput):
    def __init__(self):
        super(ReadonlyTextInput, self).__init__(attrs={
            'disabled': 'true'
        })


class ApplicantForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ApplicantForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''

    class Meta:
        model = WaitlistApplicant
        fields = '__all__'
        exclude = ['waitlist_t1', 'waitlist_mt', 'acad_verified',
                   'marriage_certificate_verified', 'photograph_verified', 'grade_sheet_verified',
                   'recommendation_verified', 'acad_feedback', 'hcu_feedback', 'offer', 'occupying',
                   'offered_on', 'occupied_on', 'vacated', 'vacated_on', 'updated_form']
        widgets = {
            'name': ReadonlyTextInput(),
            'roll_number': ReadonlyTextInput(),
            'email': ReadonlyTextInput(),
            'fellowship': forms.RadioSelect(),
            'permanent_address': forms.Textarea(attrs={'rows': '4'}),
            'fellowship_date': DateInput(),
            'course_work_completes_on': DateInput()
        }


class EditDocsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditDocsForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''

    class Meta:
        model = WaitlistApplicant
        fields = ['marriage_certificate', 'photograph', 'grade_sheet', 'recommendation']
