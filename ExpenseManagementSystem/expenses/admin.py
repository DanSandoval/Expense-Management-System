from django.contrib import admin
from .models import Expense, Category,Budget, UserProfile

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'date', 'category', 'user')  # Fields to display in list view
    list_filter = ('date', 'category', 'user')  # Filters
    search_fields = ('title', 'category__name', 'user__username')  # Search capability

# Register your models here.
admin.site.register(Expense)
admin.site.register(Category)
admin.site.register(Budget)
admin.site.register(UserProfile)