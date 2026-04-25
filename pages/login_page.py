import logging
import re
from pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.signin_link = self.page.locator("a[href*='signin'], a:has-text('Sign in')").first
        self.username_input = self.page.locator("input#userid, input#user")
        self.continue_btn = self.page.locator("button#signin-continue-btn, button#btn-continue, button:has-text('Continue')")
        self.password_input = self.page.locator("input#pass, input#password")
        self.login_btn = self.page.locator("button#sgnBt, button#login-btn, button:has-text('Sign in')")

    def login(self, username, password):
        self.navigate("https://www.ebay.com")
        
        # Check if already logged in by looking for the "Hi [Name]" greeting
        try:
            if self.page.locator("#gh-ug, .gh-identity__greeting").filter(has_text="Hi").is_visible(timeout=5000):
                self.logger.info("User already logged in. Skipping login steps.")
                return
        except:
            pass

        self.logger.info("Starting login process")
        if self.signin_link.is_visible():
            self.signin_link.click()
        else:
            self.logger.info("Sign in link not found on home page, navigating to signin page directly")
            self.page.goto("https://signin.ebay.com")
            
        # Check for splash CAPTCHA or Step-up verification
        current_url = self.page.url.lower()
        if "captcha" in current_url or "stepup" in current_url or "acctxs" in current_url:
            self.logger.warning(f"Verification or Step-up detected ({current_url})! Waiting for manual solution or timeout (2 mins)...")
            try:
                # Wait for any indicator that verification is done (e.g. navigation back to ebay or visible user input)
                self.page.wait_for_selector("input#userid, input#user, #gh-ug", timeout=120000)
                self.logger.info("Verification likely solved, continuing...")
            except:
                self.logger.error("Verification not solved in time. Failing.")
                raise Exception("Login blocked by verification")

        try:
            self.username_input.wait_for(state="visible", timeout=15000)
        except:
            self.logger.error("Username input not found. Might be blocked by CAPTCHA.")
            raise Exception("Login page not loaded correctly")
        self.page.wait_for_timeout(1000) 
        self.logger.info(f"Entering username: {username}")
        self.username_input.fill(username)
        self.page.wait_for_timeout(500)
        self.continue_btn.click()
        
        # Check for password field or another CAPTCHA
        try:
            self.password_input.wait_for(state="visible", timeout=10000)
            self.page.wait_for_timeout(1000)
            self.logger.info("Entering password")
            self.password_input.fill(password)
            self.page.wait_for_timeout(500)
            self.login_btn.click()
            self.logger.info("Login form submitted")
        except Exception as e:
            if "captcha" in self.page.url.lower() or "stepup" in self.page.url.lower():
                self.logger.warning("Verification screen detected during login flow! Waiting 30s...")
                self.page.wait_for_timeout(30000)
            self.logger.error(f"Login process failed. Current URL: {self.page.url}")
            self.logger.error(f"Exception details: {str(e)}")
            import traceback
            self.logger.debug(f"Full Traceback: {traceback.format_exc()}")
            raise e
