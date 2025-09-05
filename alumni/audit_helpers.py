"""
Helper functions for alumni audit logging that avoid AnonymousUser errors.
"""
import json
from django.db import connection
from django.utils import timezone

def create_alumni_audit_log(alumni, action, ip_address=None, user_agent=None, 
                          changed_fields=None, reason=None):
    """
    Safely create an audit log for alumni without user assignment issues.
    
    This uses raw SQL to completely bypass Django ORM, middleware and signals,
    eliminating any possibility of AnonymousUser errors.
    
    Args:
        alumni: The Alumni instance to log activity for
        action: One of the defined action types ('create', 'update', etc.)
        ip_address: Optional IP address string
        user_agent: Optional user agent string
        changed_fields: Optional dict of changed fields (will be JSON serialized)
        reason: Optional reason string
        
    Returns:
        True if log creation was successful, False otherwise
    """
    try:
        # Only attempt to log if alumni has a valid PK
        if not alumni or not alumni.pk:
            print("Cannot log - alumni object has no primary key")
            return False
            
        # Convert changed_fields to JSON string
        if changed_fields:
            changed_fields_json = json.dumps(changed_fields, default=str)
        else:
            changed_fields_json = ""

        # Get current timestamp
        timestamp = timezone.now()
        
        # Prepare parameters, ensuring None values are properly handled
        params = [
            alumni.pk,                            # alumni_id
            None,                                 # user_id (explicitly NULL)
            action,                               # action
            timestamp.isoformat(),                # timestamp
            ip_address or None,                   # ip_address
            user_agent or "",                     # user_agent
            changed_fields_json,                  # changed_fields
            reason or ""                          # reason
        ]
        
        # Execute direct SQL insert to bypass all Django ORM mechanisms
        # Django default table name convention: <app_name>_<model_name_lowercase>
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO alumni_auditlog 
                    (alumni_id, user_id, action, timestamp, 
                     ip_address, user_agent, changed_fields, reason)
                VALUES 
                    (%s, %s, %s, %s, %s, %s, %s, %s)
            """, params)
            
        return True
    except Exception as e:
        print(f"Failed to create audit log via SQL: {e}")
        return False
