import logging
from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)

    def navigate(self, url: str):
        self.logger.info(f"Navigating to {url}")
        self.page.goto(url)
        self.handle_popups()

    def handle_popups(self):
        """
        Attempts to close common eBay promotional overlays and pop-ups.
        """
        popup_selectors = [
            "button.shale-overlay-close",
            "button[aria-label='Close']",
            ".shale-overlay-container button",
            ".survey-popup-close",
            ".coupon-popup-close",
            ".lightbox-close",
            "#shale-overlay-container .close-button",
            "button:has-text('Maybe later')",
            "button:has-text('No thanks')",
            ".gh-eb-pop [aria-label='Close']"
        ]
        
        for selector in popup_selectors:
            try:
                popup = self.page.locator(selector).first
                if popup.is_visible(timeout=1000):
                    self.logger.info(f"Closing pop-up detected by selector: {selector}")
                    popup.click()
                    self.page.wait_for_timeout(1000)
            except Exception:
                pass

    def wait_for_load(self):
        self.page.wait_for_load_state("networkidle")
        self.handle_popups()
