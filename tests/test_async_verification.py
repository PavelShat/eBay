import pytest
import allure
from pages.search_results_page import SearchResultsPage
from pages.item_page import ItemPage
from pages.cart_page import CartPage

@pytest.mark.e2e
@pytest.mark.asyncio
@allure.feature("Async Cart Verification")
@allure.story("Verify Multiple Items Budget")
async def test_assert_cart_total_not_exceeds_scenario(page):
    search_page = SearchResultsPage(page)
    item_page = ItemPage(page)
    cart_page = CartPage(page)

    search_term = "shoes"
    budget_per_item = 220
    items_count = 5

    allure.dynamic.title(f"Scenario: {items_count} items under ${budget_per_item}")

    # 1. searchItemsByNameUnderPrice("shoes", 220, 5)
    urls = await search_page.search_items_by_name_under_price(search_term, budget_per_item, items_count)
    assert len(urls) > 0, "No items found for the specific criteria"
    allure.attach(f"Found {len(urls)} items: {', '.join(urls)}", name="Found URLs")

    # 2. addItemsToCart(urls)
    await item_page.add_items_to_cart(urls)

    # 3. assertCartTotalNotExceeds(220, urls.length)
    # This method contains the requested tracing and screenshot logic
    await cart_page.assert_cart_total_not_exceeds(budget_per_item, len(urls))
