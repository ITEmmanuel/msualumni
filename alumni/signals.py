"""
Signal handlers for the Alumni app with fixed user assignment to prevent AnonymousUser errors.
"""
import json
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Alumni, AuditLog

def get_client_ip(request):
    """Get client IP address from request object."""
    if not request:
        return None
        
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(pre_save, sender=Alumni)
def alumni_pre_save(sender, instance, **kwargs):
    """Track changes before saving an Alumni record."""
    if instance.pk:
        try:
            old_instance = Alumni.objects.get(pk=instance.pk)
            changes = {}
            for field in instance._meta.fields:
                field_name = field.name
                if field_name in ['id', 'registration_date']:  # Skip these fields
                    continue
                old_value = getattr(old_instance, field_name, None)
                new_value = getattr(instance, field_name, None)
                if old_value != new_value:
                    changes[field_name] = {
                        'old': str(old_value),
                        'new': str(new_value)
                    }
            if changes:
                instance._change = changes
        except Alumni.DoesNotExist:
            pass

@receiver(post_save, sender=Alumni)
def alumni_post_save(sender, instance, created, **kwargs):
    """Log when an Alumni record is created or updated."""
    action = 'create' if created else 'update'
    
    # Get the request object if available
    request = None
    try:
        if hasattr(instance, '_request'):
            request = instance._request
    except:
        pass
    
    # Create audit log entry
    try:
        AuditLog.objects.create(
            alumni=instance,
            user=None,  # Always use None to avoid AnonymousUser errors
            action=action,
            ip_address=get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
            changed_fields=json.dumps(getattr(instance, '_change', {}), default=str),
            reason=getattr(instance, '_change_reason', '')
        )
    except Exception as e:
        print(f"Failed to create audit log in signal handler: {e}")

@receiver(post_delete, sender=Alumni)
def alumni_post_delete(sender, instance, **kwargs):
    """Log when an Alumni record is deleted."""
    # Get the request object if available
    request = None
    try:
        if hasattr(instance, '_request'):
            request = instance._request
    except:
        pass
    
    # Create audit log entry
    try:
        AuditLog.objects.create(
            alumni=instance,
            user=None,  # Always use None to avoid AnonymousUser errors
            action='delete',
            ip_address=get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
            reason=getattr(instance, '_delete_reason', '')
        )
    except Exception as e:
        print(f"Failed to create audit log in signal handler: {e}")
