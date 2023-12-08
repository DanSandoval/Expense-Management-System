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
from django.db.models import Sum

# Import other necessary modules

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
            form.save_m2m()
            return redirect(reverse('expense_confirmation', kwargs={'expense_id': expense.id}))
    else:
        form = ExpenseForm()#this loads the categories connected to a specific user
    return render(request, 'expenses/add_expense.html', {'form': form})

@login_required
def view_reports(request):
    user = request.user
    user_reports = Report.objects.filter(user=request.user).order_by('-created_date')

    # Passing the reports to the template
    context = {'reports': user_reports}
    return render(request, 'expenses/view_reports.html', context)

# @login_required
# def generate_report_view(request):
#     if request.method == 'POST':
#         form = YourReportForm(request.POST)
#         if form.is_valid():
#             # Create and save the report instance
#             report = create_and_save_report_instance(form, request.user)

#             # Generate report data and save to a CSV file
#             generate_and_save_report_data(report, form, request.user)

#             messages.success(request, 'Report generated successfully.')
#             return redirect('view_reports')
#         else:
#             messages.error(request, 'Error in generating report.')
#     else:
#         form = YourReportForm()

#     context = {'form': form}
#     return render(request, 'expenses/report_form.html', context)

# def generate_expense_report(user, start_date, end_date, categories):
#     # If categories are selected, filter expenses by those categories.
#     if categories:
#         expenses = Expense.objects.filter(
#             user=user,
#             date__range=[start_date, end_date],
#             category__in=categories
#         )
#     else:
#         # If no categories are selected, fetch all expenses for the user in the date range.
#         expenses = Expense.objects.filter(
#             user=user,
#             date__range=[start_date, end_date]
#         )
    
#     print("Number of expenses fetched:", expenses.count())  # Debugging line
#     return expenses

# def create_and_save_report_instance(form, user):
#     start_date = form.cleaned_data['start_date']
#     end_date = form.cleaned_data['end_date']
#     report = Report(user=user, title=f"Report from {start_date} to {end_date}")
#     report.save()
#     return report

# def generate_and_save_report_data(report, form, user):
#     start_date = form.cleaned_data['start_date']
#     end_date = form.cleaned_data['end_date']
#     categories = form.cleaned_data.get('category')  # This will be a queryset

#     # Generate the report data
#     report_data = generate_expense_report(user, start_date, end_date, categories)

#     # Define CSV file path
#     csv_file_name = f'report_{user.id}_{start_date}_to_{end_date}.csv'
#     csv_file_path = os.path.join(settings.MEDIA_ROOT, 'reports', csv_file_name)

#     # Ensure the directory exists
#     os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

#     # Write and attach the CSV file to the report
#     with open(csv_file_path, 'w', newline='') as csvfile, open(csv_file_path, 'rb') as readfile:
#         writer = csv.writer(csvfile)
#         headers = ['Title', 'Amount', 'Date', 'Category']
#         writer.writerow(headers)

#         for expense in report_data['expenses']:
#             print("Writing expense to CSV:", expense.title, expense.amount, expense.date, expense.category.name)
#             row = [expense.title, expense.amount, expense.date, expense.category.name]
#             writer.writerow(row)
#             #writer.writerow([expense.title, expense.amount, expense.date, expense.category.name])

#         report.report_file.save(csv_file_name, ContentFile(readfile.read()))

@login_required
def generate_report_view(request):
    form = YourReportForm(request.POST or None)
    form_submitted = False
    
    if request.method == 'POST' and form.is_valid():
        form_submitted = True
        report = create_and_save_report_instance(form, request.user)
        generate_and_save_report_data(report, form, request.user)

        # Fetch report data for display
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        categories = form.cleaned_data.get('category')
        report_data = generate_expense_report(request.user, start_date, end_date, categories)

        # Extract expenses from the returned dictionary
        expenses = report_data['expenses']
        total_expense = sum(expense.amount for expense in expenses)

		# Prepare data for the chart
        date_category_counts = {}

        for expense in expenses:
            date_str = expense.date.strftime("%Y-%m-%d")
            if date_str not in date_category_counts:
                date_category_counts[date_str] = set()
            date_category_counts[date_str].update(cat.name for cat in expense.category.all())

        bubble_data = {
            'datasets': [{
                'label': 'Expenses',
                'data': [
                    {
                        'x': expense.date.strftime("%Y-%m-%d"),
                		'y': float(expense.amount),
                		'r': len(date_category_counts[expense.date.strftime("%Y-%m-%d")]) * 5,
                        'expenseTitle': expense.title,
                        'amount': float(expense.amount),
                        'categories': ', '.join([cat.name for cat in expense.category.all()])
            		}
            		for expense in expenses
				],
                'backgroundColor': 'rgba(0, 123, 255, 0.5)',
				'hoverBackgroundColor': '(0, 123, 255, 1)',
			}]
		}

        context = {
            'form': form,
            'form_submitted': form_submitted,
            'expenses': expenses,
            'total_expense': total_expense,
            'start_date': start_date,
            'end_date': end_date,
            'bubble_data': bubble_data  # Add bubble chart data to the context
        }

        return render(request, 'expenses/report_form.html', context)
    else:
        context = {'form': form, 'form_submitted': form_submitted}
        return render(request, 'expenses/report_form.html', context)


# @login_required
# def generate_report_view(request):
#     form = YourReportForm(request.POST or None)
#     form_submitted = False
    
#     if request.method == 'POST' and form.is_valid():
#         form_submitted = True
#         report = create_and_save_report_instance(form, request.user)
#         generate_and_save_report_data(report, form, request.user)

#         # Fetch report data for display
#         start_date = form.cleaned_data['start_date']
#         end_date = form.cleaned_data['end_date']
#         categories = form.cleaned_data.get('category')
#         report_data = generate_expense_report(request.user, start_date, end_date, categories)

#         # Extract expenses from the returned dictionary
#         expenses = report_data['expenses']
#         total_expense = sum(expense.amount for expense in expenses)

#         # Prepare data for the chart
#         category_totals = expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total')

#         chart_data = {
#             'categories': [item['category__name'] for item in category_totals],
#             'totals': [float(item['total']) for item in category_totals]  # Convert to float
#         }

#         context = {
#             'form': form,
#             'form_submitted': form_submitted,
#             'expenses': expenses,
#             'total_expense': total_expense,
#             'start_date': start_date,
#             'end_date': end_date,
#             'chart_data': chart_data  # Add chart data to the context
#         }

#         messages.success(request, 'Report generated successfully.')
#         return render(request, 'expenses/report_form.html', context)

#     else:
#         context = {'form': form, 'form_submitted': form_submitted}
#         return render(request, 'expenses/report_form.html', context)
    
#     @login_required
# def generate_report_view(request):
#     form = YourReportForm(request.POST or None)
#     form_submitted = False
    
#     if request.method == 'POST' and form.is_valid():
#         form_submitted = True
#         report = create_and_save_report_instance(form, request.user)
#         generate_and_save_report_data(report, form, request.user)

#         # Fetch report data for display
#         start_date = form.cleaned_data['start_date']
#         end_date = form.cleaned_data['end_date']
#         categories = form.cleaned_data.get('category')
#         report_data = generate_expense_report(request.user, start_date, end_date, categories)

#         # Extract expenses from the returned dictionary
#         expenses = report_data['expenses']
#         total_expense = sum(expense.amount for expense in expenses)

#         context = {
#             'form': form,
#             'form_submitted': form_submitted,
#             'expenses': expenses,
#             'total_expense': total_expense,
#             'start_date': start_date,
#             'end_date': end_date
#         }

#         messages.success(request, 'Report generated successfully.')
#         # Render the same page with report data
#         return render(request, 'expenses/report_form.html', context)

    # else:
    #     # If not POST or form is not valid, render the page with empty form
    #     context = {'form': form}
    #     return render(request, 'expenses/report_form.html', context)

def generate_expense_report(user, start_date, end_date, category_queryset):
    if category_queryset:
        expenses = Expense.objects.filter(
            user=user,
            date__range=[start_date, end_date],
            category__in=category_queryset
        )
    else:
        expenses = Expense.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).select_related('category')
        
    for expense in expenses:
        print(expense.title, expense.category) 
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

    # Get category queryset from the form's category field
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
            category_names = ', '.join([cat.name for cat in expense.category.all()])
            category_names = category_names if category_names else 'No Category'
            row = [expense.title, expense.amount, expense.date, category_names]
            writer.writerow(row)

    with open(csv_file_path, 'rb') as f:
        report.report_file.save(csv_file_name, ContentFile(f.read()))

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


