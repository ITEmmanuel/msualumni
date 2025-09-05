"""Django management command to seed International & Alumni Relations Office content.

Usage:
    python manage.py seed_iaro_content
"""
from django.core.management.base import BaseCommand

from alumni.models import IAROContent, IAROObjective


class Command(BaseCommand):
    help = "Seed the database with IARO content and key objectives."

    def handle(self, *args, **options):
        if IAROContent.objects.exists():
            self.stdout.write(self.style.WARNING("IAROContent already exists. Skipping creation."))
            return

        description = (
            "The International & Alumni Relations Office (IARO) champions Midlands State University's global "
            "presence by cultivating strategic partnerships, supporting international students and staff, and "
            "connecting our vibrant alumni community worldwide. We facilitate collaborations, mobility opportunities "
            "and networking initiatives while promoting an inclusive, diverse campus culture."
        )

        vision = "To be a leading hub for internationalisation and alumni engagement in the region and beyond."

        iaro = IAROContent.objects.create(description=description, vision=vision, is_active=True)

        objectives = [
            ("Internationalisation", "Attract international students and staff, foster collaborations and expand MSU's global outreach."),
            ("Student mobility", "Coordinate exchanges, study-abroad and internship programmes to give students invaluable global exposure."),
            ("Alumni engagement", "Strengthen bonds with alumni worldwide through networking, events and fundraising initiatives."),
        ]

        for order, (title, obj_desc) in enumerate(objectives, start=1):
            IAROObjective.objects.create(iaro=iaro, title=title, description=obj_desc, order=order)

        self.stdout.write(self.style.SUCCESS("Successfully seeded IARO content and objectives."))
