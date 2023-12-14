from django import forms
from .models import Expense, Category, UserProfile, RecurringExpense
from django.forms import ModelForm
from django.core.validators import RegexValidator

CHART_CHOICES = [
    ('donut', 'Donut Chart'),
    ('line', 'Line Chart'),
    ('polar', 'Polar Area Chart'),
]

class YourReportForm(forms.Form):
    custom_title = forms.CharField(max_length=100, required=False, label="Report Title (optional)")
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.order_by('name').distinct(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'horizontal-select'}),
        required=False
    )
    
    chart_type = forms.ChoiceField(choices=CHART_CHOICES, required=False, label='Chart Type')
    
class ExpenseForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(),  # You can choose a different widget if you prefer
        required=False
    )

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'date', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
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
        