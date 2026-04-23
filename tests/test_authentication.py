import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage

@pytest.mark.e2e
def test_authentication(page, data):
    """
    Test successful login and verification of user greeting.
    """
    login_page = LoginPage(page)
    home_page = HomePage(page)

    # 1. Perform Login
    login_page.login(data["username"], data["password"])
    
    # 2. Verify User Greeting on Home Page
    # eBay usually displays "Hi [Name]!" or similar
    try:
        # Increase timeout and use a more specific wait
        print(f"Current URL after login attempt: {page.url}")
        page.wait_for_selector("#gh-ug, #gh-eb-u, .gh-identity__greeting", timeout=20000)
        
        greeting = home_page.get_user_greeting()
        print(f"Detected Greeting: {greeting}")
        
        # Extract name from email if needed (e.g. pavel.shataylo -> pavel)
        expected_part = data["username"].split('.')[0].lower()
        
        if "Sign in" in greeting:
             # Capture page state before failing
             print(f"FAILED: Still at {page.url} with title {page.title()}")
             pytest.fail(f"Login failed: Still seeing 'Sign in' link at {page.url}")
            
        assert "Hi" in greeting or expected_part in greeting.lower(), \
            f"Greeting '{greeting}' does not seem to belong to user '{data['username']}'"
            
    except Exception as e:
        print(f"EXCEPTION at {page.url} with title '{page.title()}': {str(e)}")
        # Dump header HTML for debugging
        try:
            header_html = page.locator("header").inner_html()
            print(f"HEADER HTML: {header_html[:1500]}") # Print first 1500 chars
        except Exception as inner_e:
            print(f"Could not get header HTML: {inner_e}")
            
        if "captcha" in page.url.lower() or "verify" in page.url.lower():
             pytest.skip(f"Test blocked by verification/CAPTCHA at {page.url}")
        else:
             raise e
