from django.shortcuts import render, redirect, get_object_or_404
from .utils import generate_expense_report
from .forms import YourReportForm, ExpenseForm, UserProfileForm
from .models import UserProfile, Expense, Report
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.contrib import messages

# Import other necessary modules

def home(request):
    return render(request, 'expenses/home.html')

def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect(reverse('expense_confirmation', kwargs={'expense_id': expense.id}))
    else:
        form = ExpenseForm()#this loads the categories connected to a specific user
    return render(request, 'expenses/add_expense.html', {'form': form})

def view_reports(request):
    user = request.user
    user_reports = Report.objects.filter(user=request.user).order_by('-created_date')

    # Passing the reports to the template
    context = {'reports': user_reports}
    return render(request, 'expenses/view_reports.html', context)

def generate_report_view(request):
    context = {'form': YourReportForm()}
    if request.method == 'POST':
        form = YourReportForm(request.POST)
        if form.is_valid():
            user = request.user
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            category = form.cleaned_data.get('category')  # optional

            # Create a new Report instance
            report = Report()
            report.user = user
            # Set other fields for the report, such as title, created_date, etc.
            report.title = f"Report from {start_date} to {end_date}"

            # Assume generate_expense_report returns data for the report
            report_data = generate_expense_report(user, start_date, end_date, category)
            #might generate a file or a summary text here

            report.save()  # Save the report instance

            # Update context or redirect as needed
            messages.success(request, 'Report generated successfully.')
            return redirect('view_reports')  # Redirect to the reports view page
        else:
            print(form.errors)
            messages.error(request, 'Error in generating report.')

    return render(request, 'expenses/report_form.html', context)

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
    return render(request, 'expenses/expense_confirmation.html', {'expense': expense})

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


