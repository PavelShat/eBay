import re
from pages.base_page import BasePage

class CartPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.cart_total = self.page.locator("div[data-test-id='SUBTOTAL'] span.text-display-span")

    def assert_cart_total_not_exceeds(self, budget_per_item: float, items_count: int):
        """
        Calculates threshold (budget_per_item * items_count) and verifies against cart subtotal.
        """
        try:
            # Open the shopping cart
            self.navigate("https://cart.ebay.com/")
            max_limit = budget_per_item * items_count
            
            # Read the subtotal/total amount
            self.cart_total.wait_for(state="visible", timeout=10000)
            total_text = self.cart_total.text_content() or "0"
            
            # Extract numbers: $1,234.56 -> 1234.56
            numeric_str = re.sub(r'[^\d.]', '', total_text)
            total_amount = float(numeric_str) if numeric_str else 0.0
            
            # Verify that the total amount does not exceed the threshold
            assert total_amount <= max_limit, (
                f"Cart total ${total_amount} exceeds calculated limit of ${max_limit} "
                f"(${budget_per_item} per item x {items_count} items)"
            )
            
        except Exception as e:
            print(f"Could not verify cart total: {str(e)}")
            raise e
