from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from .models import Alumni, Donation
import re

class AlumniRegistrationForm(forms.ModelForm):
    data_protection_consent = forms.BooleanField(
        required=True,
        label='Data Protection Consent',
        help_text='I consent to the processing of my personal data in accordance with the Data Protection Act of Zimbabwe',
        error_messages={
            'required': 'You must consent to the processing of your data to register.'
        }
    )
    
    class Meta:
        model = Alumni
        fields = [
            # Personal Information
            'salutation', 'first_name', 'last_name', 'gender', 'maiden_name', 'date_of_birth', 'national_id',
            # Contact Information
            'email', 'mobile_number', 'city', 'country',
            # Academic Information
            'reg_number', 'programme_studied', 'graduation_year', 'degree_level',
            'other_programs',
            # Employment Information
            'employment_status', 'current_employer', 'job_title', 'industry', 'date_of_engagement', 'employment_other_details',
            # Areas of Interest
            'interest_networking', 'interest_academic', 'interest_career',
            'interest_giving_back', 'interest_stay_informed', 'interest_other', 'interest_other_details',
            # Data Protection
            'data_protection_consent',
        ]
        widgets = {
            'salutation': forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'w-full p-2 border border-gray-300 rounded-md',
                    'max': timezone.now().date().isoformat()
                }
            ),
            'gender': forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'graduation_year': forms.NumberInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
                'min': 2000,
                'max': timezone.now().year + 2
            }),
            # Employment widgets
            'employment_status': forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'current_employer': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md', 
                                                 'placeholder': 'Name of Organisation'}),
            'job_title': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md', 
                                          'placeholder': 'Designation'}),
            
            # Interest widgets - using checkboxes
            'date_of_engagement': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-2 border border-gray-300 rounded-md'
            }),
            'interest_networking': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-msu-blue rounded border-gray-300 focus:ring-msu-blue',
            }),
            'interest_academic': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-msu-blue rounded border-gray-300 focus:ring-msu-blue',
            }),
            'interest_career': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-msu-blue rounded border-gray-300 focus:ring-msu-blue',
            }),
            'interest_giving_back': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-msu-blue rounded border-gray-300 focus:ring-msu-blue',
            }),
            'interest_stay_informed': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-msu-blue rounded border-gray-300 focus:ring-msu-blue',
            }),
            'interest_other': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-msu-blue rounded border-gray-300 focus:ring-msu-blue',
            }),
            'interest_other_details': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md', 'rows': 3, 'placeholder': 'Please specify your other interests'
            }),
            'other_programs': forms.Textarea(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md', 'rows': 3, 'placeholder': 'e.g., Postgrad Diploma in ...; Short Course in ...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['salutation'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['gender'].required = True
        self.fields['national_id'].required = True
        self.fields['email'].required = True
        self.fields['mobile_number'].required = True
        self.fields['programme_studied'].required = True
        self.fields['graduation_year'].required = True
        
        # Add help text and placeholders
        self.fields['reg_number'].help_text = 'Leave blank if you don\'t remember'
        self.fields['reg_number'].required = False
        self.fields['national_id'].help_text = 'National ID or Passport Number'
        self.fields['mobile_number'].validators = [
            RegexValidator(
                regex=r'^\+?[0-9]{9,15}$',
                message='Enter a valid phone number (e.g., +263771234567 or 0771234567)'
            )
        ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        import re
        email_regex = r'^[^@]+@[^@]+\.[^@]+$'
        if not re.match(email_regex, email):
            raise forms.ValidationError('Please enter a valid email address.')
        if Alumni.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if Alumni.objects.filter(national_id=national_id).exists():
            raise forms.ValidationError('This ID number is already registered.')
        return national_id

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = timezone.now().date()
            age = (today - dob).days / 365.2425
            if age < 18:
                raise ValidationError('You must be at least 18 years old to register.')
        return dob

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[a-zA-Z\s]+$', first_name):
            raise forms.ValidationError('First name must contain only letters and spaces.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[a-zA-Z\s]+$', last_name):
            raise forms.ValidationError('Last name must contain only letters and spaces.')
        return last_name


class AlumniEmploymentUpdateForm(forms.ModelForm):
    """Form for alumni who only want to update their employment information."""
    class Meta:
        model = Alumni
        fields = ['employment_status', 'current_employer', 'job_title', 'industry']
        widgets = {
            'employment_status': forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'current_employer': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'job_title': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'industry': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
        }


class AlumniFullUpdateForm(AlumniRegistrationForm):
    """Form for alumni who want to update their full profile via the tab interface."""
    national_id = forms.CharField(
        max_length=50,
        label='National ID / Passport',
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common = 'w-full p-2 border border-gray-300 rounded-md'
        checkbox = 'h-5 w-5 text-msu-blue rounded border-gray-300 focus:ring-msu-blue'
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', checkbox)
            else:
                field.widget.attrs.setdefault('class', common)

    class Meta(AlumniRegistrationForm.Meta):
        pass

    def clean_email(self):
        return self.cleaned_data.get('email')  # skip duplicate validation

    def clean_national_id(self):
        return self.cleaned_data.get('national_id')


class DonationForm(forms.ModelForm):
    """Form for alumni or friends to make a donation pledge."""
    class Meta:
        model = Donation
        fields = ['name', 'email', 'amount', 'currency', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'message': forms.Textarea(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md', 'rows': 3}),
        }