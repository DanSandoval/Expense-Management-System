"""
Helper script to run Selenium tests for the Expense Management System.
This script ensures the test database is set up correctly before running tests.
"""

import os
import sys
import django
from django.core.management import call_command

# Add the parent directory to sys.path so Python can find your Django project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expensemanagementsystem.settings')
django.setup()

def run_tests():
    """Run all Selenium tests in the selenium_tests directory."""
    # First, make migrations and migrate to ensure test database is up to date
    print("Setting up test database...")
    call_command('migrate')
    
    # Populate default categories for tests
    print("Creating test categories...")
    call_command('populate_categories')
    
    # Run tests
    print("Running Selenium tests...")
    # Using Django test runner
    call_command('test', 'selenium_tests', verbosity=2)
    
    # Alternatively, if you prefer to use pytest:
    # import pytest
    # pytest.main(['selenium_tests'])

if __name__ == '__main__':
    run_tests()