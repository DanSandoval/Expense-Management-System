from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Expense, Category, UserProfile, User, RecurringExpense
from django.urls import reverse
from .utils import generate_expense_report
from datetime import date, timedelta
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
        
class RecurringExpenseModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a user
        test_user = User.objects.create_user(username='testuser', password='testpass')
        # Create a category
        test_category = Category.objects.create(name='Test Category')
        # Create an expense
        test_expense = Expense.objects.create(
            title='Test Expense',
            amount=100,
            date=date.today(),
            category=test_category,
            user=test_user
        )
        # Create a recurring expense
        RecurringExpense.objects.create(
            expense=test_expense,
            frequency='monthly',
            recurring_from=date.today()
        )

    def test_recurring_expense_creation(self):
        recurring_expense = RecurringExpense.objects.get(id=1)
        self.assertEqual(recurring_expense.frequency, 'monthly')
        self.assertEqual(recurring_expense.expense.title, 'Test Expense')
        self.assertTrue(recurring_expense.is_active)

    def test_recurring_expense_link_to_expense(self):
        expense = Expense.objects.get(id=1)
        recurring_expense = RecurringExpense.objects.get(expense=expense)
        self.assertEqual(recurring_expense.expense, expense)
        
class ExpenseEntryAndReportTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a test user
        cls.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword123')
        # Create a category
        cls.category = Category.objects.create(name='Test Category')
        # Create an expense
        cls.expense = Expense.objects.create(
            title='Test Expense', amount=100.00, date=date.today(), category=cls.category, user=cls.user
        )

    def test_expense_entry_and_report(self):
        # Test if the expense entry is created successfully
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(Expense.objects.first(), self.expense)

        # Generate report for the user
        report_data = generate_expense_report(self.user, date.today(), date.today())
        
        # Check if the report data includes the created expense
        self.assertIn(self.expense, report_data['expenses'])
        self.assertEqual(report_data['total_amount'], self.expense.amount)
        
class RecurringExpenseEntryAndReportTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = User.objects.create_user(username='testuser', email='test@example.com', password='12345')

        # Create test category
        cls.category = Category.objects.create(name="Test Category")

        # Create test expense
        cls.expense = Expense.objects.create(
            title="Test Expense", 
            amount=100, 
            date=date.today(), 
            category=cls.category, 
            user=cls.user
        )

        # Create recurring expense
        cls.recurring_expense = RecurringExpense.objects.create(
            expense=cls.expense, 
            frequency='monthly', 
            recurring_from=date.today(),
            is_active=True
        )

    def test_recurring_expense_creation(self):
        self.assertEqual(RecurringExpense.objects.count(), 1)
        self.assertEqual(RecurringExpense.objects.first(), self.recurring_expense)

    def test_report_generation_includes_recurring_expenses(self):
        # Create additional expenses for report testing
        Expense.objects.create(
            title="Additional Expense", 
            amount=50, 
            date=date.today() - timedelta(days=10), 
            category=self.category, 
            user=self.user
        )

        report_data = generate_expense_report(
            self.user, 
            date.today() - timedelta(days=30), 
            date.today()
        )
        self.assertIn(self.expense, report_data['expenses'])
        self.assertEqual(report_data['total_amount'], 150) # Assuming the sum of expenses is 150
        

class RecurringExpenseReportTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Creating test data
        cls.user = User.objects.create_user(username='testuser', email='test@example.com', password='12345')
        cls.category = Category.objects.create(name='Test Category')
        cls.expense = Expense.objects.create(
            title='Test Recurring Expense',
            amount=200,
            date=date.today() - timedelta(days=60),
            category=cls.category,
            user=cls.user
        )
        cls.recurring_expense = RecurringExpense.objects.create(
            expense=cls.expense,
            frequency='monthly',
            recurring_from=date.today() - timedelta(days=60),
            is_active=True
        )

    def test_generate_expense_report_with_recurring_expenses(self):
        # Testing report generation including recurring expenses
        report_data = generate_expense_report(
            self.user, 
            date.today() - timedelta(days=90), 
            date.today()
        )
        self.assertIn(self.expense, report_data['expenses'])
        self.assertGreaterEqual(report_data['total_amount'], self.expense.amount)        
        
class RecurringFromAttributeTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Creating test data
        cls.user = User.objects.create_user(username='testuser', email='test@example.com', password='12345')
        cls.category = Category.objects.create(name='Test Category')
        cls.expense = Expense.objects.create(
            title='Test Future Recurring Expense',
            amount=300,
            date=date.today() + timedelta(days=30),
            category=cls.category,
            user=cls.user
        )
        cls.recurring_expense = RecurringExpense.objects.create(
            expense=cls.expense,
            frequency='monthly',
            recurring_from=date.today() + timedelta(days=30),
            is_active=True
        )

    def test_recurring_from_effectiveness(self):
        # Testing if recurring_from attribute is respected
        report_data = generate_expense_report(
            self.user, 
            date.today() - timedelta(days=15), 
            date.today() + timedelta(days=15)
        )
        # The recurring expense should not be included in the report as it starts in the future
        self.assertNotIn(self.expense, report_data['expenses'])        

# Similar tests can be written for UserProfile and Category models
