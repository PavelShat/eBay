import logging
from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)

    def navigate(self, url: str):
        self.logger.info(f"Navigating to {url}")
        self.page.goto(url)

    def wait_for_load(self):
        self.page.wait_for_load_state("networkidle")
