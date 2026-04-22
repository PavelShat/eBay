import json
import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
from pages.item_page import ItemPage
from pages.cart_page import CartPage

def load_test_data():
    with open("data/test_data.json") as f:
        return json.load(f)

@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.parametrize("data", load_test_data())
async def test_ebay_shopping_flow(page, data):
    # Initialize Page Objects mapped to Playwright's page fixture
    login_page = LoginPage(page)
    home_page = HomePage(page)
    search_page = SearchResultsPage(page)
    item_page = ItemPage(page)
    cart_page = CartPage(page)

    # 1. Authentication
    await login_page.login(data["username"], data["password"])
    
    # 2. Search Item
    await home_page.search_item(data["search_term"])

    # 3. Filter by price and select first item
    await search_page.filter_by_price(data["min_price"], data["max_price"])
    await search_page.select_first_item()

    # 4. Add to cart
    await item_page.add_to_cart()

    # 5. Assert amount (Passing items_count=1 as only one item was added in this flow)
    await cart_page.assert_cart_total_not_exceeds(float(data["max_price"]), 1)
