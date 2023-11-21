from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from expenses.models import RecurringExpense, Expense

class Command(BaseCommand):
    help = 'Check and handle missed recurring expenses'

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        missed_recurrings = RecurringExpense.objects.filter(next_due_date__lt=today, is_active=True)

        for recurring in missed_recurrings:
            # Create a new expense instance
            Expense.objects.create(
                title=recurring.expense.title,
                amount=recurring.expense.amount,
                date=recurring.next_due_date,
                category=recurring.expense.category,
                #user=recurring.expense.user,  # Uncomment if you use user field
            )
            
            # Update next_due_date based on frequency
            if recurring.frequency == 'daily':
                recurring.next_due_date += timedelta(days=1)
            elif recurring.frequency == 'weekly':
                recurring.next_due_date += timedelta(weeks=1)
            elif recurring.frequency == 'monthly':
                # This is a simplification. You may need more complex logic for monthly recurrence.
                recurring.next_due_date += timedelta(days=30)

            recurring.save()

        self.stdout.write(self.style.SUCCESS('Successfully processed missed recurring expenses'))
