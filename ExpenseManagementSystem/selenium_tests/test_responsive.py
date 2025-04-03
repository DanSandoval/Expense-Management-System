from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium_tests.base import SeleniumTestCase
import time
import os

class ResponsiveTests(SeleniumTestCase):
    """Tests for responsive design across different screen sizes."""
    
    def _login(self):
        """Helper method to log in the test user."""
        self.browser.get(f"{self.live_server_url}/login/")
        self.browser.find_element(By.NAME, "username").send_keys('testuser')
        self.browser.find_element(By.NAME, "password").send_keys('testpassword123')
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Log Out"))
        )
    
    def test_mobile_navigation(self):
        """Test the navigation menu works on mobile screen sizes."""
        # First login at normal size
        self._login()
        
        # Then resize to mobile dimensions
        self.browser.set_window_size(375, 812)  # iPhone X dimensions
        
        # Go to the homepage 
        self.browser.get(self.live_server_url)
        
        # Take a screenshot of initial state
        self.browser.save_screenshot(os.path.join(self.screenshots_dir, "mobile_before_toggle.png"))
        
        # Check that the navbar toggler is visible
        navbar_toggler = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "navbar-toggler"))
        )
        self.assertTrue(navbar_toggler.is_displayed())
        
        # Locate the navbar collapse element
        navbar_collapse = self.browser.find_element(By.ID, "navbarCollapse")
        
        # Get initial state
        initial_display = self.browser.execute_script(
            "return window.getComputedStyle(arguments[0]).getPropertyValue('display')", 
            navbar_collapse
        )
        print(f"Initial navbar display: {initial_display}")
        self.browser.save_screenshot(os.path.join(self.screenshots_dir, "initial_navbar_state.png"))
        
        # Use JavaScript to click the toggler, which is more reliable
        self.browser.execute_script("arguments[0].click();", navbar_toggler)
        
        # Add delay to allow animation
        time.sleep(2)  # Increased delay
        
        # Take a screenshot after clicking
        self.browser.save_screenshot(os.path.join(self.screenshots_dir, "mobile_after_toggle.png"))
        
        # Multiple ways to verify the menu expanded
        try:
            # Way 1: Check if menu has 'show' class
            is_expanded = self.browser.execute_script(
                "return arguments[0].classList.contains('show')", 
                navbar_collapse
            )
            
            if is_expanded:
                print("Menu has 'show' class - success")
                self.assertTrue(True)
                return
                
            # Way 2: Check if element has height
            is_visible = self.browser.execute_script(
                "return arguments[0].getBoundingClientRect().height > 0", 
                navbar_collapse
            )
            
            if is_visible:
                print("Menu has height > 0 - success")
                self.assertTrue(True)
                return
                
            # Way 3: Check if any links are visible
            menu_items = navbar_collapse.find_elements(By.TAG_NAME, "a")
            for item in menu_items:
                if item.is_displayed():
                    print(f"Menu item visible: {item.text} - success")
                    self.assertTrue(True)
                    return
                    
            # If we get here, none of our verification methods worked
            # Take one more screenshot and report the issue
            self.browser.save_screenshot(os.path.join(self.screenshots_dir, "navbar_verify_failed.png"))
            self.fail("Could not verify navbar menu expanded")
            
        finally:
            # Reset window size at the end
            self.browser.set_window_size(1920, 1080)