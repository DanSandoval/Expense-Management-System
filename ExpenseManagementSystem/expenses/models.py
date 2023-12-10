from django.db import models
from django.contrib.auth.models import User
import uuid

def default_category():
    # Ensure there's at least one category and return its ID
    category, created = Category.objects.get_or_create(
        name="Default", defaults={'description': 'Auto-generated default category'})
    return category.id

# Create your models here.
class UserProfiles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio =models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)  
    birth_date = models.DateField(null=True, blank=True)  
    
    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    #user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True) # Optional: to allow user-specific categories
    
    def __str__(self):
        return self.name
    

class Expense(models.Model):
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.title
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    #many additional field possible here
    """profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)"""
    
    def __str__(self):
        return self.user.username
    
    
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_budget = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    # null=True, blank=True allows category to be optional

    def __str__(self):
        return f"{self.user.username}'s budget"
    
class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    report_file = models.FileField(upload_to='reports/', blank=True, null=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)    
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
class RecurringExpense(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=50)  # e.g., 'daily', 'weekly', 'monthly'
    recurring_from = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.expense.title} - {self.frequency}"

