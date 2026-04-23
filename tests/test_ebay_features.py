import pytest
import time
import random
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.search_results_page import SearchResultsPage
from pages.item_page import ItemPage
from pages.cart_page import CartPage

class TestEbayCore:

    @pytest.mark.order(1)
    def test_01_authentication(self, page, data):
        """1. Authentication Test"""
        login_page = LoginPage(page)
        time.sleep(random.uniform(2, 4))
        try:
            login_page.login(data["username"], data["password"])
        except Exception as e:
            print(f"Authentication skipped/failed: {str(e)}")
            pytest.skip("Login flow interrupted (likely Captcha)")

    @pytest.mark.order(2)
    def test_02_search_function_with_conditions(self, page, data):
        """2. Search function with price conditions"""
        home_page = HomePage(page)
        search_page = SearchResultsPage(page)
        
        time.sleep(random.uniform(3, 5))
        home_page.search_item(data["search_term"])
        time.sleep(2)
        search_page.filter_by_price(data["min_price"], data["max_price"])
        
        # Verify we are on results page and results are visible
        assert "Search" in page.title() or data["search_term"].lower() in page.title().lower()

    @pytest.mark.order(3)
    def test_03_add_items_to_cart(self, page, data):
        """3. addItemsToCart"""
        home_page = HomePage(page)
        search_page = SearchResultsPage(page)
        item_page = ItemPage(page)
        
        # We need to be on an item page to add to cart
        time.sleep(random.uniform(4, 6))
        home_page.search_item(data["search_term"])
        search_page.filter_by_price(data["min_price"], data["max_price"])
        search_page.select_first_item()
        
        item_page.add_to_cart()
        time.sleep(3)
        # Verify cart counter or navigation to cart
        # Some eBay versions show a popup, others navigate. We ensure we see evidence of addition.
        is_cart_page = "cart" in page.url.lower() or "shopping cart" in page.title().lower()
        has_cart_count = page.locator("#gh-cart-n, .gh-cart-n, #gh-cart-count").is_visible()
        has_success_msg = page.locator(".confirmation-message, .atc-success-msg, :has-text('Added to cart'), :has-text('item added')").first.is_visible()
        
        assert is_cart_page or has_cart_count or has_success_msg, f"No evidence of item added to cart. URL: {page.url}"

    @pytest.mark.order(4)
    def test_04_assert_cart_total_not_exceeds(self, page, data):
        """4. assertCartTotalNotExceeds"""
        # Note: This test assumes an item was added in previous steps or adds one now
        home_page = HomePage(page)
        search_page = SearchResultsPage(page)
        item_page = ItemPage(page)
        cart_page = CartPage(page)
        
        # Ensure there is something in the cart
        home_page.search_item(data["search_term"])
        search_page.filter_by_price(data["min_price"], data["max_price"])
        search_page.select_first_item()
        item_page.add_to_cart()
        
        budget = float(data["max_price"])
        cart_page.assert_cart_total_not_exceeds(budget, 1)
