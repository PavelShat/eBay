from playwright.sync_api import Page
from pages.base_page import BasePage

class HomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input = self.page.locator("input#gh-ac, input[aria-label='Search for anything']")
        self.search_btn = self.page.locator("input#gh-btn, button#gh-search-btn, #gh-btn")

    def search_item(self, term: str):
        self.navigate("https://www.ebay.com")
        self.search_input.fill(term)
        self.search_btn.click()
