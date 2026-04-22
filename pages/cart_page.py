import allure
import re
from pages.base_page import BasePage

class CartPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.cart_total = self.page.locator("div[data-test-id='SUBTOTAL'] span.text-display-span")

    @allure.step("Verify Cart total does not exceed budget: ${budget_per_item} x {items_count} items")
    def assert_cart_total_not_exceeds(self, budget_per_item: float, items_count: int):
        """
        Calculates threshold (budget_per_item * items_count) and verifies against cart subtotal.
        Captures a trace and screenshot of the cart page.
        """
        # 1. Start Trace of the cart page state
        self.page.context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        try:
            # 2. Open the shopping cart
            self.navigate("https://cart.ebay.com/")
            max_limit = budget_per_item * items_count
            
            # 3. Read the subtotal/total amount
            self.cart_total.wait_for(state="visible", timeout=10000)
            total_text = self.cart_total.text_content() or "0"
            
            # 4. Extract numbers: $1,234.56 -> 1234.56
            numeric_str = re.sub(r'[^\d.]', '', total_text)
            total_amount = float(numeric_str) if numeric_str else 0.0
            
            # 5. Save Screenshot of the cart page
            screenshot = self.page.screenshot(full_page=True)
            allure.attach(
                screenshot, 
                name="Cart Total Verification Log", 
                attachment_type=allure.attachment_type.PNG
            )
            
            # 6. Verify that the total amount does not exceed the threshold
            assert total_amount <= max_limit, (
                f"Cart total ${total_amount} exceeds calculated limit of ${max_limit} "
                f"(${budget_per_item} per item x {items_count} items)"
            )
            
        except Exception as e:
            # Capture error state if something goes wrong
            error_screenshot = self.page.screenshot(full_page=True)
            allure.attach(error_screenshot, name="Cart Error State", attachment_type=allure.attachment_type.PNG)
            allure.attach(f"Could not verify cart total: {str(e)}", name="Cart Error Log", attachment_type=allure.attachment_type.TEXT)
            raise e
        finally:
            # 7. Stop and save trace
            trace_path = "cart_page_verification.zip"
            self.page.context.tracing.stop(path=trace_path)
            allure.attach.file(
                trace_path, 
                name="Cart Verification Trace"
            )
