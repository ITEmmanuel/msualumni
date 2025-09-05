"""Seed sample newsletters published in 2024.

Usage:
    python manage.py seed_2024_newsletters
"""
from datetime import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand

from alumni.models import Newsletter


class Command(BaseCommand):
    help = "Seed the database with a few example newsletters from 2024."

    def handle(self, *args, **options):
        newsletters = [
            {
                "title": "MSU IARO Quarterly Update – Q1 2024",
                "content": (
                    "Highlights from the first quarter: new partnerships in Asia, successful alumni networking "
                    "events in Harare and progress on the student exchange programme launching later this year."
                ),
                "published_date": timezone.make_aware(datetime(2024, 3, 15, 10, 0)),
            },
            {
                "title": "International Week Recap 2024",
                "content": (
                    "A look back at International Week 2024, featuring cultural exhibitions, guest lectures and the "
                    "signing of three MoUs with universities in Europe and North America."
                ),
                "published_date": timezone.make_aware(datetime(2024, 6, 5, 9, 30)),
            },
            {
                "title": "Alumni Spotlight – September 2024 Edition",
                "content": (
                    "Meet inspiring MSU graduates making an impact across the globe. This edition features alumni in "
                    "biotech, public policy and social entrepreneurship."
                ),
                "published_date": timezone.make_aware(datetime(2024, 9, 20, 14, 0)),
            },
        ]

        created = 0
        for item in newsletters:
            if Newsletter.objects.filter(title=item["title"]).exists():
                self.stdout.write(f"Newsletter '{item['title']}' already exists. Skipping.")
                continue
            Newsletter.objects.create(**item)
            created += 1
            self.stdout.write(self.style.SUCCESS(f"Created '{item['title']}'."))

        if created:
            self.stdout.write(self.style.SUCCESS(f"Successfully created {created} newsletter(s)."))
        else:
            self.stdout.write(self.style.WARNING("No new newsletters created."))
