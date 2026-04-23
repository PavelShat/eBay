import random
from pages.base_page import BasePage

class ItemPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Expanded list of possible selectors for the 'Add to cart' button across all eBay locales/UI versions
        self.add_to_cart_btn = self.page.locator("#atcBtn_btn_1, #isCartBtn_btn, #atcRedesignId_btn, [id*='atc'], [data-testid*='atc'], span:has-text('Add to cart')").first

    def add_to_cart(self):
        # 1. Try to handle any mandatory variants that might block the 'Add to cart' button
        try:
            # Look for all buttons that might be listboxes
            variant_buttons = self.page.locator(".listbox-button__control, button[id*='msku'], select").all()
            for btn in variant_buttons:
                if btn.is_visible() and btn.is_enabled():
                    if btn.tag_name() == "select":
                        options = btn.locator("option").all()
                        valid = [o.get_attribute("value") for o in options if o.get_attribute("value") and o.get_attribute("value") not in ("-1", "0")]
                        if valid:
                            btn.select_option(value=random.choice(valid))
                            self.page.wait_for_timeout(1000)
                    else:
                        btn.click(force=True)
                        self.page.wait_for_timeout(500)
                        options = self.page.locator("[role='option'], .listbox-button__list-item").all()
                        valid = [o for o in options if o.is_visible() and o.get_attribute("aria-disabled") != "true" and "Select" not in (o.text_content() or "")]
                        if valid:
                            random.choice(valid).click(force=True)
                            self.page.wait_for_timeout(1000)
                        else:
                            self.page.keyboard.press("Escape")
        except:
            pass

        # 2. Click Add to cart
        self.add_to_cart_btn.wait_for(state="visible", timeout=15000)
        self.add_to_cart_btn.click(force=True)
        
        # 3. Handle 'Go to cart' or 'No thanks' popups that might appear after adding
        self.page.wait_for_load_state("load")
        self.page.wait_for_timeout(2000)
        
        # Optionally click 'Go to cart' if it's visible to ensure we are on the cart page for assertions
        try:
            go_to_cart_btn = self.page.locator("a:has-text('Go to cart'), button:has-text('Go to cart'), [data-test-id='view-cart']").first
            if go_to_cart_btn.is_visible(timeout=3000):
                go_to_cart_btn.click()
                self.page.wait_for_load_state("load")
        except:
            pass

    def add_items_to_cart(self, urls: list):
        """
        Navigates to multiple item URLs and adds each to the cart.
        """
        for url in urls:
            print(f"Adding item to cart: {url}")
            self.page.goto(url)
            self.page.wait_for_load_state("load")
            self.add_to_cart()
