from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from alumni.models import Alumni, Newsletter, Event

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.job_title}"


class BirthdayTemplate(models.Model):
    MONTH_CHOICES = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]
    
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES, unique=True)
    title = models.CharField(max_length=200, help_text="Template title for this month")
    message = models.TextField(help_text="Birthday message template. Use {name} for alumni name, {birthday_date} for birthday date.")
    background_color = models.CharField(max_length=7, default='#f0f9ff', help_text="Hex color code for template background")
    text_color = models.CharField(max_length=7, default='#1e40af', help_text="Hex color code for template text")
    border_color = models.CharField(max_length=7, default='#3b82f6', help_text="Hex color code for template border")
    emoji = models.CharField(max_length=10, default='🎉', help_text="Emoji to display with birthday message")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['month']
    
    def __str__(self):
        return f"{self.get_month_display()} - {self.title}"
    
    def get_formatted_message(self, alumni_name, birthday_date):
        """Format the template message with alumni data"""
        return self.message.format(
            name=alumni_name,
            birthday_date=birthday_date.strftime("%B %d")
        )


class Communication(models.Model):
    COMMUNICATION_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('announcement', 'Announcement'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPES)
    sent_date = models.DateTimeField(default=timezone.now)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Alumni, related_name='communications_received')
    
    def __str__(self):
        return f"{self.title} ({self.communication_type})"
