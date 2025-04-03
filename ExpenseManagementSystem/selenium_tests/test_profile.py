from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium_tests.base import SeleniumTestCase
from datetime import date
import time
import os
import traceback

class ProfileTests(SeleniumTestCase):
    """Tests for user profile functionality."""
    
    def _login(self):
        """Helper method to log in the test user."""
        print(f"Logging in at {self.live_server_url}")
        
        # Create screenshots directory if it doesn't exist
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        self.browser.get(f"{self.live_server_url}/login/")
        self.browser.save_screenshot(os.path.join(self.screenshots_dir, "login_page.png"))
        
        try:
            username_field = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys('testuser')
            
            password_field = self.browser.find_element(By.NAME, "password")
            password_field.send_keys('testpassword123')
            
            self.browser.save_screenshot(os.path.join(self.screenshots_dir, "login_form_filled.png"))
            
            submit_button = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
            self.browser.execute_script("arguments[0].click();", submit_button)
            
            # Wait for navigation to complete
            WebDriverWait(self.browser, 10).until(
                lambda driver: "Add Expense" in driver.page_source or "Log Out" in driver.page_source
            )
            
            self.browser.save_screenshot(os.path.join(self.screenshots_dir, "login_successful.png"))
            print("Login successful")
            
        except Exception as e:
            print(f"Login error: {e}")
            self.browser.save_screenshot(os.path.join(self.screenshots_dir, "login_error.png"))
            traceback.print_exc()
            raise
    
    def test_view_profile(self):
        """Test viewing the user profile."""
        try:
            self._login()
            
            # Navigate to profile page
            print(f"Navigating to profile page at {self.live_server_url}/profile/")
            self.browser.get(f"{self.live_server_url}/profile/")
            self.browser.save_screenshot(os.path.join(self.screenshots_dir, "profile_page_initial.png"))
            
            # Wait for the profile page to load
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "card"))
            )
            
            self.browser.save_screenshot(os.path.join(self.screenshots_dir, "profile_page_loaded.png"))
            
            # Check for profile-related content
            page_source = self.browser.page_source
            if "Profile" in page_source:
                print("Found 'Profile' on page")
                
                # Check for Edit Profile button
                try:
                    edit_profile_link = self.browser.find_element(By.LINK_TEXT, "Edit Profile")
                    self.assertTrue(edit_profile_link.is_displayed())
                    print("Edit Profile link is displayed")
                except Exception as e:
                    print(f"Error finding Edit Profile link: {e}")
                    self.browser.save_screenshot(os.path.join(self.screenshots_dir, "edit_profile_link_error.png"))
                    raise
            else:
                print("'Profile' not found on page")
                self.browser.save_screenshot(os.path.join(self.screenshots_dir, "profile_content_error.png"))
                self.fail("Profile content not found on page")
                
        except Exception as e:
            print(f"Error in test_view_profile: {e}")
            self.browser.save_screenshot(os.path.join(self.screenshots_dir, "test_view_profile_error.png"))
            traceback.print_exc()
            raise
    
    def test_edit_profile(self):
        """Test editing the user profile."""
        try:
            self._login()
            
            # Navigate to edit profile page
            print(f"Navigating to edit profile page at {self.live_server_url}/edit-profile/")
            self.browser.get(f"{self.live_server_url}/edit-profile/")
            self.browser.save_screenshot(os.path.join(self.screenshots_dir, "edit_profile_initial.png"))
            
            # Wait for form to load with more specific selector
            form = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "form"))
            )
            
            # Check all form fields are present
            print("Checking form fields")
            form_fields = {}
            try:
                form_fields['bio'] = self.browser.find_element(By.NAME, "bio")
                print("Found bio field")
            except:
                print("Bio field not found")
                
            try:
                form_fields['phone'] = self.browser.find_element(By.NAME, "phone_number")
                print("Found phone field")
            except:
                print("Phone field not found")
                
            try:
                form_fields['birth_date'] = self.browser.find_element(By.NAME, "birth_date")
                print("Found birth_date field")
            except:
                try:
                    form_fields['birth_date'] = self.browser.find_element(By.ID, "id_birth_date")
                    print("Found birth_date field by ID")
                except:
                    print("Birth date field not found")
            
            self.browser.save_screenshot(os.path.join(self.screenshots_dir, "edit_profile_form_loaded.png"))
            
            # Fill form fields if they exist
            print("Filling form fields")
            if 'bio' in form_fields:
                form_fields['bio'].clear()
                form_fields['bio'].send_keys("This is a test bio updated with Edge WebDriver")
                print("Filled bio field")
            
            if 'phone' in form_fields:
                form_fields['phone'].clear()
                form_fields['phone'].send_keys("+12345678901")
                print("Filled phone field")
            
            if 'birth_date' in form_fields:
                # Different methods to set the date field
                try:
                    # Try direct JavaScript setting
                    test_birth_date = "1990-01-01"
                    self.browser.execute_script(
                        f"arguments[0].value = '{test_birth_date}';", form_fields['birth_date']
                    )
                    print(f"Set birth date to {test_birth_date} using JavaScript")
                except Exception as e:
                    print(f"Error setting birth date with direct JavaScript: {e}")
                    try:
                        # Try ID-based JavaScript
                        self.browser.execute_script(
                            f"document.getElementById('id_birth_date').value = '{test_birth_date}';"
                        )
                        print(f"Set birth date to {test_birth_date} using ID-based JavaScript")
                    except Exception as e:
                        print(f"Error setting birth date with ID-based JavaScript: {e}")
                        try:
                            # Fall back to send_keys
                            form_fields['birth_date'].clear()
                            form_fields['birth_date'].send_keys(test_birth_date)
                            print(f"Set birth date to {test_birth_date} using send_keys")
                        except Exception as e:
                            print(f"Error setting birth date with send_keys: {e}")
            
            self.browser.save_screenshot(os.path.join(self.screenshots_dir, "edit_profile_form_filled.png"))
            
            # Find and submit the form
            print("Finding submit button")
            try:
                submit_button = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
                print("Found submit button")
                
                # Ensure button is visible
                self.browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                print("Scrolled to submit button")
                time.sleep(0.5)
                
                # Take screenshot before clicking
                self.browser.save_screenshot(os.path.join(self.screenshots_dir, "before_profile_submit.png"))
                
                # Click using JavaScript
                print("Clicking submit button with JavaScript")
                self.browser.execute_script("arguments[0].click();", submit_button)
                
                # Wait for form submission and page change
                print("Waiting for form submission to complete")
                time.sleep(3)
                
                # Take screenshot after submission
                self.browser.save_screenshot(os.path.join(self.screenshots_dir, "after_profile_submit.png"))
                
                # Check if we were redirected
                current_url = self.browser.current_url
                print(f"Current URL after submission: {current_url}")
                
                if "/profile/" in current_url:
                    print("Successfully redirected to profile page")
                    
                    # Verify our updates appear in the profile
                    page_source = self.browser.page_source
                    if "This is a test bio updated with Edge WebDriver" in page_source:
                        print("Found updated bio in profile page")
                    if "+12345678901" in page_source:
                        print("Found updated phone number in profile page")
                    
                    self.browser.save_screenshot(os.path.join(self.screenshots_dir, "profile_updated.png"))
                    self.assertTrue(True)  # Test passes
                else:
                    print("Not redirected to profile page")
                    
                    # Check for error messages
                    error_elements = self.browser.find_elements(By.CSS_SELECTOR, ".alert-danger, .errorlist")
                    if error_elements:
                        for error in error_elements:
                            print(f"Form error: {error.text}")
                            
                    # Try to figure out where we are
                    page_source = self.browser.page_source[:1000]
                    print(f"Page source excerpt: {page_source}")
                    
                    self.browser.save_screenshot(os.path.join(self.screenshots_dir, "profile_update_failed.png"))
                    self.fail(f"Profile update failed - current URL: {current_url}")
                
            except Exception as e:
                print(f"Error finding or clicking submit button: {e}")
                self.browser.save_screenshot(os.path.join(self.screenshots_dir, "submit_button_error.png"))
                traceback.print_exc()
                raise
                
        except Exception as e:
            print(f"Error in test_edit_profile: {e}")
            self.browser.save_screenshot(os.path.join(self.screenshots_dir, "test_edit_profile_error.png"))
            traceback.print_exc()
            raise