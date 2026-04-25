import pytest
from pages.search_results_page import SearchResultsPage
from pages.item_page import ItemPage
from pages.cart_page import CartPage

@pytest.mark.e2e
@pytest.mark.order(5)
def test_full_scenario_verification(page, data):
    """
    Full Scenario Example:
    1. searchItemsByNameUnderPrice("shoes", 220, 5)
    2. addItemsToCart(urls)
    3. assertCartTotalNotExceeds(220, urls.length)
    """
    search_page = SearchResultsPage(page)
    item_page = ItemPage(page)
    cart_page = CartPage(page)

    search_term = "shoes"
    budget_per_item = 220
    items_count = 5

    print(f"\n--- Starting Full Scenario: {search_term} under ${budget_per_item} ---", flush=True)

    # 1. searchItemsByNameUnderPrice("shoes", 220, 5)
    urls = search_page.search_items_by_name_under_price(search_term, budget_per_item, items_count)
    print(f"Found {len(urls)} items to add.", flush=True)
    assert len(urls) > 0, "No items found for the specific criteria"

    # 2. addItemsToCart(urls)
    item_page.add_items_to_cart(urls)

    # 3. assertCartTotalNotExceeds(220, urls.length)
    cart_page.assert_cart_total_not_exceeds(budget_per_item, len(urls))
