import re
import allure
import random
from pages.base_page import BasePage

class SearchResultsPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.search_btn = self.page.locator("button#gh-search-btn, input#gh-btn, .gh-spr, #gh-btn")
        self.min_price_input = self.page.locator("input[aria-label*='Minimum'], input[placeholder*='min']")
        self.max_price_input = self.page.locator("input[aria-label*='Maximum'], input[placeholder*='max']")
        # Broadest possible selector for item links, using multiple common eBay classes
        self.item_links = self.page.locator(".s-item a.s-item__link[href*='/itm/'], .s-card__link[href*='/itm/'], a.s-item__link[href*='/itm/']")

    @allure.step("Filter by price range: ${min_price} - ${max_price}")
    def filter_by_price(self, min_price: str, max_price: str):
        self.min_price_input.first.wait_for(state="visible", timeout=15000)
        self.min_price_input.first.fill(min_price)
        self.max_price_input.first.fill(max_price)
        self.max_price_input.first.press("Enter")
        # Use a soft wait for navigation and load
        self.page.wait_for_load_state("load")
        self.page.wait_for_timeout(2000)

    @allure.step("Select the first real item with a valid ID")
    def select_first_item(self):
        """
        Extracts a valid product URL by verifying it contains a 10-12 digit item ID.
        """
        # Wait for any item container or link to appear
        try:
            self.page.wait_for_selector(".s-item, .s-card__link, a.s-item__link", state="attached", timeout=30000)
        except Exception:
            allure.attach(self.page.content(), name="failure_page_source", attachment_type=allure.attachment_type.HTML)
            raise

        # Give it a moment to render
        self.page.wait_for_timeout(2000)
        
        # Get all potential item links
        links = self.item_links.all()
        target_href = None
        
        for link in links:
            href = link.get_attribute("href")
            # Items often have a 10-13 digit ID. 
            if href and re.search(r'\d{10,}', href):
                # Ensure it's not a placeholder/template link
                if "123456" not in href and "product" not in href.lower():
                    target_href = href
                    if target_href.startswith("/"):
                        target_href = "https://www.ebay.com" + target_href
                    break
        
        if not target_href:
             # Fallback: take the first link that has /itm/
             all_itm_links = self.page.locator("a[href*='/itm/']").all()
             for l in all_itm_links:
                 h = l.get_attribute("href")
                 if h and "123456" not in h:
                     target_href = h
                     if target_href.startswith("/"):
                         target_href = "https://www.ebay.com" + target_href
                     break

        if not target_href:
            raise Exception("Could not find any valid item links on the search results page.")

        allure.attach(f"Navigating directly to item: {target_href}", name="Navigation Info")
        self.page.goto(target_href)
        self.page.wait_for_load_state("load")
        self.page.wait_for_timeout(2000)
