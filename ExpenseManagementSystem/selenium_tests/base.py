from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from expenses.models import Category
import os
import time
import logging

# Set up logging - keep it in the project directory for simplicity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='selenium_tests.log'
)
logger = logging.getLogger('selenium_tests')

class SeleniumTestCase(StaticLiveServerTestCase):
    """Base class for Selenium tests. Sets up and tears down the browser."""
    
    # Define screenshots directory - keep it simple and in project root
    screenshots_dir = "edge_test_results"
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        logger.info(f"Starting tests with LiveServerURL: {cls.live_server_url}")
        
        # Create screenshots directory
        os.makedirs(cls.screenshots_dir, exist_ok=True)
        logger.info(f"Created screenshots directory: {os.path.abspath(cls.screenshots_dir)}")
        
        # Set up Edge options
        edge_options = Options()
        # Uncomment the line below to run tests without a visible browser window
        # edge_options.add_argument("--headless")
        edge_options.add_argument("--window-size=1920,1080")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--disable-gpu")
        
        # Critical: Increase connection timeout and disable same-origin policy for testing
        edge_options.add_argument("--ignore-certificate-errors")
        edge_options.add_argument("--ignore-ssl-errors=yes")
        edge_options.add_argument("--disable-web-security")
        edge_options.add_argument("--allow-insecure-localhost")
        edge_options.add_argument("--disable-same-origin-policy")
        
        # Add performance logging preferences
        edge_options.add_argument("--enable-logging")
        edge_options.add_argument("--v=1")
        
        # Initialize the Edge WebDriver - use directly from PATH since it's available there
        try:
            # Simply initialize Edge from PATH without specifying any path
            logger.info("Initializing Edge WebDriver from PATH")
            cls.browser = webdriver.Edge(options=edge_options)
            logger.info("Successfully initialized Edge WebDriver from PATH")
        except Exception as e:
            logger.error(f"Error initializing Edge from PATH: {e}")
            # If that fails, try with a specific path as fallback
            try:
                current_dir = os.getcwd()
                possible_paths = [
                    os.path.join(current_dir, 'edgedriver_win64', 'msedgedriver.exe'),
                    os.path.join(os.path.dirname(current_dir), 'edgedriver_win64', 'msedgedriver.exe')
                ]
                
                for edgedriver_path in possible_paths:
                    if os.path.exists(edgedriver_path):
                        logger.info(f"Found Edge WebDriver at: {edgedriver_path}")
                        service = Service(edgedriver_path)
                        cls.browser = webdriver.Edge(service=service, options=edge_options)
                        break
                else:
                    raise FileNotFoundError("Could not find msedgedriver.exe in any expected location")
            except Exception as e2:
                logger.error(f"Error initializing Edge with specific path: {e2}")
                raise
        
        # Set page load timeout and implicit wait
        cls.browser.set_page_load_timeout(60)  # Increased timeout for slow connections
        cls.browser.implicitly_wait(10)
        
        # Save a screenshot of the initial browser state
        try:
            screenshot_path = os.path.join(cls.screenshots_dir, 'browser_initialized.png')
            cls.browser.save_screenshot(screenshot_path)
            logger.info(f"Saved initial screenshot to {screenshot_path}")
        except Exception as e:
            logger.warning(f"Could not save initial screenshot: {e}")
    
    @classmethod
    def tearDownClass(cls):
        try:
            logger.info("Quitting browser")
            cls.browser.quit()
        except Exception as e:
            logger.error(f"Error quitting browser: {e}")
        finally:
            super().tearDownClass()
    
    def setUp(self):
        """Create test user and categories for each test."""
        test_name = self._testMethodName
        logger.info(f"Setting up test: {test_name}")
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='testpassword123'
        )
        logger.info(f"Created test user: {self.user.username}")
        
        # Create test categories
        self.categories = []
        for cat_name in ['Food', 'Travel', 'Entertainment']:
            category = Category.objects.create(name=cat_name)
            self.categories.append(category)
        logger.info(f"Created {len(self.categories)} test categories")
        
        # Take a screenshot at the beginning of each test
        try:
            screenshot_path = os.path.join(self.screenshots_dir, f'{test_name}_start.png')
            self.browser.save_screenshot(screenshot_path)
            logger.info(f"Saved start screenshot to {screenshot_path}")
        except Exception as e:
            logger.warning(f"Could not save start screenshot for {test_name}: {e}")
            
    def tearDown(self):
        """Take screenshot on test failure and clean up."""
        test_name = self._testMethodName
        logger.info(f"Tearing down test: {test_name}")
        
        # Take a screenshot at the end of each test
        try:
            screenshot_path = os.path.join(self.screenshots_dir, f'{test_name}_end.png')
            self.browser.save_screenshot(screenshot_path)
            logger.info(f"Saved end screenshot to {screenshot_path}")
        except Exception as e:
            logger.warning(f"Could not save end screenshot for {test_name}: {e}")
        
        # Handle test failures
        if hasattr(self._outcome, 'errors') and self._outcome.errors:
            for test, err in self._outcome.errors:
                if err:
                    logger.error(f"Test {test_name} failed: {err}")
                    # Test failed, capture screenshot with a more descriptive name
                    try:
                        screenshot_path = os.path.join(self.screenshots_dir, f'error-{test_name}.png')
                        self.browser.save_screenshot(screenshot_path)
                        logger.info(f"Saved error screenshot to {screenshot_path}")
                    except Exception as e:
                        logger.warning(f"Could not save error screenshot for {test_name}: {e}")