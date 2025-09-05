from django import forms
from alumni.models import Newsletter, Event
from .models import Communication, BirthdayTemplate
from django.contrib.auth.forms import AuthenticationForm


class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-msu-blue focus:border-msu-blue', 'placeholder': 'Enter username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-msu-blue focus:border-msu-blue', 'placeholder': 'Enter password'}))


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['title', 'content', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'content': forms.Textarea(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md', 'rows': 10}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'is_virtual', 'virtual_link', 'registration_required', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md', 'rows': 5}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'location': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'virtual_link': forms.URLInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
        }


class CommunicationForm(forms.ModelForm):
    all_alumni = forms.BooleanField(required=False, label="Send to all alumni")
    
    class Meta:
        model = Communication
        fields = ['title', 'message', 'communication_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'message': forms.Textarea(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md', 'rows': 5}),
            'communication_type': forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
        }


class BirthdayTemplateForm(forms.ModelForm):
    class Meta:
        model = BirthdayTemplate
        fields = ['month', 'title', 'message', 'background_color', 'text_color', 'border_color', 'emoji', 'is_active']
        widgets = {
            'month': forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md', 'placeholder': 'e.g., January Birthday Celebrations'}),
            'message': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md', 
                'rows': 4,
                'placeholder': 'Happy Birthday {name}! Wishing you a wonderful {birthday_date} and an amazing year ahead!'
            }),
            'background_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'w-full h-10 border border-gray-300 rounded-md'
            }),
            'text_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'w-full h-10 border border-gray-300 rounded-md'
            }),
            'border_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'w-full h-10 border border-gray-300 rounded-md'
            }),
            'emoji': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md', 'placeholder': '🎉'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].help_text = 'Use {name} for alumni name and {birthday_date} for birthday date in your template.'
