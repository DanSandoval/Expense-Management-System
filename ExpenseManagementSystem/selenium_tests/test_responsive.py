from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_tests.base import SeleniumTestCase
import time

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
        self.browser.save_screenshot("mobile_before_toggle.png")
        
        # Check that the navbar toggler is visible
        navbar_toggler = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "navbar-toggler"))
        )
        self.assertTrue(navbar_toggler.is_displayed())
        
        # Locate the navbar collapse element
        navbar_collapse = self.browser.find_element(By.ID, "navbarCollapse")
        
        # Verify it's initially hidden (in most Bootstrap implementations)
        # Check computed style instead of is_displayed() which can be unreliable
        is_initially_visible = navbar_collapse.value_of_css_property("display") != "none"
        self.assertFalse(is_initially_visible, "Navbar should be collapsed initially on mobile")
        
        # Click the toggler button
        navbar_toggler.click()
        
        # Add delay to allow animation
        time.sleep(1)
        
        # Take a screenshot after clicking
        self.browser.save_screenshot("mobile_after_toggle.png")
        
        # Wait for the collapse animation to complete
        WebDriverWait(self.browser, 10).until(
            lambda browser: navbar_collapse.value_of_css_property("display") != "none"
        )
        
        # Now verify the menu is expanded
        is_expanded = navbar_collapse.value_of_css_property("display") != "none"
        self.assertTrue(is_expanded, "Navbar should be expanded after clicking toggler")
        
        # Reset window size
        self.browser.set_window_size(1920, 1080)