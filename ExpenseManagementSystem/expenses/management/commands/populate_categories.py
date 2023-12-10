from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from expenses.models import Category  # Adjust the import based on your model

class Command(BaseCommand):
    help = 'Populate the database with predefined categories'

    def handle(self, *args, **kwargs):
        categories = ['Food', 'Travel', 'Utilities', 'Entertainment', 'Other']  # Add your categories here
        for cat_name in categories:
            Category.objects.get_or_create(name=cat_name)
     
        self.stdout.write(self.style.SUCCESS('Successfully populated categories'))