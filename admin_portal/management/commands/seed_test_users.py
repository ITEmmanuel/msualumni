"""Django management command to create two test users.

Usage:
    python manage.py seed_test_users
"""

from django.contrib.auth import get_user_model
from admin_portal.models import AdminProfile
from django.core.management.base import BaseCommand

User = get_user_model()

TEST_USERS = [
    {"username": "chenai", "password": "msu123", "job_title": "Alumni Officer"},
    {"username": "emmanuel", "password": "msu123", "job_title": "Alumni Officer"},
]

class Command(BaseCommand):
    help = "Seed the database with test users (chenai & emmanuel)."

    def handle(self, *args, **options):
        created = 0
        for user_info in TEST_USERS:
            username = user_info["username"]
            password = user_info["password"]
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password)
                user.is_staff = True
                user.save()
                # Create AdminProfile
                AdminProfile.objects.create(user=user, job_title=user_info.get('job_title', 'Staff'))
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created user '{username}'."))
            else:
                self.stdout.write(f"User '{username}' already exists. Skipping.")
        if created == 0:
            self.stdout.write(self.style.WARNING("No new users were created."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Successfully created {created} user(s)."))
