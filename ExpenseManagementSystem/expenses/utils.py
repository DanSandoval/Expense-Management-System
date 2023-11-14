from django.db.models import Sum
from .models import Expense

def generate_expense_report(user, start_date, end_date, category=None):
    queryset = Expense.objects.filter(user=user, date__range=[start_date, end_date])
    if category:
        queryset = queryset.filter(category=category)
    total_expense = queryset.aggregate(total_amount=Sum('amount'))
    return total_expense['total_amount']
