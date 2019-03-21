from django import forms
from django.forms import inlineformset_factory
from django.core.validators import RegexValidator
from .models import Candidate, JobPosting, Attendance
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, ButtonHolder, Fieldset, HTML, Button, Row, Field


class RegisterForm(forms.Form):
    error_css_class = 'errorlist'

    candidate_first_name = forms.CharField(label='Your First Name', max_length=200)
    candidate_last_name = forms.CharField(label='Your Last Name', max_length=200)
    candidate_email = forms.EmailField(label='Your Email', max_length=200)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{8,15}$',
                                 message='Phone number must be entered in the format: ''+999999999''. Up to 15 digits allowed.')
    candidate_phone = forms.CharField(validators=[phone_regex], label='Your Phone Number', max_length=15, required=False)
    JobPostingFormSet = inlineformset_factory(JobPosting, Attendance, fields=('selected_job_posting',))
    candidate_job_postings = forms.MultipleChoiceField(label='Choose Job', initial='', widget=forms.CheckboxSelectMultiple(), required=True)

    class Meta:
        model = Candidate

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(form=self)
        self.helper.form_id = 'id-registrationForm'
        self.helper.form_method = 'post'
        self.helper.form_action = 'detail'
        self.helper.layout = Layout(
            Div(
                Div('candidate_first_name'),
                Div('candidate_last_name'),
                Div('candidate_email'),
                Div('candidate_phone'),
                Div('candidate_job_postings'),
                css_class='row'
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='btn-default')
            )
        )
