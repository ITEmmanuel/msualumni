from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator, URLValidator
from datetime import datetime
from django.utils.translation import gettext_lazy as _
import json
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

User = get_user_model()


class AuditLog(models.Model):
    """Model to track all changes to Alumni records for data protection compliance."""
    ACTION_TYPES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('view', 'Viewed')
    ]
    
    alumni = models.ForeignKey('Alumni', on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    changed_fields = models.TextField(blank=True, help_text='JSON of changed fields and their values')
    reason = models.TextField(blank=True, help_text='Reason for the change')

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')

    def __str__(self):
        return f"{self.get_action_display()} - {self.alumni} - {self.timestamp}"


class IAROContent(models.Model):
    """Model to store IARO section content for the home page."""
    title = models.CharField(max_length=200, default='International & Alumni Relations Office')
    description = models.TextField(help_text='Main description for the IARO section')
    vision = models.TextField(help_text='Vision statement')
    is_active = models.BooleanField(default=True, help_text='Show this content on the home page')
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('IARO Content')
        verbose_name_plural = _('IARO Content')

    def __str__(self):
        return f"IARO Content (Updated: {self.last_updated.strftime('%Y-%m-%d')})"


class IAROObjective(models.Model):
    """Model to store IARO objectives."""
    iaro = models.ForeignKey(IAROContent, on_delete=models.CASCADE, related_name='objectives')
    title = models.CharField(max_length=100, help_text='Short title for the objective')
    description = models.TextField(help_text='Detailed description of the objective')
    order = models.PositiveIntegerField(default=0, help_text='Order in which objectives should appear')

    class Meta:
        ordering = ['order']
        verbose_name = _('IARO Objective')
        verbose_name_plural = _('IARO Objectives')

    def __str__(self):
        return f"{self.title} - {self.iaro}"

class Alumni(models.Model):
    # Personal Information
    SALUTATION_CHOICES = [
        ('Mr', 'Mr.'),
        ('Ms', 'Ms.'),
        ('Mrs', 'Mrs.'),
        ('Dr', 'Dr.'),
        ('Prof', 'Prof.'),
    ]
    salutation = models.CharField(max_length=10, choices=SALUTATION_CHOICES, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    date_of_birth = models.DateField(null=True, blank=True)
    maiden_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Maiden Name')
    national_id = models.CharField(max_length=50, help_text="National ID/Passport Number")
    
    # Contact Information
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Zimbabwe')
    
    # Academic Information
    reg_number = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Leave blank if you don't remember"
    )
    programme_studied = models.CharField(max_length=200)
    graduation_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(2000),
            MaxValueValidator(datetime.now().year + 2)
        ]
    )
    DEGREE_LEVELS = [
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('undergraduate', 'Undergraduate Degree'),
        ('masters', 'Masters Degree'),
        ('phd', 'PhD/Doctorate'),
        ('postdoc', 'Postdoctoral'),
        ('other', 'Other')
    ]
    degree_level = models.CharField(
        max_length=20,
        choices=DEGREE_LEVELS,
        blank=True,
        help_text='Highest degree level obtained at MSU'
    )
    other_programs = models.TextField(blank=True, help_text='List other programs obtained from MSU (optional)')
    
    # System Fields
    registration_date = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    data_protection_consent = models.BooleanField(
        default=False,
        help_text="I consent to the processing of my personal data in accordance with the Data Protection Act of Zimbabwe"
    )
    # Employment Information
    EMPLOYMENT_STATUS_CHOICES = [
        ('formally_employed', 'Formally Employed'),
        ('self_employed', 'Self Employed'),
        ('unemployed', 'Not yet Employed'),
        ('other', 'Other')
    ]
    employment_status = models.CharField(max_length=50, choices=EMPLOYMENT_STATUS_CHOICES, blank=True)
    current_employer = models.CharField(max_length=200, blank=True, verbose_name='Name of Organisation')
    job_title = models.CharField(max_length=200, blank=True, verbose_name='Designation')
    industry = models.CharField(max_length=200, blank=True)
    employment_other_details = models.TextField(blank=True, verbose_name='Please specify')
    
    # Areas of Interest
    interest_networking = models.BooleanField(default=False, 
                                          verbose_name='Networking/Peer Engagement')
    interest_academic = models.BooleanField(default=False, 
                                         verbose_name='Academic & Mentorship')
    interest_career = models.BooleanField(default=False, 
                                       verbose_name='Career & Professional Development')
    interest_giving_back = models.BooleanField(default=False, 
                                           verbose_name='Giving Back')
    interest_stay_informed = models.BooleanField(default=False, 
                                             verbose_name='Stay Informed')
    interest_other = models.BooleanField(default=False, verbose_name='Other Interest')
    interest_other_details = models.TextField(blank=True, verbose_name='Please specify other interest')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='alumni_profile_pictures/', blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Alumni"
    
    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.reg_number})"
        return self.reg_number


class Newsletter(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(default=timezone.now)
    attachment = models.FileField(upload_to='newsletter_attachments/', blank=True, null=True)
    
    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    is_virtual = models.BooleanField(default=False)
    virtual_link = models.URLField(blank=True, null=True)
    registration_required = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    
    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    alumni = models.ForeignKey(Alumni, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(default=timezone.now)
    attended = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('event', 'alumni')
    
    def __str__(self):
        return f"{self.alumni} - {self.event}"




class AlumniStory(models.Model):
    """Inspirational stories from alumni."""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to='alumni_stories_photos/', blank=True, null=True)
    published_date = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-published_date']
        verbose_name = _('Alumni Story')
        verbose_name_plural = _('Alumni Stories')

    def __str__(self):
        return self.title


class SocialLink(models.Model):
    """External social / messaging communities for alumni."""
    PLATFORM_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('linkedin', 'LinkedIn'),
        ('x', 'X / Twitter'),
        ('newsletter', 'Newsletter'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField()
    icon = models.CharField(max_length=100, blank=True, help_text='Path to icon in static or external URL')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = _('Social Link')
        verbose_name_plural = _('Social Links')

    def __str__(self):
        return self.name


class Donation(models.Model):
    """Financial contributions from alumni or friends."""
    alumni = models.ForeignKey('Alumni', on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Donation')
        verbose_name_plural = _('Donations')

    def __str__(self):
        return f"{self.name} - {self.amount} {self.currency}"

def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Signal handlers moved to signals.py to fix AnonymousUser issues
# @receiver(pre_save, sender=Alumni)
# def alumni_pre_save(sender, instance, **kwargs):
#     """Track changes before saving an Alumni record."""
#     if instance.pk:
#         try:
#             old_instance = Alumni.objects.get(pk=instance.pk)
#             changes = {}
#             for field in instance._meta.fields:
#                 field_name = field.name
#                 if field_name in ['id', 'registration_date']:  # Skip these fields
#                     continue
#                 old_value = getattr(old_instance, field_name, None)
#                 new_value = getattr(instance, field_name, None)
#                 if old_value != new_value:
#                     changes[field_name] = {
#                         'old': str(old_value),
#                         'new': str(new_value)
#                     }
#             if changes:
#                 instance._change = changes
#         except Alumni.DoesNotExist:
#             pass


# @receiver(post_save, sender=Alumni)
# def alumni_post_save(sender, instance, created, **kwargs):
#     """Log when an Alumni record is created or updated."""
#     action = 'create' if created else 'update'
#     
#     # Get the request object if available
#     request = None
#     try:
#         from django.utils.deprecation import MiddlewareMixin
#         from django.http import HttpRequest
#         if hasattr(instance, '_request'):
#             request = instance._request
#     except:
#         pass
#     
#     # Create audit log entry
#     AuditLog.objects.create(
#         alumni=instance,
#         user=request.user if request and hasattr(request, 'user') else None,
#         action=action,
#         ip_address=get_client_ip(request) if request else None,
#         user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
#         changed_fields=json.dumps(getattr(instance, '_change', {}), default=str),
#         reason=getattr(instance, '_change_reason', '')
#     )


# Signal handlers moved to signals.py to fix AnonymousUser issues
# @receiver(post_delete, sender=Alumni)
# def alumni_post_delete(sender, instance, **kwargs):
#     """Log when an Alumni record is deleted."""
#     # Get the request object if available
#     request = None
#     try:
#         if hasattr(instance, '_request'):
#             request = instance._request
#     except:
#         pass
#     
#     # Create audit log entry
#     AuditLog.objects.create(
#         alumni=instance,
#         user=request.user if request and hasattr(request, 'user') else None,
#         action='delete',
#         ip_address=get_client_ip(request) if request else None,
#         user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
#         reason=getattr(instance, '_delete_reason', '')
#     )