from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_tests.base import SeleniumTestCase
import time
import uuid
import os

class UserAuthTests(SeleniumTestCase):
    """Tests for user authentication flows."""
    
    def test_login(self):
        """Test user can log in successfully."""
        # Open the login page
        self.browser.get(f"{self.live_server_url}/login/")
        
        # Take a screenshot for debugging
        self.browser.save_screenshot(os.path.join(self.screenshots_dir, "login_page.png"))
        
        # Fill in login details
        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")
        
        username_input.send_keys('testuser')
        password_input.send_keys('testpassword123')
        
        # Submit the form
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for login to complete and check that we're at the homepage
        WebDriverWait(self.browser, 10).until(
            EC.url_contains(self.live_server_url)
        )
        
        # Take a screenshot after login
        self.browser.save_screenshot(os.path.join(self.screenshots_dir, "after_login.png"))
        
        # Verify login was successful by checking for logout link
        logout_link = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Log Out"))
        )
        self.assertTrue(logout_link.is_displayed())
    
    def test_register(self):
        """Test user can register a new account."""
        # Generate a unique username to avoid conflicts
        unique_username = f"edgeuser{uuid.uuid4().hex[:8]}"
        
        # Navigate to register page
        self.browser.get(f"{self.live_server_url}/register/")
        
        # Take a screenshot for debugging
        self.browser.save_screenshot(os.path.join(self.screenshots_dir, "register_page.png"))
        
        # Fill in registration form - updated to use name attribute instead of ID
        username_field = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys(unique_username)
        
        # Find password fields - Django's UserCreationForm uses password1 and password2
        self.browser.find_element(By.NAME, "password1").send_keys("complex_password123")
        self.browser.find_element(By.NAME, "password2").send_keys("complex_password123")
        
        # Submit the form
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Take a screenshot after registration
        self.browser.save_screenshot(os.path.join(self.screenshots_dir, "after_register.png"))
        
        # Check we're redirected to login page or homepage (depending on your app's flow)
        WebDriverWait(self.browser, 10).until(
            EC.url_contains("/login/")
        )
        
        # Try logging in with the new account
        self.browser.find_element(By.NAME, "username").send_keys(unique_username)
        self.browser.find_element(By.NAME, "password").send_keys("complex_password123")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Take a screenshot after login with new account
        self.browser.save_screenshot(os.path.join(self.screenshots_dir, "login_with_new_account.png"))
        
        # Verify login was successful
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Log Out"))
        )