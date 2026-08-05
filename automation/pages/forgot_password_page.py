"""Forgot Password Page Object."""

from selenium.webdriver.common.by import By
from .base_page import BasePage
from automation.config import routes


class ForgotPasswordPage(BasePage):
    EMAIL_INPUT   = (By.ID, 'email')
    SUBMIT_BTN    = (By.CSS_SELECTOR, 'button[type="submit"]')
    SUCCESS_MSG   = (By.XPATH, '//*[contains(text(),"sent") or contains(text(),"check your email")]')
    ERROR_MSG     = (By.CSS_SELECTOR, '[class*="destructive"], [class*="error"]')
    BACK_LINK     = (By.XPATH, '//a[contains(@href,"login")]')

    def open(self):
        self.navigate_to(routes.FORGOT_PASSWORD)
        return self

    def enter_email(self, email: str):
        self.type(self.EMAIL_INPUT, email)
        return self

    def click_submit(self):
        self.click(self.SUBMIT_BTN)
        return self

    def submit_email(self, email: str):
        self.enter_email(email)
        self.click_submit()
        return self

    def is_success_shown(self) -> bool:
        return self.is_present(self.SUCCESS_MSG, 10)

    def is_error_shown(self) -> bool:
        return self.is_present(self.ERROR_MSG, 5)

    def click_back_to_login(self):
        self.click(self.BACK_LINK)
        return self
