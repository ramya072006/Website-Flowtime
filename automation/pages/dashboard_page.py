"""Dashboard Page Object — FlowTime /dashboard route."""

from selenium.webdriver.common.by import By
from .base_page import BasePage
from automation.config import routes


class DashboardPage(BasePage):
    """Page Object for the authenticated dashboard."""

    SIDEBAR          = (By.CSS_SELECTOR, 'nav[class*="sidebar"], aside, [class*="sidebar"]')
    HEADER           = (By.CSS_SELECTOR, 'header, [class*="header"]')
    WELCOME_TEXT     = (By.XPATH, '//*[contains(text(),"Welcome") or contains(text(),"Dashboard")]')
    USER_AVATAR      = (By.CSS_SELECTOR, '[class*="avatar"], [aria-label*="user"], [aria-label*="menu"]')
    NAV_DASHBOARD    = (By.XPATH, '//a[contains(@href,"dashboard")]')
    NAV_TASKS        = (By.XPATH, '//a[contains(@href,"tasks")]')
    NAV_HABITS       = (By.XPATH, '//a[contains(@href,"habits")]')
    NAV_CALENDAR     = (By.XPATH, '//a[contains(@href,"calendar")]')
    NAV_ANALYTICS    = (By.XPATH, '//a[contains(@href,"analytics")]')
    NAV_FOCUS        = (By.XPATH, '//a[contains(@href,"focus")]')
    NAV_NOTIFICATIONS = (By.XPATH, '//a[contains(@href,"notifications")]')
    NAV_SETTINGS     = (By.XPATH, '//a[contains(@href,"settings")]')
    NAV_AI           = (By.XPATH, '//a[contains(@href,"/ai")]')
    NAV_TEAM         = (By.XPATH, '//a[contains(@href,"team")]')
    STATS_CARDS      = (By.CSS_SELECTOR, '[class*="stat"], [class*="metric"], [class*="card"]')
    LOADING_SPINNER  = (By.CSS_SELECTOR, '.animate-spin, .animate-pulse')

    def open(self):
        self.navigate_to(routes.DASHBOARD)
        return self

    def is_dashboard_loaded(self) -> bool:
        return (self.is_displayed(self.SIDEBAR, 10) or
                self.is_displayed(self.HEADER, 10))

    def navigate_to_tasks(self):
        self.click(self.NAV_TASKS)
        self.wait.until_url_contains('tasks')
        return self

    def navigate_to_habits(self):
        self.click(self.NAV_HABITS)
        self.wait.until_url_contains('habits')
        return self

    def navigate_to_calendar(self):
        self.click(self.NAV_CALENDAR)
        self.wait.until_url_contains('calendar')
        return self

    def navigate_to_analytics(self):
        self.click(self.NAV_ANALYTICS)
        self.wait.until_url_contains('analytics')
        return self

    def navigate_to_settings(self):
        self.click(self.NAV_SETTINGS)
        self.wait.until_url_contains('settings')
        return self

    def navigate_to_ai(self):
        self.click(self.NAV_AI)
        self.wait.until_url_contains('/ai')
        return self

    def navigate_to_team(self):
        self.click(self.NAV_TEAM)
        self.wait.until_url_contains('team')
        return self

    def get_stats_count(self) -> int:
        try:
            return len(self.find_all(self.STATS_CARDS))
        except Exception:
            return 0

    def is_sidebar_visible(self) -> bool:
        return self.is_displayed(self.SIDEBAR, 5)

    def is_header_visible(self) -> bool:
        return self.is_displayed(self.HEADER, 5)
