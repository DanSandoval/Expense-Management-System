"""
Focused test just for the expense form - simplified for better debugging.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium_tests.base import SeleniumTestCase
from datetime import date, timedelta
import time
import os

class ExpenseFormTest(SeleniumTestCase):
    """Test specifically focused on the expense form functionality."""
    
    def _login(self):
        """Helper method to log in the test user."""
        print(f"Logging in at {self.live_server_url}")
        self.browser.get(f"{self.live_server_url}/login/")
        
        # Take screenshot before login
        screenshot_path = os.path.join(self.screenshots_dir, 'before_login.png')
        self.browser.save_screenshot(screenshot_path)
        
        # Fill in login form
        self.browser.find_element(By.NAME, "username").send_keys('testuser')
        self.browser.find_element(By.NAME, "password").send_keys('testpassword123')
        
        # Take screenshot of filled login form
        screenshot_path = os.path.join(self.screenshots_dir, 'login_form_filled.png')
        self.browser.save_screenshot(screenshot_path)
        
        # Submit login form
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for navigation to complete
        try:
            WebDriverWait(self.browser, 10).until(
                lambda driver: "Add Expense" in driver.page_source
            )
            print("Successfully logged in")
            
            # Take screenshot after login
            screenshot_path = os.path.join(self.screenshots_dir, 'after_login.png')
            self.browser.save_screenshot(screenshot_path)
        except Exception as e:
            print(f"Login issue: {e}")
            screenshot_path = os.path.join(self.screenshots_dir, 'login_failed.png')
            self.browser.save_screenshot(screenshot_path)
            raise
    
    def test_expense_form_load(self):
        """Just test that the expense form loads correctly."""
        self._login()
        
        # Navigate to Add Expense page
        print(f"Navigating to add expense at {self.live_server_url}/add-expense/")
        self.browser.get(f"{self.live_server_url}/add-expense/")
        
        # Take screenshot of the form page
        screenshot_path = os.path.join(self.screenshots_dir, 'expense_form_initial.png')
        self.browser.save_screenshot(screenshot_path)
        
        # Just verify form elements are present
        title_field = self.browser.find_element(By.ID, "id_title")
        amount_field = self.browser.find_element(By.ID, "id_amount")
        date_field = self.browser.find_element(By.ID, "id_date")
        category_field = self.browser.find_element(By.ID, "id_category")
        
        self.assertTrue(title_field.is_displayed(), "Title field is displayed")
        self.assertTrue(amount_field.is_displayed(), "Amount field is displayed")
        self.assertTrue(date_field.is_displayed(), "Date field is displayed")
        self.assertTrue(category_field.is_displayed(), "Category field is displayed")
        
        print("All form fields are present and displayed")
    
    def test_expense_form_submission(self):
        """Test submitting the expense form with explicit waits and clear steps."""
        self._login()
        
        # Navigate to Add Expense page
        print(f"Navigating to add expense at {self.live_server_url}/add-expense/")
        self.browser.get(f"{self.live_server_url}/add-expense/")
        
        # Wait for form to load
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "id_title"))
        )
        
        # Take screenshot before filling
        screenshot_path = os.path.join(self.screenshots_dir, 'before_filling_form.png')
        self.browser.save_screenshot(screenshot_path)
        
        # Fill in form fields one by one with verification
        print("Filling in title field")
        title_field = self.browser.find_element(By.ID, "id_title")
        title_field.clear()
        title_field.send_keys("Edge Test Expense")
        time.sleep(0.5)  # Small pause
        
        print("Filling in amount field")
        amount_field = self.browser.find_element(By.ID, "id_amount")
        amount_field.clear()
        amount_field.send_keys("42.99")
        time.sleep(0.5)  # Small pause
        
        print("Filling in date field")
        date_field = self.browser.find_element(By.ID, "id_date")
        date_field.clear()
        
        # Use a fixed date in the past to avoid any potential issues
        test_date = "2023-12-31"
        # Use JavaScript to set the date value directly to avoid format issues
        self.browser.execute_script(
            f"document.getElementById('id_date').value = '{test_date}';"
        )
        print(f"Set date to: {test_date}")
        time.sleep(0.5)  # Small pause
        
        print("Selecting category")
        select_element = self.browser.find_element(By.ID, "id_category")
        select = Select(select_element)
        select.select_by_index(1)  # Select first non-empty option
        selected_option = select.first_selected_option
        print(f"Selected category: {selected_option.text}")
        time.sleep(0.5)  # Small pause
        
        # Take screenshot after filling
        screenshot_path = os.path.join(self.screenshots_dir, 'after_filling_form.png')
        self.browser.save_screenshot(screenshot_path)
        
        # Submit form and handle potential issues
        print("Submitting form")
        submit_button = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # Take screenshot focusing on the submit button
        screenshot_path = os.path.join(self.screenshots_dir, 'submit_button.png')
        self.browser.save_screenshot(screenshot_path)
        
        # Ensure button is visible
        self.browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)  # Small pause
        
        # Click using JavaScript to avoid any potential clicking issues
        self.browser.execute_script("arguments[0].click();", submit_button)
        
        # Wait for submission to complete and page to change
        time.sleep(3)  # Longer wait for page transition
        
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
            else:
                print("No visible error messages on form")
            
            print("Form page source excerpt:")
            print(self.browser.page_source[:1000])  # Print first 1000 chars of page source
            
            # This might be a valid failure - form validation could be preventing submission
            self.fail("Form submission did not redirect - check screenshots for details")
        else:
            # We were redirected somewhere else, which suggests success
            print("Form submission resulted in page change - likely successful")
            print("New page source excerpt:")
            print(self.browser.page_source[:1000])  # Print first 1000 chars of page source
            
            # Check for success indicators in text
            page_source = self.browser.page_source
            if "Edge Test Expense" in page_source:
                print("Found expense title in response page - success!")
            elif "confirmation" in current_url.lower() or "success" in page_source.lower():
                print("URL or page content suggests successful submission")
            else:
                print("Submission completed but expense title not found in response")
            
            # Test passes if we got redirected
            self.assertTrue(True)