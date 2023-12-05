from django.contrib import admin
from .models import Expense, Category, Budget, UserProfile, Report

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'date', 'display_categories', 'user')
    list_filter = ('date', 'category', 'user')
    search_fields = ('title', 'category__name', 'user__username')

    def display_categories(self, obj):
        # Fetching categories related to this specific expense
        Category = obj.category.all()  # This fetches categories related to the specific expense
        return ", ".join([cat.name for cat in obj.category.all()])
    display_categories.short_description = 'Categories'

admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)
admin.site.register(Budget)
admin.site.register(UserProfile)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_date')
    list_filter = ('user', 'created_date')
    search_fields = ('title',)
