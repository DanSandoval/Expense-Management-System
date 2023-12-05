from django import forms
from .models import Expense, Category, UserProfile, RecurringExpense
from django.forms import ModelForm
from django.core.validators import RegexValidator

class YourReportForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.order_by('name').distinct(),
        widget=forms.CheckboxSelectMultiple,  # Or forms.SelectMultiple for a dropdown
        required=False
    )
    
class ExpenseForm(forms.ModelForm):
    
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )
    is_recurring = forms.BooleanField(required=False, label="Recurring Expense?")
    frequency = forms.ChoiceField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], required=False)
    recurring_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'date', 'category', 'is_recurring', 'frequency']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'recurring_from': forms.DateInput(attrs={'type': 'date'}),
            'categories': forms.CheckboxSelectMultiple(),
            }
        labels = {
            'recurring_from': 'First Recurrence Date',  # Update the label here
        }
    
    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        
class UserProfileForm(forms.ModelForm):
    # Regular expression for validating phone numbers
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    # Adding the validator to the phone_number field
    phone_number = forms.CharField(validators=[phone_regex], max_length=17)
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'phone_number', 'birth_date', 'profile_picture']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),  # Add this line
            # Other widgets if needed
        }
        