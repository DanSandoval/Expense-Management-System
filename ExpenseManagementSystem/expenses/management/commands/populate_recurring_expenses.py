from django.core.management.base import BaseCommand
from django.utils import timezone
from expenses.models import RecurringExpense, Expense
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populates due recurring expenses'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        due_recurring_expenses = RecurringExpense.objects.filter(recurring_from__lte=today)

        for recurring_expense in due_recurring_expenses:
            Expense.objects.create(
                title=recurring_expense.title,
                amount=recurring_expense.amount,
                date=today,
                category=recurring_expense.category,
                # user=recurring_expense.user
            )
            recurring_expense.next_due_date += timedelta(days=recurring_expense.frequency)
            recurring_expense.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated due recurring expenses'))
