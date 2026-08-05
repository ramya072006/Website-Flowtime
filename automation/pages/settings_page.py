"""Settings Page Object — FlowTime /settings route."""

from selenium.webdriver.common.by import By
from .base_page import BasePage
from automation.config import routes


class SettingsPage(BasePage):
    PAGE_HEADING   = (By.XPATH, '//*[contains(text(),"Settings") or contains(text(),"settings")]')
    TABS           = (By.CSS_SELECTOR, '[role="tab"], button[data-state]')
    PROFILE_TAB    = (By.XPATH, '//button[contains(text(),"Profile")]')
    SECURITY_TAB   = (By.XPATH, '//button[contains(text(),"Security") or contains(text(),"Password")]')
    NOTIF_TAB      = (By.XPATH, '//button[contains(text(),"Notification")]')
    THEME_SWITCH   = (By.CSS_SELECTOR, 'button[role="switch"], input[type="checkbox"][id*="theme"]')
    SAVE_BTN       = (By.XPATH, '//button[contains(text(),"Save")]')
    NAME_INPUT     = (By.CSS_SELECTOR, 'input[id*="name"], input[placeholder*="name"]')
    DARK_THEME_BTN = (By.XPATH, '//button[contains(text(),"Dark")]')
    LIGHT_THEME_BTN = (By.XPATH, '//button[contains(text(),"Light")]')

    def open(self):
        self.navigate_to(routes.SETTINGS)
        return self

    def open_tab(self, tab_name: str):
        self.click((By.XPATH, f'//button[contains(text(),"{tab_name}")]'))
        return self

    def click_profile_tab(self):
        if self.is_present(self.PROFILE_TAB, 5):
            self.click(self.PROFILE_TAB)
        return self

    def click_security_tab(self):
        if self.is_present(self.SECURITY_TAB, 5):
            self.click(self.SECURITY_TAB)
        return self

    def click_save(self):
        self.click(self.SAVE_BTN)
        return self

    def is_loaded(self) -> bool:
        return self.is_displayed(self.PAGE_HEADING, 10)

    def get_tab_count(self) -> int:
        try:
            return len(self.find_all(self.TABS))
        except Exception:
            return 0
