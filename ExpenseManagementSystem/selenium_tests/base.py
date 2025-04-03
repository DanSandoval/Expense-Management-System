from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from expenses.models import Category
import os

class SeleniumTestCase(StaticLiveServerTestCase):
    """Base class for Selenium tests. Sets up and tears down the browser."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up Chrome options - headless mode is useful for CI/CD environments
        chrome_options = Options()
        # Uncomment the line below to run tests without a visible browser window
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Initialize the Chrome WebDriver
        # Try to use ChromeDriver directly without WebDriverManager
        try:
            # First, try to use Chrome from PATH
            cls.browser = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Error initializing Chrome from PATH: {e}")
            try:
                # Try with a specific path if you know where ChromeDriver is
                # You can update this path to match where you've placed chromedriver
                chromedriver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
                service = Service(chromedriver_path)
                cls.browser = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e2:
                print(f"Error initializing Chrome with specific path: {e2}")
                raise
        
        cls.browser.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()
    
    def setUp(self):
        """Create test user and categories for each test."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create test categories
        self.categories = []
        for cat_name in ['Food', 'Travel', 'Entertainment']:
            category = Category.objects.create(name=cat_name)
            self.categories.append(category)
            
    def tearDown(self):
        """Take screenshot on test failure."""
        if hasattr(self._outcome, 'errors') and self._outcome.errors:
            for test, err in self._outcome.errors:
                if err:
                    # Test failed, capture screenshot
                    screenshot_name = f"error-{self._testMethodName}.png"
                    self.browser.save_screenshot(screenshot_name)
                    print(f"Screenshot saved as {screenshot_name}")