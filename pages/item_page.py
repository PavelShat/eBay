import random
import os
import re
from pages.base_page import BasePage

class ItemPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Use a text-based locator for maximum reliability across eBay variants
        # We specifically look for "Add to cart" or "Add to basket"
        self.add_to_cart_btn = self.page.locator("a, button").filter(has_text=re.compile(r"^(Add to cart|Add to basket)$", re.IGNORECASE)).first

    def add_to_cart(self):
        # Capture initial cart count
        try:
            initial_count_text = self.page.locator("#gh-cart-n, .gh-cart-n").first.text_content() or "0"
            initial_count = int(re.sub(r'\D', '', initial_count_text))
        except:
            initial_count = 0

        # 1. Try to handle any mandatory variants
        # ... (variant logic same as before)
        try:
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
        self.add_to_cart_btn.scroll_into_view_if_needed()
        self.add_to_cart_btn.wait_for(state="visible", timeout=15000)
        
        btn_text = self.add_to_cart_btn.text_content().strip()
        print(f"Clicking specific button: {btn_text}", flush=True)
        
        try:
             self.add_to_cart_btn.click(timeout=5000)
        except:
             self.add_to_cart_btn.click(force=True)
        
        # 3. Verify addition by checking cart count change or navigation
        # We wait up to 10 seconds for the counter to increment
        for _ in range(10):
            self.page.wait_for_timeout(1000)
            try:
                current_count_text = self.page.locator("#gh-cart-n, .gh-cart-n").first.text_content() or "0"
                current_count = int(re.sub(r'\D', '', current_count_text))
                if current_count > initial_count:
                    print(f"Success: Cart count increased from {initial_count} to {current_count}", flush=True)
                    break
            except:
                pass
            
            # Also check if we navigated to cart or saw a success message
            if "cart" in self.page.url.lower() or self.page.locator(".atc-overlay, :has-text('item added')").first.is_visible():
                print("Success: Navigated to cart or saw confirmation message.", flush=True)
                break
        
        # 4. Handle 'Go to cart' side panel or navigation
        try:
            cart_selectors = [
                "a:has-text('Go to cart')", 
                "button:has-text('Go to cart')",
                "[data-test-id='view-cart']",
                ".atc-overlay-view-cart",
                "a[href*='cart']"
            ]
            
            for selector in cart_selectors:
                btn = self.page.locator(selector).first
                if btn.is_visible():
                    btn.click()
                    self.page.wait_for_load_state("networkidle")
                    break
        except:
            pass

    def add_items_to_cart(self, urls: list):
        """
        Navigates to multiple item URLs, adds each to the cart, and returns to search.
        Saves a screenshot for each item added.
        """
        for idx, url in enumerate(urls, 1):
            print(f"[{idx}/{len(urls)}] Adding item to cart: {url}", flush=True)
            self.page.goto(url)
            self.page.wait_for_load_state("load")
            
            # Add to cart handles variants and clicking the button
            self.add_to_cart()
            
            # Save screenshot of the added item
            screenshot_path = f"reports/added_item_{idx}.png"
            os.makedirs("reports", exist_ok=True)
            self.page.screenshot(path=screenshot_path)
            print(f"Saved screenshot to {screenshot_path}", flush=True)
            
            # Return to the search screen
            # Re-navigating to the search results might be more stable than go_back()
            # if multiple redirects happened.
            print("Returning to search results...", flush=True)
            self.page.go_back()
            # If we are still on item page (e.g. because of redirects), go back again
            if "itm/" in self.page.url:
                self.page.go_back()
            self.page.wait_for_timeout(1000)
