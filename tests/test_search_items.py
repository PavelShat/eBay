import pytest
from pages.search_results_page import SearchResultsPage

@pytest.mark.e2e
def test_search_items(page, data):
    """
    Test searching for an item with specific price conditions using XPath and pagination.
    Retrieves up to 5 items that are <= maxPrice.
    """
    search_page = SearchResultsPage(page)
    
    # Extract data from test_data.json
    search_term = data["search_term"]
    min_price = data["min_price"]
    max_price = float(data["max_price"])
    limit = 5
    
    print(f"\nSearching for: '{search_term}' with Max Price: ${max_price}")
    
    # Execute the search_by_query method
    # Let's intercept to save a screenshot
    urls = search_page.search_by_query(
        query=search_term,
        maxPrice=max_price,
        limit=limit,
        minPrice=min_price
    )
    
    page.screenshot(path="debug_search.png", full_page=True)
    with open("debug_search.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    
    print(f"Found {len(urls)} items matching criteria.")
    for idx, url in enumerate(urls, 1):
        print(f"{idx}. {url}")
    
    # Assertions
    # If there are items, we should have retrieved at least some (though 0 is also OK per requirements)
    # The length should not exceed the limit
    assert len(urls) <= limit, f"Expected at most {limit} items, but got {len(urls)}"
    
    # We can ensure it's returning a list of URLs
    assert isinstance(urls, list), "Expected return value to be a list"
    if len(urls) > 0:
        assert all("ebay.com" in url for url in urls), "Returned items should contain valid eBay URLs"
