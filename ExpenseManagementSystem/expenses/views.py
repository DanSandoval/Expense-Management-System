from django.shortcuts import render, redirect
from .utils import generate_expense_report
from .forms import YourReportForm, ExpenseForm, UserProfileForm
from .models import UserProfile
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
            return redirect('home') # redirect to a page where you list expenses
    else:
        form = ExpenseForm()#this loads the categories connected to a specific user
    return render(request, 'expenses/add_expense.html', {'form': form})

def expense_report_view(request):
    # Assuming you have a form to capture report parameters
    if request.method == 'POST':
        form = YourReportForm(request.POST)
        if form.is_valid():
            user = request.user
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            category = form.cleaned_data.get('category')  # optional

            total_expense = generate_expense_report(user, start_date, end_date, category)
            # Now you can pass total_expense to your template or further processing
            return render(request, 'expenses/report_form.html')

    else:
        form = YourReportForm()

    return render(request, 'expenses/report_form.html', {'form': form})

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
            return redirect('profile')  # Redirect to the profile page
    else:
        form = UserProfileForm(instance=request.user.userprofile)
        
    return render(request, 'edit_profile.html', {'form': form})



# Create additional views here.


