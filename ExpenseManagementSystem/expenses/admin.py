from django.contrib import admin
from .models import Expense, Category, Budget, UserProfile, Report

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'date', 'display_category', 'user')  # Changed to display_category
    list_filter = ('date', 'category', 'user')  # category remains unchanged if it's now a ForeignKey
    search_fields = ('title', 'category__name', 'user__username')

    def display_category(self, obj):
        # Display the category of this specific expense
        return obj.category.name if obj.category else "No Category"
    display_category.short_description = 'Category'  # Changed to singular

admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)
admin.site.register(Budget)
admin.site.register(UserProfile)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_date')
    list_filter = ('user', 'created_date')
    search_fields = ('title',)
