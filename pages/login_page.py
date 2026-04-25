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
                print("User already logged in. Skipping login steps.", flush=True)
                return
        except:
            pass

        if self.signin_link.is_visible():
            self.signin_link.click()
        else:
            self.page.goto("https://signin.ebay.com")
            
        self.username_input.wait_for(state="visible", timeout=10000)
        self.page.wait_for_timeout(1000) # Small human-like delay
        self.username_input.type(username, delay=100) # Type like a human
        self.page.wait_for_timeout(500)
        self.continue_btn.click()
        
        # Soft wait for password field as eBay might show a Captcha here
        try:
            self.password_input.wait_for(state="visible", timeout=5000)
            self.page.wait_for_timeout(1000)
            self.password_input.type(password, delay=100)
            self.page.wait_for_timeout(500)
            self.login_btn.click()
        except Exception as e:
            print(f"Warning: Login was interrupted. Reason: {repr(e)}. Test will continue as guest if possible.")
