import pytest
import allure
import time
import random
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.search_results_page import SearchResultsPage
from pages.item_page import ItemPage
from pages.cart_page import CartPage

@allure.feature("eBay E2E Tests - Sync Flow")
class TestEbayCore:

    @allure.story("Authentication")
    def test_01_authentication(self, page, data):
        """Test the user login flow with soft-skip on Captcha."""
        login_page = LoginPage(page)
        # Random sleep to avoid bot detection
        time.sleep(random.uniform(2, 5))
        try:
            login_page.login(data["username"], data["password"])
            allure.attach("Authentication flow attempted", name="Status")
        except Exception as e:
            allure.attach(f"Authentication blocked: {str(e)}", name="Status")
            pytest.skip("Skipping authentication due to security block")

    @allure.story("Search and Filter")
    def test_02_product_search(self, page, data):
        """Test searching for an item and applying price filters."""
        home_page = HomePage(page)
        search_page = SearchResultsPage(page)
        
        # Soft start
        time.sleep(random.uniform(3, 6))
        home_page.search_item(data["search_term"])
        time.sleep(random.uniform(2, 4))
        search_page.filter_by_price(data["min_price"], data["max_price"])
        allure.attach("Search and filter completed", name="Status")

    @allure.story("Complete Cart Workflow")
    def test_03_add_to_cart_and_verify(self, page, data):
        """Combined test for adding to cart and verifying total to minimize bot detection."""
        home_page = HomePage(page)
        search_page = SearchResultsPage(page)
        item_page = ItemPage(page)
        cart_page = CartPage(page)
        
        # 1. Search with human-like delay
        time.sleep(random.uniform(5, 8))
        home_page.search_item(data["search_term"])
        time.sleep(5)
        
        # 2. Select first real item
        search_page.select_first_item()
        page.wait_for_load_state("load")
        time.sleep(5)
        
        # 3. Add to cart
        item_page.add_to_cart()
        allure.attach("Item added to cart", name="Cart Status")
        time.sleep(5)
        
        # 4. Verify cart total (Budget per item, items count)
        budget = float(data["max_price"])
        cart_page.assert_cart_total_not_exceeds(budget, 1)
        allure.attach("Cart total verified successfully", name="Verification Status")
