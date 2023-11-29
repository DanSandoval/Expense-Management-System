"""
URL configuration for ExpenseManagementSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from expenses.views import generate_report_view, add_expense, home, report_detail, edit_profile, register_view, expense_confirmation, profile_view, view_reports

urlpatterns = [
    path('', home, name='home'),
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
    path('generate-report/',generate_report_view, name= 'generate_report'),
    path('add-expense/',add_expense, name='add_expense'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('expense-confirmation/<int:expense_id>/', expense_confirmation, name='expense_confirmation'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile_view'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('view-reports/', view_reports, name='view_reports'),
    path('report/<int:report_id>/', report_detail, name='report_detail'),
]