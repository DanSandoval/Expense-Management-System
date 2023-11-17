from django import forms
from .models import Expense, Category
from django.forms import ModelForm

class YourReportForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date =  forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    category = forms.ModelChoiceField(queryset= Category.objects.order_by('name').values_list('name', flat=True).distinct(), required=False)
    
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'date', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'category': forms.Select()
        }
        
    # def __init__(self, *args, **kwargs):
    #     #user = kwargs.pop('user', None)
    #     super(ExpenseForm, self).__init__(*args, **kwargs)
    #     if user is not None:
    #         self.fields['category'].queryset = Category.objects.all()
            