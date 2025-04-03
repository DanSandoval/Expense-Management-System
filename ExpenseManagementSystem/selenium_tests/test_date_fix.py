"""
Test specifically focused on fixing the date format issue in the expense form.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium_tests.base import SeleniumTestCase
from datetime import date, timedelta
import time
import os

class DateFormatTest(SeleniumTestCase):
    """Test specifically focused on fixing the date format issue."""
    
    def _login(self):
        """Helper method to log in the test user."""
        print(f"Logging in at {self.live_server_url}")
        self.browser.get(f"{self.live_server_url}/login/")
        
        # Fill in login form
        self.browser.find_element(By.NAME, "username").send_keys('testuser')
        self.browser.find_element(By.NAME, "password").send_keys('testpassword123')
        
        # Submit login form
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for navigation to complete
        try:
            WebDriverWait(self.browser, 10).until(
                lambda driver: "Add Expense" in driver.page_source
            )
            print("Successfully logged in")
        except Exception as e:
            print(f"Login issue: {e}")
            raise
    
    def test_expense_form_with_correct_date(self):
        """Test submitting the expense form with proper date format."""
        self._login()
        
        # Navigate to Add Expense page
        print(f"Navigating to add expense at {self.live_server_url}/add-expense/")
        self.browser.get(f"{self.live_server_url}/add-expense/")
        
        # Wait for form to load
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "id_title"))
        )
        
        # Take screenshot before filling
        os.makedirs(self.screenshots_dir, exist_ok=True)
        screenshot_path = os.path.join(self.screenshots_dir, 'before_filling_form.png')
        self.browser.save_screenshot(screenshot_path)
        
        # Fill in form fields one by one
        print("Filling in title field")
        title_field = self.browser.find_element(By.ID, "id_title")
        title_field.clear()
        title_field.send_keys("Date Format Test Expense")
        
        print("Filling in amount field")
        amount_field = self.browser.find_element(By.ID, "id_amount")
        amount_field.clear()
        amount_field.send_keys("42.99")
        
        print("Filling in date field - using correct YYYY-MM-DD format")
        date_field = self.browser.find_element(By.ID, "id_date")
        date_field.clear()
        
        # Use a valid date in the required format (YYYY-MM-DD)
        test_date = "2023-12-31"  # Use this fixed valid date
        self.browser.execute_script(f"document.getElementById('id_date').value = '{test_date}'")
        print(f"Set date to: {test_date}")
        
        # Take screenshot after setting date
        screenshot_path = os.path.join(self.screenshots_dir, 'after_setting_date.png')
        self.browser.save_screenshot(screenshot_path)
        
        print("Selecting category")
        select_element = self.browser.find_element(By.ID, "id_category")
        select = Select(select_element)
        select.select_by_index(1)  # Select first non-empty option
        
        # Take screenshot after filling
        screenshot_path = os.path.join(self.screenshots_dir, 'after_filling_form.png')
        self.browser.save_screenshot(screenshot_path)
        
        # Submit form
        print("Submitting form")
        submit_button = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # Ensure button is visible and click using JavaScript
        self.browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        self.browser.execute_script("arguments[0].click();", submit_button)
        
        # Wait for submission to complete
        time.sleep(3)
        
        # Take screenshot after submission
        screenshot_path = os.path.join(self.screenshots_dir, 'after_form_submission.png')
        self.browser.save_screenshot(screenshot_path)
        
        # Print current URL to help with debugging
        current_url = self.browser.current_url
        print(f"Current URL after submission: {current_url}")
        
        # Check if we were redirected (success case) or still on the form (error case)
        if "/add-expense/" in current_url:
            # We're still on the form page, check for error messages
            print("Still on form page, checking for errors")
            error_elements = self.browser.find_elements(By.CSS_SELECTOR, ".alert-danger, .errorlist")
            if error_elements:
                for error in error_elements:
                    print(f"Form error: {error.text}")
            
            # Check if there's a date format error specifically
            date_field_parent = self.browser.find_element(By.ID, "id_date").find_element(By.XPATH, "./..")
            if "Enter a valid date" in date_field_parent.text:
                print("Date format error detected")
                self.fail("Date format is still incorrect")
            else:
                print("No specific date format error found, but form still not submitted successfully")
                self.fail("Form submission failed for unknown reasons")
        else:
            # We were redirected somewhere else, which suggests success!
            print("Form submission resulted in page change - successfully submitted!")
            self.assertTrue(True)
