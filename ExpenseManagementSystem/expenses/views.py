from django.shortcuts import render, redirect, get_object_or_404
from .utils import generate_expense_report
from .forms import YourReportForm, ExpenseForm, UserProfileForm
from .models import UserProfile, Expense, Report
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.contrib import messages
import csv
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, functions as Func
from django.core.serializers.json import DjangoJSONEncoder
import json, calendar
from collections import defaultdict

def home(request):
    return render(request, 'expenses/home.html')

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect(reverse('expense_confirmation', kwargs={'expense_id': expense.id}))
    else:
        form = ExpenseForm()
    return render(request, 'expenses/add_expense.html', {'form': form})

@login_required
def view_reports(request):
    user_reports = Report.objects.filter(user=request.user).order_by('-created_date')
    context = {'reports': user_reports}
    return render(request, 'expenses/view_reports.html', context)

@login_required
def generate_report_view(request):
    form = YourReportForm(request.POST or None)
    form_submitted = False

    if request.method == 'POST' and form.is_valid():
        form_submitted = True
        report = create_and_save_report_instance(form, request.user)
        generate_and_save_report_data(report, form, request.user)

        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        category_queryset = form.cleaned_data.get('category')

        report_data = generate_expense_report(request.user, start_date, end_date, category_queryset)
        expenses = report_data['expenses']
        total_expense = sum(expense.amount for expense in expenses)

        if category_queryset:
            donut_chart_data = generate_donut_chart_data(expenses)

            # Aggregate and format data for the line chart
            expenses_by_month = aggregate_expenses_by_month(expenses, start_date, end_date)
            line_chart_data = format_data_for_chart(expenses_by_month, start_date, end_date)

        context = {
            'form': form,
            'form_submitted': form_submitted,
            'expenses': expenses,
            'total_expense': total_expense,
            'start_date': start_date,
            'end_date': end_date,
            'donut_chart_data': donut_chart_data,
            'line_chart_data': json.dumps(line_chart_data, cls=DjangoJSONEncoder) if line_chart_data else None
        }

        messages.success(request, 'Report generated successfully.')
        return render(request, 'expenses/report_form.html', context)

    else:
        context = {'form': form}
        return render(request, 'expenses/report_form.html', context)

    
def format_data_for_chart(expenses_aggregated, start_date, end_date):
    # Generate month labels
    labels = []
    for year in range(start_date.year, end_date.year + 1):
        start_month = start_date.month if year == start_date.year else 1
        end_month = end_date.month if year == end_date.year else 12
        for month in range(start_month, end_month + 1):
            labels.append(f"{calendar.month_name[month]} {year}")

    # Initialize a dictionary to hold expense data for each category
    category_data = defaultdict(lambda: [0] * len(labels))

    # Populate the category data
    for expense in expenses_aggregated:
        # Calculate the index in labels array
        month_label = f"{calendar.month_name[expense['month']]} {expense['year']}"
        if month_label in labels:
            index = labels.index(month_label)
            category_data[expense['category__name']][index] = expense['total']

    # Create datasets for Chart.js
    datasets = []
    for category, data in category_data.items():
        dataset = {
            'label': category,
            'data': data,
            'borderColor': get_random_color(),  # Define a function to get a random color
            'fill': False
        }
        datasets.append(dataset)

    return {'labels': labels, 'datasets': datasets}

def get_random_color():
    # Function to generate a random color
    import random
    r = lambda: random.randint(0,255)
    return f'rgba({r()}, {r()}, {r()}, 1)'
    
def aggregate_expenses_by_month(expenses, start_date, end_date):
    expenses = expenses.annotate(
        month=Func.ExtractMonth('date'),
        year=Func.ExtractYear('date')
    ).values('month', 'year', 'category__name').annotate(total=Sum('amount')).order_by('year', 'month')

    return expenses
    
def generate_donut_chart_data(expenses):
    category_totals = expenses.values('category__name').annotate(total=Sum('amount'))
    labels = [category['category__name'] for category in category_totals]
    data = [category['total'] for category in category_totals]

    donut_chart_data = {
        'labels': labels,
        'datasets': [{'data': data, 'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56']}]
    }
    return json.dumps(donut_chart_data, cls=DjangoJSONEncoder)

def generate_expense_report(user, start_date, end_date, category_queryset):
    if category_queryset:
        expenses = Expense.objects.filter(user=user, date__range=[start_date, end_date], category__in=category_queryset)
    else:
        expenses = Expense.objects.filter(user=user, date__range=[start_date, end_date])
    return {'expenses': expenses}

def create_and_save_report_instance(form, user):
    start_date = form.cleaned_data['start_date']
    end_date = form.cleaned_data['end_date']
    report = Report(user=user, title=f"Report from {start_date} to {end_date}")
    report.save()
    return report

def generate_and_save_report_data(report, form, user):
    start_date = form.cleaned_data['start_date']
    end_date = form.cleaned_data['end_date']
    category_queryset = form.cleaned_data.get('category')

    report_data = generate_expense_report(user, start_date, end_date, category_queryset)

    csv_file_name = f'report_{user.id}_{start_date}_to_{end_date}.csv'
    csv_file_path = os.path.join(settings.MEDIA_ROOT, 'reports', csv_file_name)

    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        headers = ['Title', 'Amount', 'Date', 'Category']
        writer.writerow(headers)

        for expense in report_data['expenses']:
            row = [expense.title, expense.amount, expense.date, expense.category.name]
            writer.writerow(row)

    with open(csv_file_path, 'rb') as f:
        report.report_file.save(csv_file_name, ContentFile(f.read()))

def generate_donut_chart(request):
    if request.method == 'POST':
        form = YourReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            selected_categories = form.cleaned_data['category']

            # Filter expenses based on date range and selected categories
            expenses = Expense.objects.filter(
                date__range=(start_date, end_date),
                category__in=selected_categories
            )

            # Calculate total expenses for each category
            category_totals = expenses.values('category__name').annotate(total=Sum('amount'))

            # Prepare data for the donut chart
            labels = [category['category__name'] for category in category_totals]
            data = [category['total'] for category in category_totals]

            return render(request, 'your_template.html', {'labels': labels, 'data': data})

    else:
        form = YourReportForm()

    return render(request, 'your_template.html', {'form': form})        

def edit_profile(request):
    user = request.user
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
        
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile_view')  # Redirect to the profile page
    else:
        form = UserProfileForm(instance=request.user.userprofile)
        
    return render(request, 'expenses/edit_profile.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page after successful registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def expense_confirmation(request, expense_id):
    expense = Expense.objects.get(id=expense_id)
    categories = expense.category.all()  # Retrieve all categories associated with the expense
    return render(request, 'expenses/expense_confirmation.html', {
        'expense': expense,
        'categories': categories,  # Add categories to the context
    })

def profile_view(request):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None
    
    return render(request, 'expenses/profile_view.html', {'user_profile': user_profile})

def report_detail(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    return render(request, 'expenses/report_detail.html', {'report': report})


