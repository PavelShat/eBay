import allure
from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        with allure.step(f"Navigate to {url}"):
            self.page.goto(url)

    def wait_for_load(self):
        with allure.step("Wait for page to load"):
            self.page.wait_for_load_state("networkidle")
