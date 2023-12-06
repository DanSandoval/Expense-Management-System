from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from expenses.models import Expense, Category, RecurringExpense
from faker import Faker
import random
import datetime

class Command(BaseCommand):
    help = 'Populates the database with random expense entries'

    def add_arguments(self, parser):
        parser.add_argument('num_entries', type=int, help='Indicates the number of expense entries to create')

    def handle(self, *args, **kwargs):
        num_entries = kwargs['num_entries']
        fake = Faker()

        users = list(User.objects.all())
        categories = list(Category.objects.all())

        for _ in range(num_entries):
            title = fake.sentence(nb_words=4)
            amount = round(random.uniform(10.00, 500.00), 2)
            date = fake.date_between(start_date='-2y', end_date='today')
            user = random.choice(users)

            expense = Expense.objects.create(title=title, amount=amount, date=date, user=user)
            expense_categories = random.sample(categories, random.randint(1, len(categories)))
            expense.category.set(expense_categories)

        self.stdout.write(self.style.SUCCESS(f'Successfully populated {num_entries} expense entries'))
