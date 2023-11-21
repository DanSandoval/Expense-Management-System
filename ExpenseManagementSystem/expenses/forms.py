from django import forms
from .models import Expense, Category, UserProfile, RecurringExpense
from django.forms import ModelForm

class YourReportForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date =  forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    category = forms.ModelChoiceField(queryset= Category.objects.order_by('name').values_list('name', flat=True).distinct(), required=False)
    
class ExpenseForm(forms.ModelForm):
    
    is_recurring = forms.BooleanField(required=False, label="Recurring Expense?")
    frequency = forms.ChoiceField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], required=False)
    recurring_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'date', 'category', 'is_recurring', 'frequency']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'category': forms.Select(),
            'recurring_from': forms.DateInput(attrs={'type': 'date'}),  # Add this line
        }
        labels = {
            'recurring_from': 'Recurring From',  # Update the label here
        }
    
    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
    # def __init__(self, *args, **kwargs):
    #     #user = kwargs.pop('user', None)
    #     super(ExpenseForm, self).__init__(*args, **kwargs)
    #     if user is not None:
    #         self.fields['category'].queryset = Category.objects.all()
        
class UserProfileForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'phone_number', 'birth_date', 'profile_picture']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),  # Add this line
            # Other widgets if needed
        }
        