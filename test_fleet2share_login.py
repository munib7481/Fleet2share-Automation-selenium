import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ===================================================================
# LOCATORS (EASILY CHANGEABLE)
# Modify the CSS Selectors below if the application's UI changes.
# ===================================================================
class Fleet2ShareLocators:
    # Login Page Locators
    # Login Page Locators (Updated for MUI components)
    EMAIL_INPUT = "input[placeholder*='mail']"   # Matches 'Emailadres invullen' or 'Email'
    PASSWORD_INPUT = "input[type='password']"
    LOGIN_BUTTON = "button.MuiButton-contained"  # Primary MUI button
    
    # Validation/Message Locators
    ERROR_MESSAGE = "div[role='status']"         # Toast notification notification
    DASHBOARD_ELEMENT = "main"                   # Generic element to check for successful login


# ===================================================================
# PAGE OBJECT MODEL
# ===================================================================
class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
    def show_status(self, message):
        """Displays a temporary banner on the webpage for visibility"""
        script = f"""
        let msg = document.getElementById('test-status-banner');
        if (!msg) {{
            msg = document.createElement('div');
            msg.id = 'test-status-banner';
            msg.style.position = 'fixed';
            msg.style.top = '20px';
            msg.style.left = '50%';
            msg.style.transform = 'translateX(-50%)';
            msg.style.backgroundColor = '#4caf50';
            msg.style.color = 'white';
            msg.style.padding = '12px 24px';
            msg.style.borderRadius = '8px';
            msg.style.zIndex = '10000';
            msg.style.fontWeight = 'bold';
            msg.style.fontSize = '18px';
            msg.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
            msg.style.transition = 'all 0.3s ease';
            document.body.appendChild(msg);
        }}
        msg.innerText = "{message}";
        msg.style.backgroundColor = "{'#f44336' if 'Invalid' in message or 'Wrong' in message else '#4caf50'}";
        """
        self.driver.execute_script(script)
        print(f"[TEST STATUS] {message}")
        
    def load(self):
        self.driver.get("https://dev.fleet2share.com/login")
        
    def enter_email(self, email):
        status = f"Entering {'Valid' if '@' in email else 'Invalid'} Email: {email}"
        self.show_status(status)
        element = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, Fleet2ShareLocators.EMAIL_INPUT)))
        element.clear()
        element.send_keys(email)
        time.sleep(2)  # Delay for visibility
        
    def enter_password(self, password):
        status = f"Entering {'Valid' if len(password) >= 8 else 'Short/Invalid'} Password: {password}"
        self.show_status(status)
        element = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, Fleet2ShareLocators.PASSWORD_INPUT)))
        element.clear()
        element.send_keys(password)
        time.sleep(2)  # Delay for visibility
        
    def click_login(self):
        self.show_status("Clicking Login Button...")
        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, Fleet2ShareLocators.LOGIN_BUTTON)))
        element.click()
        time.sleep(2)  # Delay for visibility
        
    def get_error_message(self):
        element = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, Fleet2ShareLocators.ERROR_MESSAGE)))
        return element.text

    def is_dashboard_loaded(self):
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, Fleet2ShareLocators.DASHBOARD_ELEMENT)))
            return True
        except:
            return False


# ===================================================================
# TEST CASES
# ===================================================================
class TestFleet2ShareLogin(unittest.TestCase):

    def setUp(self):
        # Setup Chrome WebDriver
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.login_page = LoginPage(self.driver)

    def test_01_successful_login(self):
        """Test Case: Valid login credentials"""
        self.login_page.load()
        self.login_page.enter_email("Sarah@fleet.com")
        self.login_page.enter_password("12345678")
        self.login_page.click_login()
        time.sleep(8)
        # Verify dashboard is loaded (or URL has changed)
        self.assertTrue(self.login_page.is_dashboard_loaded(), "Dashboard did not load after valid login.")
        self.assertNotIn("login", self.driver.current_url.lower())

    def test_02_invalid_password(self):
        """Test Case: Valid email but incorrect password"""
        self.login_page.load()
        self.login_page.enter_email("valid_user@fleet2share.com")
        self.login_page.enter_password("WrongPassword123")
        self.login_page.click_login()
        
        # Verify error message is shown
        error_text = self.login_page.get_error_message()
        self.assertTrue(len(error_text) > 0, "Error message was not displayed.")

    def test_03_invalid_email_format(self):
        """Test Case: Invalid email format"""
        self.login_page.load()
        self.login_page.enter_email("invalid_email")
        self.login_page.enter_password("Password123!")
        self.login_page.click_login()
        
        # Depending on the app, either HTML5 validation stops it, or server returns error
        # Assuming an error message is shown on the page
        error_text = self.login_page.get_error_message()
        self.assertTrue(len(error_text) > 0, "Validation message for invalid email format was not displayed.")

    def test_04_empty_credentials(self):
        """Test Case: Empty email and password fields"""
        self.login_page.load()
        self.login_page.enter_email("")
        self.login_page.enter_password("")
        self.login_page.click_login()
        
        # Verify that the user stays on the login page
        self.assertIn("login", self.driver.current_url.lower())

    def tearDown(self):
        # Close the browser after each test
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    unittest.main()
