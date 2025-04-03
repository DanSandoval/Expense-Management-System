from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium_tests.base import SeleniumTestCase
from datetime import date
import time

class ExpenseWorkflowTests(SeleniumTestCase):
    """End-to-end tests for core expense management workflows."""
    
    def _login(self):
        """Helper method to log in the test user."""
        self.browser.get(f"{self.live_server_url}/login/")
        self.browser.find_element(By.NAME, "username").send_keys('testuser')
        self.browser.find_element(By.NAME, "password").send_keys('testpassword123')
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Add Expense"))
        )
    
    def test_inspect_form_ids(self):
        """Inspect the actual IDs of form elements for debugging."""
        self._login()
        
        # Navigate to Add Expense page
        self.browser.get(f"{self.live_server_url}/add-expense/")
        
        # Wait for the page to load
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form"))
        )
        
        # Print all form element IDs and names for debugging
        form_elements = self.browser.find_elements(By.CSS_SELECTOR, "form input, form select, form textarea")
        for element in form_elements:
            print(f"Form element: {element.get_attribute('name')} - ID: {element.get_attribute('id')}")
        
        self.assertTrue(True)  # Just to make the test pass
    
    def test_add_expense(self):
        """Test adding a new expense."""
        self._login()
        
        # Navigate to Add Expense page
        self.browser.get(f"{self.live_server_url}/add-expense/")
        
        # Wait for form to load - use name attribute instead of ID
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form"))
        )
        
        time.sleep(1)  # Small delay to ensure form is fully loaded
        
        # Fill out the expense form - use name instead of ID
        title_field = self.browser.find_element(By.NAME, "title")
        amount_field = self.browser.find_element(By.NAME, "amount")
        date_field = self.browser.find_element(By.NAME, "date")
        
        title_field.send_keys("Selenium Test Expense")
        amount_field.send_keys("42.99")
        
        # Set the date
        date_field.clear()
        date_field.send_keys(date.today().strftime("%Y-%m-%d"))
        
        # Find and select a category - this can be tricky, let's try multiple approaches
        try:
            # First try by name
            select = Select(self.browser.find_element(By.NAME, "category"))
            select.select_by_visible_text(self.categories[0].name)
        except Exception:
            try:
                # Try by ID
                select = Select(self.browser.find_element(By.ID, "id_category"))
                select.select_by_index(0)  # Just select the first option
            except Exception as e:
                print(f"Failed to select category: {e}")
                # As a last resort, take a screenshot to diagnose
                self.browser.save_screenshot("category_selection_error.png")
                raise
        
        # Submit the form
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Verify we're taken to the confirmation page or redirected appropriately
        WebDriverWait(self.browser, 10).until(
            EC.url_contains("expense")
        )
        
        # Verify some content that would indicate success
        self.assertIn("Selenium Test Expense", self.browser.page_source)
        self.assertIn("42.99", self.browser.page_source)
    
    def test_generate_report(self):
        """Test generating an expense report with charts."""
        self._login()
        
        # First add an expense to ensure we have data
        self.browser.get(f"{self.live_server_url}/add-expense/")
        
        # Wait for form to load
        time.sleep(1)
        
        # Fill out the form
        self.browser.find_element(By.NAME, "title").send_keys("Report Test Expense")
        self.browser.find_element(By.NAME, "amount").send_keys("75.50")
        
        date_input = self.browser.find_element(By.NAME, "date")
        date_input.clear()
        date_input.send_keys(date.today().strftime("%Y-%m-%d"))
        
        # Select category
        try:
            select = Select(self.browser.find_element(By.NAME, "category"))
            select.select_by_visible_text(self.categories[0].name)
        except Exception:
            select = Select(self.browser.find_element(By.ID, "id_category"))
            select.select_by_index(0)
        
        # Submit form
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for confirmation/redirect
        WebDriverWait(self.browser, 10).until(
            EC.url_contains("expense")
        )
        
        # Navigate to Generate Reports
        self.browser.find_element(By.LINK_TEXT, "Generate Reports").click()
        
        # Wait for form to load - use more reliable selectors
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form"))
        )
        
        time.sleep(1)  # Give form time to fully render
        
        # Fill out report form
        today = date.today().strftime("%Y-%m-%d")
        
        # Use name attributes which are more reliable
        start_date = self.browser.find_element(By.NAME, "start_date")
        end_date = self.browser.find_element(By.NAME, "end_date")
        
        start_date.clear()
        end_date.clear()
        
        start_date.send_keys(today)
        end_date.send_keys(today)
        
        # Select category - this may be a checkbox or multiple selection in your app
        # First print what's available to help debug
        category_options = self.browser.find_elements(By.CSS_SELECTOR, "input[name='category']")
        if category_options:
            # If it's checkboxes, click the first one
            category_options[0].click()
        else:
            # Try finding toggle buttons
            toggle_labels = self.browser.find_elements(By.CSS_SELECTOR, ".toggle-button")
            if toggle_labels:
                toggle_labels[0].click()
            else:
                # Take screenshot for debugging
                self.browser.save_screenshot("category_selection_report.png")
                print("Could not find category selection elements")
        
        # Submit the report form
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Verify report is generated successfully
        # This could be checking for specific text, table presence, or chart elements
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )
        
        # Verify our expense is in the report
        self.assertIn("Report Test Expense", self.browser.page_source)