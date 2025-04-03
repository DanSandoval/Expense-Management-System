"""
Simple standalone test script to verify Microsoft Edge basic functionality.
This script doesn't require Django or any other framework.
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
import subprocess

def create_screenshots_dir():
    """Create screenshots directory if it doesn't exist."""
    # Create directly in the current directory
    screenshots_dir = 'edge_test_screenshots'
    os.makedirs(screenshots_dir, exist_ok=True)
    return screenshots_dir

def setup_browser():
    """Initialize the Microsoft Edge browser."""
    print("Setting up Edge browser...")
    
    edge_options = Options()
    edge_options.add_argument("--window-size=1920,1080")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    
    # Critical SSL and security settings
    edge_options.add_argument("--ignore-certificate-errors")
    edge_options.add_argument("--ignore-ssl-errors=yes")
    edge_options.add_argument("--disable-web-security")
    
    # Initialize browser
    browser = webdriver.Edge(options=edge_options)
    browser.set_page_load_timeout(30)
    browser.implicitly_wait(10)
    
    print("Browser initialized successfully")
    return browser

def test_navigation_to_google():
    """Test simple navigation to Google."""
    print("\nTesting navigation to Google...")
    browser = setup_browser()
    
    try:
        # Navigate to Google
        browser.get("https://www.google.com")
        
        # Take a screenshot
        screenshots_dir = create_screenshots_dir()
        browser.save_screenshot(os.path.join(screenshots_dir, 'google_homepage.png'))
        print(f"Screenshot saved to {screenshots_dir}/google_homepage.png")
        
        # Check if the search box is present
        search_box = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys("Selenium WebDriver")
        
        # Take another screenshot
        browser.save_screenshot(os.path.join(screenshots_dir, 'google_with_search.png'))
        print(f"Screenshot saved to {screenshots_dir}/google_with_search.png")
        
        print("✅ Successfully navigated to Google and found search box")
        return True
    except Exception as e:
        print(f"❌ Error testing Google navigation: {e}")
        return False
    finally:
        browser.quit()

def is_django_server_running():
    """Check if Django server is running on port 8000."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    sock.close()
    return result == 0

def test_navigation_to_django_admin():
    """Test navigation to Django admin site (doesn't require a running server)."""
    print("\nTesting navigation to a public Django site...")
    browser = setup_browser()
    
    try:
        # Try to navigate to the Django project website instead of localhost
        browser.get("https://www.djangoproject.com")
        time.sleep(2)
        
        # Take a screenshot
        screenshots_dir = create_screenshots_dir()
        browser.save_screenshot(os.path.join(screenshots_dir, 'django_website.png'))
        print(f"Screenshot saved to {screenshots_dir}/django_website.png")
        
        # Check for Django logo or text
        page_title = browser.title
        print(f"Page title: {page_title}")
        
        # Check if the page loaded successfully
        if "Django" in page_title or "Django" in browser.page_source:
            print("✅ Successfully navigated to Django website")
            return True
        else:
            print("❌ Could not confirm Django page loaded correctly")
            return False
    except Exception as e:
        print(f"❌ Error testing Django website navigation: {e}")
        return False
    finally:
        browser.quit()

def optional_test_localhost():
    """Optional test to check localhost if a server is running."""
    if not is_django_server_running():
        print("\nSkipping localhost test - no server detected on port 8000")
        print("If you want to test localhost navigation, run:")
        print("python manage.py runserver")
        print("In a separate terminal window before running this test")
        return True
    
    print("\nDetected Django server running, testing localhost navigation...")
    browser = setup_browser()
    
    try:
        # Try to navigate to localhost
        browser.get("http://127.0.0.1:8000")  # Using IP address instead of localhost
        time.sleep(2)
        
        # Take a screenshot
        screenshots_dir = create_screenshots_dir()
        browser.save_screenshot(os.path.join(screenshots_dir, 'localhost.png'))
        print(f"Screenshot saved to {screenshots_dir}/localhost.png")
        
        # Check if we can access the page
        page_source = browser.page_source
        print(f"Page source length: {len(page_source)} characters")
        
        # Check for Django-specific elements
        indicators = [
            "<html", "<body", "<head", "<!DOCTYPE",
            "Django", "Expense", "Management"
        ]
        found_indicators = [ind for ind in indicators if ind in page_source]
        
        if found_indicators:
            print(f"✅ Found {len(found_indicators)} page indicators: {found_indicators}")
            return True
        else:
            print("❌ Could not find any page indicators in the source")
            return False
    except Exception as e:
        print(f"❌ Error testing localhost navigation: {e}")
        return False
    finally:
        browser.quit()

def main():
    """Run all browser tests."""
    print("=" * 60)
    print("Microsoft Edge WebDriver Basic Tests")
    print("=" * 60)
    
    # Test navigation to Google (general internet connectivity)
    google_test = test_navigation_to_google()
    
    # Test navigation to Django website (public site)
    django_test = test_navigation_to_django_admin()
    
    # Optionally test localhost if server is running
    localhost_test = optional_test_localhost()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Google Navigation Test: {'✅ PASS' if google_test else '❌ FAIL'}")
    print(f"Django Website Test: {'✅ PASS' if django_test else '❌ FAIL'}")
    
    # Overall result
    if google_test and django_test:
        print("\n✅ Main tests passed! Your Edge WebDriver setup appears to be working correctly.")
        
        # Show where screenshots are saved
        screenshots_dir = create_screenshots_dir()
        print(f"\nScreenshots have been saved to: {os.path.abspath(screenshots_dir)}")
        
        print("\nTo run the Django test server separately and test localhost:")
        print("1. Open a new terminal window")
        print("2. Run: python manage.py runserver")
        print("3. Run this script again to test localhost navigation")
        
        return 0
    else:
        print("\n❌ Some tests failed. There might be issues with your Edge WebDriver setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())