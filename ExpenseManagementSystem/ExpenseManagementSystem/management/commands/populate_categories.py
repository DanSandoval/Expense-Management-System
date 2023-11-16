from django.core.management.base import BaseCommand
from .models import Category

class Command(BaseCommand):
    help = 'Populates the database with default category data'

    def handle(self, *args, **kwargs):
        categories = ['Food', 'Travel', 'Utilities', 'Entertainment', 'Healthcare']
        for category_name in categories:
            Category.objects.get_or_create(name=category_name)
        self.stdout.write(self.style.SUCCESS('Successfully populated categories'))
