import logging
from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage
from pages.item_page import ItemPage
from pages.cart_page import CartPage
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)8s] %(message)s')
logger = logging.getLogger(__name__)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Load data
        with open("data/test_data.json") as f:
            data = json.load(f)[0]
            
        login_page = LoginPage(page)
        item_page = ItemPage(page)
        cart_page = CartPage(page)
        
        # 1. Login
        logger.info("Logging in...")
        login_page.login(data["username"], data["password"])
        page.wait_for_timeout(5000)
        
        # 2. Clear Cart
        logger.info("Clearing cart...")
        cart_page.clear_cart()
        
        # 3. Add one item
        test_url = "https://www.ebay.com/itm/123209299640" # One of the socks URLs
        logger.info(f"Adding item: {test_url}")
        page.goto(test_url)
        item_page.add_to_cart()
        
        # 4. Verify
        logger.info("Verifying cart...")
        cart_page.verify_item_count(1)
        
        logger.info("Success!")
        browser.close()

if __name__ == "__main__":
    run()
