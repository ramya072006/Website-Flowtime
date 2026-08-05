"""Register Page Object — FlowTime /register route."""

from selenium.webdriver.common.by import By
from .base_page import BasePage
from automation.config import routes


class RegisterPage(BasePage):
    """Page Object for the FlowTime registration page."""

    NAME_INPUT     = (By.ID, 'name')
    EMAIL_INPUT    = (By.ID, 'email')
    PASS_INPUT     = (By.ID, 'password')
    CONFIRM_INPUT  = (By.ID, 'confirmPassword')
    SUBMIT_BTN     = (By.CSS_SELECTOR, 'button[type="submit"]')
    LOGIN_LINK     = (By.XPATH, '//a[contains(@href,"login")]')
    STRENGTH_BAR   = (By.CSS_SELECTOR, '.bg-red-500, .bg-yellow-500, .bg-blue-500, .bg-green-500')
    PASS_MISMATCH  = (By.XPATH, '//p[contains(text(),"do not match")]')
    TOAST          = (By.CSS_SELECTOR, '[data-state="open"][role="status"], [class*="toast"]')
    LOADING_SPIN   = (By.CSS_SELECTOR, '.animate-spin')

    def open(self):
        self.navigate_to(routes.REGISTER)
        return self

    def enter_name(self, name: str):
        self.type(self.NAME_INPUT, name)
        return self

    def enter_email(self, email: str):
        self.type(self.EMAIL_INPUT, email)
        return self

    def enter_password(self, password: str):
        self.type(self.PASS_INPUT, password)
        return self

    def enter_confirm_password(self, password: str):
        self.type(self.CONFIRM_INPUT, password)
        return self

    def click_submit(self):
        self.click(self.SUBMIT_BTN)
        return self

    def register(self, name: str, email: str, password: str, confirm: str = None):
        self.enter_name(name)
        self.enter_email(email)
        self.enter_password(password)
        self.enter_confirm_password(confirm or password)
        self.click_submit()
        return self

    def is_submit_disabled(self) -> bool:
        elem = self.find(self.SUBMIT_BTN)
        return elem.get_attribute('disabled') is not None

    def is_password_mismatch_shown(self) -> bool:
        return self.is_present(self.PASS_MISMATCH, 3)

    def is_strength_bar_visible(self) -> bool:
        return self.is_present(self.STRENGTH_BAR, 3)

    def click_login_link(self):
        self.click(self.LOGIN_LINK)
        return self

    def wait_for_otp_redirect(self):
        self.wait.until_url_contains('verify-otp', timeout=15)

    def is_loading(self) -> bool:
        return self.is_present(self.LOADING_SPIN, 3)
