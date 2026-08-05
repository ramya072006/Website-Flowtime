"""Landing Page Object — FlowTime home route /"""

from selenium.webdriver.common.by import By
from .base_page import BasePage
from automation.config import routes


class LandingPage(BasePage):
    """Page Object for the FlowTime public landing page."""

    GET_STARTED_BTN  = (By.XPATH, '//a[contains(@href,"register")] | //button[contains(text(),"Get Started")]')
    LOGIN_BTN        = (By.XPATH, '//a[contains(@href,"login")]')
    HERO_SECTION     = (By.CSS_SELECTOR, 'main, section, [class*="hero"], [class*="landing"]')
    NAV_BAR          = (By.CSS_SELECTOR, 'nav, header')
    LOGO             = (By.CSS_SELECTOR, '[class*="logo"], a[href="/"]')
    FEATURE_CARDS    = (By.CSS_SELECTOR, '[class*="feature"], [class*="card"]')
    FOOTER           = (By.CSS_SELECTOR, 'footer')

    def open(self):
        self.navigate_to(routes.HOME)
        return self

    def click_get_started(self):
        self.click(self.GET_STARTED_BTN)
        return self

    def click_login(self):
        self.click(self.LOGIN_BTN)
        return self

    def is_hero_visible(self) -> bool:
        return self.is_displayed(self.HERO_SECTION)

    def is_nav_visible(self) -> bool:
        return self.is_displayed(self.NAV_BAR)

    def get_feature_count(self) -> int:
        try:
            return len(self.find_all(self.FEATURE_CARDS))
        except Exception:
            return 0

    def has_footer(self) -> bool:
        return self.is_present(self.FOOTER, 5)
