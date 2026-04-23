import re
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

    def filter_by_price(self, min_price: str, max_price: str):
        self.min_price_input.first.wait_for(state="visible", timeout=15000)
        self.min_price_input.first.fill(min_price)
        self.max_price_input.first.fill(max_price)
        self.max_price_input.first.press("Enter")
        # Use a soft wait for navigation instead of load
        self.page.wait_for_timeout(3000)

    def select_first_item(self):
        """
        Extracts a valid product URL by verifying it contains a 10-12 digit item ID.
        """
        # Wait for any item container or link to appear
        try:
            self.page.wait_for_selector(".s-item, .s-card__link, a.s-item__link", state="attached", timeout=30000)
        except Exception:
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

        print(f"Navigating directly to item: {target_href}")
        self.page.goto(target_href)
        self.page.wait_for_load_state("load")
        self.page.wait_for_timeout(2000)

    def search_items_by_name_under_price(self, name: str, max_price: float, count: int):
        """
        Searches for items and returns a list of URLs for items under the max_price.
        """
        self.page.goto("https://www.ebay.com")
        search_input = self.page.locator("input#gh-ac, input[aria-label='Search for anything']")
        search_btn = self.page.locator("input#gh-btn, button#gh-search-btn, #gh-btn")
        
        search_input.wait_for(state="visible", timeout=15000)
        search_input.fill(name)
        search_btn.click()
        
        # Filter by price
        self.filter_by_price("0", str(max_price))
        
        # Collect links - using multiple possible selectors for eBay items
        self.page.wait_for_selector(".s-item__link, .s-item a, .s-card__link", state="attached", timeout=15000)
        self.page.wait_for_timeout(2000) # Wait for results to settle
        
        links = self.item_links.all()
        urls = []
        
        for link in links:
            try:
                href = link.get_attribute("href")
                if href and re.search(r'\d{10,}', href) and "123456" not in href:
                    if href.startswith("/"):
                        href = "https://www.ebay.com" + href
                    if href not in urls: # Avoid duplicates
                        urls.append(href)
                if len(urls) >= count:
                    break
            except:
                continue
        return urls

    def search_by_query(self, query: str, maxPrice: float, limit: int = 5, minPrice: str = "0"):
        """
        Uses XPath to retrieve the first `limit` items whose price is <= `maxPrice`.
        Handles pagination if fewer than `limit` items are found on the first page.
        """
        # 1. Search for the query
        self.page.goto("https://www.ebay.com")
        search_input = self.page.locator("input#gh-ac, input[aria-label='Search for anything']")
        search_btn = self.page.locator("input#gh-btn, button#gh-search-btn, #gh-btn")
        
        search_input.wait_for(state="visible", timeout=15000)
        search_input.fill(query)
        search_btn.click()
        
        # 2. Filter by price
        self.filter_by_price(minPrice, str(maxPrice))
        
        # 3. XPath logic to collect items
        collected_urls = []
        page_num = 1
        max_pages = 5
        
        while len(collected_urls) < limit and page_num <= max_pages:
            print(f"--- Collecting items on page {page_num}, currently have {len(collected_urls)} ---", flush=True)
            self.page.wait_for_timeout(3000)
            
            try:
                # Wait for at least one price element to appear indicating items loaded
                self.page.wait_for_selector("xpath=//*[contains(@class, 's-item__price')]", timeout=15000)
            except Exception as e:
                print(f"Items not visible: {e}", flush=True)
                
            # Use XPath to find all item containers on the page
            item_elements = self.page.locator("xpath=//*[contains(@class, 's-item') or contains(@class, 's-card')]").all()
            print(f"Found {len(item_elements)} item containers on page", flush=True)
            
            for item in item_elements:
                if len(collected_urls) >= limit:
                    break
                    
                try:
                    price_element = item.locator("xpath=.//*[contains(@class, 's-item__price') or contains(@class, 's-card__price')]")
                    if price_element.count() == 0:
                        continue
                        
                    price_text = price_element.first.text_content()
                    match = re.search(r'\$?([\d,.]+)', price_text)
                    if match:
                        numeric_str = match.group(1).replace(',', '')
                        item_price = float(numeric_str)
                        
                        if item_price <= maxPrice:
                            link_element = item.locator("xpath=.//a[contains(@class, 's-item__link') or contains(@class, 's-card__link')]")
                            if link_element.count() > 0:
                                href = link_element.first.get_attribute("href")
                                if href and "123456" not in href and "product" not in href.lower():
                                    if href.startswith("/"):
                                        href = "https://www.ebay.com" + href
                                    if href not in collected_urls:
                                        collected_urls.append(href)
                                        print(f"Added item: ${item_price} - {href[:50]}...", flush=True)
                except Exception as e:
                    print(f"Error parsing item: {e}", flush=True)
                    continue
            
            if len(collected_urls) >= limit:
                break
                
            print(f"Need more items (have {len(collected_urls)} of {limit}), looking for next page...", flush=True)
            next_btn = self.page.locator("xpath=//a[contains(@class, 'pagination__next')]")
            if next_btn.count() > 0 and next_btn.first.is_visible():
                is_disabled = next_btn.first.get_attribute("aria-disabled")
                if is_disabled == "true":
                    print("Next button is disabled. Stopping.", flush=True)
                    break
                print("Navigating to next page...", flush=True)
                next_btn.first.click()
                self.page.wait_for_timeout(3000)
                page_num += 1
            else:
                print("No visible Next button found. Stopping.", flush=True)
                break
                
        return collected_urls

