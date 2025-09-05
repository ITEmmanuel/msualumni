from django.apps import AppConfig


class AlumniConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alumni'
    
    def ready(self):
        """Import signals when the app is ready."""
        import alumni.signals  # Import the fixed signal handlers
