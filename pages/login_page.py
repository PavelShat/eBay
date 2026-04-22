import allure
from pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.signin_link = self.page.locator("a[href*='signin'], a:has-text('Sign in')").first
        self.username_input = self.page.locator("input#userid, input#user")
        self.continue_btn = self.page.locator("button#signin-continue-btn, button#btn-continue, button:has-text('Continue')")
        self.password_input = self.page.locator("input#pass, input#password")
        self.login_btn = self.page.locator("button#sgnBt, button#login-btn, button:has-text('Sign in')")

    @allure.step("Navigate to Sign-In page and enter credentials")
    def login(self, username, password):
        self.navigate("https://www.ebay.com")
        if self.signin_link.is_visible():
            self.signin_link.click()
        else:
            self.page.goto("https://signin.ebay.com")
            
        self.username_input.wait_for(state="visible", timeout=10000)
        self.username_input.fill(username)
        self.continue_btn.click()
        
        # Soft wait for password field as eBay might show a Captcha here
        try:
            self.password_input.wait_for(state="visible", timeout=5000)
            self.password_input.fill(password)
            self.login_btn.click()
        except Exception:
            allure.attach("Login flow interrupted (Captcha or security check likely)", name="Login Status")
            print("Warning: Login was interrupted. Test will continue as guest if possible.")
