from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Expense, Category, UserProfile, User
from django.urls import reverse
from .utils import generate_expense_report
from datetime import date
from decimal import Decimal

class ExpenseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        
        category, created = Category.objects.get_or_create(name='Food')
        test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        Expense.objects.create(
            title='Lunch', 
            amount=15.99, 
            date='2023-01-01', 
            category=category,
            user=test_user  # Associate the expense with the test user
    )

    def test_title_label(self):
        expense = Expense.objects.get(id=1)
        field_label = expense._meta.get_field('title').verbose_name
        self.assertEquals(field_label, 'title')

    def test_string_representation(self):
        expense = Expense.objects.get(id=1)
        expected_object_name = f'{expense.title}'
        self.assertEquals(expected_object_name, str(expense))

class AddExpenseViewTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get('/add-expense/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('add_expense'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/add_expense.html')
        
class GenerateExpenseReportTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        category_food = Category.objects.create(name='Food')
        category_travel = Category.objects.create(name='Travel')
        Expense.objects.create(title='Lunch', amount=15.99, date=date(2023, 1, 1), category=category_food, user=user)
        Expense.objects.create(title='Bus Ticket', amount=30, date=date(2023, 1, 2), category=category_travel, user=user)

    def test_generate_expense_report(self):
        user = User.objects.get(username='testuser')
        report = generate_expense_report(user, '2023-01-01', '2023-01-31')
        expenses = report['expenses']
        total_amount = report['total_amount']

        self.assertEqual(expenses.count(), 2)
        self.assertTrue(expenses.filter(title='Lunch').exists())
        self.assertTrue(expenses.filter(title='Bus Ticket').exists())
        self.assertEqual(total_amount, Decimal('45.99'))  # Adjust this value based on the expected total amount

        
class ExpenseReportViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_expense_report_view(self):
        response = self.client.get(reverse('generate_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/report_form.html')
        
class UserRegistrationAndExpenseIntegrationTest(TestCase):

    def setUp(self):
        # Create a test category
        self.category = Category.objects.create(name='Test Category')

    def test_user_registration_and_expense_tracking(self):
        # Create a new user
        self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'strong_password',
            'password2': 'strong_password'
        })

        # Log in the user
        self.client.login(username='testuser', password='strong_password')

        # Add an expense
        response = self.client.post(reverse('add_expense'), {
            'title': 'Test Expense',
            'amount': 100.00,
            'date': '2023-01-01',
            'category': self.category.id
        }, follow=True)

        # Check that the expense was added successfully
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Expense.objects.filter(title='Test Expense').exists())
# Similar tests can be written for UserProfile and Category models
