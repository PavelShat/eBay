import logging
import random
import os
import re
from pages.base_page import BasePage

class ItemPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Use a text-based locator for maximum reliability across eBay variants
        # We specifically look for "Add to cart" or "Add to basket"
        # Flexible locator for the main action button
        # Targets 'Add to cart', 'Add to basket', and 'See in cart' (if already added)
        self.add_to_cart_btn = self.page.locator("a#atcBtn_btn_1, button#atcBtn_btn_1, [data-testid='x-atc-action'] button, [data-testid='x-atc-action'] a, #isCartBtn_btn").filter(has_text=re.compile(r"Add to (cart|basket)|See in cart", re.IGNORECASE)).first

    def add_to_cart(self):
        # 0. Check if already in cart (eBay changes button text to 'See in cart')
        try:
            btn_text = (self.add_to_cart_btn.text_content() or "").strip()
            if "See in cart" in btn_text:
                self.logger.info("Item already in cart ('See in cart'). Skipping addition.")
                return
        except:
            pass
        # Capture initial cart count
        try:
            initial_count_text = self.page.locator("#gh-cart-n, .gh-cart-n").first.text_content() or "0"
            initial_count = int(re.sub(r'\D', '', initial_count_text))
        except:
            initial_count = 0

        # 1. Try to handle any mandatory variants
        self.logger.info("Checking for mandatory variants...")
        
        # Max attempts to handle variants as they might be dependent
        for attempt in range(5):
            # Refresh list of variant buttons each time
            # We specifically look within the main item section and exclude header/footer
            variant_buttons = self.page.locator("#mainContent .listbox-button__control, #mainContent button[id*='msku'], #mainContent select:not(#gh-cat), #mainContent [data-testid='x-skulist-action'], #mainContent [data-testid='x-condition-action']").all()
            found_unselected = False
            
            for btn in variant_buttons:
                try:
                    if not btn.is_visible(timeout=500):
                        continue
                    
                    btn_text = (btn.text_content() or "").strip().lower()
                    # Skip if it looks like it's already selected (eBay often puts the value in the button text)
                    if "select" not in btn_text and ":" in btn_text:
                        continue
                        
                    found_unselected = True
                    tag_name = btn.evaluate("node => node.tagName").lower()
                    self.logger.info(f"Handling variant: {btn_text} ({tag_name})")
                    
                    if tag_name == "select":
                        options = btn.locator("option").all()
                        valid = [o.get_attribute("value") for o in options if o.get_attribute("value") and o.get_attribute("value") not in ("-1", "0")]
                        if valid:
                            idx = min(2, len(valid) - 1)
                            val = valid[idx]
                            self.logger.info(f"Selecting option {idx+1}: {val}")
                            btn.select_option(value=val)
                            self.page.wait_for_load_state("networkidle")
                            self.page.wait_for_timeout(2000)
                    else:
                        # Click to open dropdown/listbox
                        btn.click()
                        self.page.wait_for_timeout(1500)
                        
                        # Broad search for options in the popover/listbox
                        options = self.page.locator("[role='option'], .x-msku__select-box li, .listbox-button__list li, [data-testid='x-dropdown-option']").all()
                        valid = [o for o in options if o.is_visible() and o.get_attribute("aria-disabled") != "true" and "Select" not in (o.text_content() or "")]
                        
                        if valid:
                            idx = min(2, len(valid) - 1)
                            choice = valid[idx]
                            self.logger.info(f"Selecting choice {idx+1}: {choice.text_content().strip()}")
                            choice.click(force=True)
                            self.page.wait_for_load_state("networkidle")
                            self.page.wait_for_timeout(2000)
                        else:
                            self.page.keyboard.press("Escape")
                            self.page.wait_for_timeout(500)
                except Exception as e:
                    self.logger.debug(f"Variant interaction error: {e}")
                    continue
            
            if not found_unselected:
                break
            
            # Check if we navigated away
            if "/itm/" not in self.page.url:
                self.page.go_back()
                self.page.wait_for_load_state("load")

        # Attempt selection with fallback logic
        # try_indices = [2, 1, 0] # Try 3rd, then 2nd, then 1st
        
        # We already picked one above. Let's refine the loop to be more adaptive.
        # Actually, let's just make sure the 'Add to cart' button is enabled.
        # If not, we iterate through options for the LAST handled variant.
        
        self.logger.info("Looking for 'Add to cart' button...")
        self.add_to_cart_btn.scroll_into_view_if_needed()
        self.add_to_cart_btn.wait_for(state="visible", timeout=15000)
        
        # Check if button is enabled. If not, try to change the last selection.
        for _ in range(3): # Try a few fallbacks if disabled
            is_enabled = self.add_to_cart_btn.first.is_enabled()
            
            if is_enabled:
                break
                
            self.logger.warning("Button is disabled. Trying a different variant combination...")
            # Pick a different option for the first mandatory variant we find
            variant_buttons = self.page.locator("#mainContent .listbox-button__control, #mainContent button[id*='msku'], #mainContent select:not(#gh-cat), #mainContent [data-testid='x-skulist-action'], #mainContent [data-testid='x-condition-action']").all()
            for btn in variant_buttons:
                if btn.is_visible():
                    # Just pick the first available one as fallback
                    tag_name = btn.evaluate("node => node.tagName").lower()
                    if tag_name == "select":
                        options = btn.locator("option").all()
                        valid = [o.get_attribute("value") for o in options if o.get_attribute("value") and o.get_attribute("value") not in ("-1", "0")]
                        if valid:
                            btn.select_option(value=valid[0])
                            self.page.wait_for_timeout(1000)
                    else:
                        btn.click()
                        self.page.wait_for_timeout(500)
                        options = self.page.locator(".x-msku__select-box [role='option'], .listbox-button__list [role='option'], .x-listbox__option").all()
                        valid = [o for o in options if o.is_visible() and o.get_attribute("aria-disabled") != "true"]
                        if valid:
                            valid[0].click(force=True)
                            self.page.wait_for_timeout(1000)
                    break # Only change one at a time
        
        btn_text = self.add_to_cart_btn.text_content().strip()
        self.logger.info(f"Clicking: {btn_text}")
        try:
             self.add_to_cart_btn.click(timeout=5000)
        except:
             self.add_to_cart_btn.click(force=True)
        
        # 3. Verify addition by checking cart count change or navigation
        # We wait up to 10 seconds for the counter to increment
        self.logger.info("Verifying addition...")
        for i in range(10):
            self.page.wait_for_timeout(1000)
            try:
                cart_badge = self.page.locator("#gh-cart-n, .gh-cart-n").first
                if cart_badge.is_visible(timeout=500):
                    current_count_text = cart_badge.text_content() or "1"
                    current_count = int(re.sub(r'\D', '', current_count_text))
                    if current_count > initial_count:
                        self.logger.info(f"Success: Cart count increased to {current_count}")
                        break
            except:
                pass
            
            # Also check if we navigated to cart or saw a success message
            if "cart" in self.page.url.lower() or self.page.locator(".atc-overlay, :has-text('item added')").first.is_visible(timeout=500):
                self.logger.info("Success: Navigated to cart or saw confirmation.")
                break
            if i == 9:
                self.logger.warning("Could not verify addition via count or overlay.")
        
        # 4. Handle 'Go to cart' side panel or navigation
        try:
            # Added 'See in cart' which is a common eBay variant
            cart_selectors = [
                "a:has-text('See in cart')",
                "a:has-text('Go to cart')", 
                "button:has-text('Go to cart')",
                "[data-test-id='view-cart']",
                ".atc-overlay-view-cart",
                "a[href*='cart']"
            ]
            
            self.logger.info("Checking for cart navigation buttons...")
            for selector in cart_selectors:
                btn = self.page.locator(selector).first
                if btn.is_visible(timeout=2000):
                    self.logger.info(f"Found navigation button: {selector}")
                    btn.click()
                    self.page.wait_for_load_state("networkidle")
                    return # Exit early if we successfully navigated
        except:
            pass

    def add_items_to_cart(self, urls: list):
        """
        Navigates to multiple item URLs, adds each to the cart, and returns to search.
        Saves a screenshot for each item added and attaches it to Report Portal.
        """
        for idx, url in enumerate(urls, 1):
            self.logger.info(f"[{idx}/{len(urls)}] Adding item to cart: {url}")
            self.page.goto(url)
            self.page.wait_for_load_state("load")
            
            # Add to cart handles variants and clicking the button
            self.add_to_cart()
            
            # Save screenshot of the added item
            screenshot_bytes = self.page.screenshot()
            
            # Attach to ReportPortal
            try:
                from reportportal_client import RPLogger
                rp_logger = logging.getLogger("reportportal_client")
                if isinstance(rp_logger, RPLogger):
                    rp_logger.info(
                        f"Item {idx} added to cart",
                        attachment={
                            "name": f"added_item_{idx}.png",
                            "data": screenshot_bytes,
                            "mime": "image/png",
                        },
                    )
            except ImportError:
                pass

            # Save locally as fallback
            os.makedirs("reports", exist_ok=True)
            screenshot_path = f"reports/added_item_{idx}.png"
            with open(screenshot_path, "wb") as f:
                f.write(screenshot_bytes)
            self.logger.info(f"Saved screenshot to {screenshot_path}")
            
            # Return to the search screen
            self.logger.info("Returning to search results...")
            self.page.go_back()
            # If we are still on item page (e.g. because of redirects), go back again
            if "itm/" in self.page.url:
                self.page.go_back()
            self.page.wait_for_timeout(1000)
