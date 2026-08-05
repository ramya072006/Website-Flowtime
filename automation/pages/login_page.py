"""Login Page Object — FlowTime /login route."""

from selenium.webdriver.common.by import By
from .base_page import BasePage
from automation.config import routes


class LoginPage(BasePage):
    """Page Object for the FlowTime login page."""

    # Locators
    EMAIL_INPUT    = (By.ID, 'email')
    PASSWORD_INPUT = (By.ID, 'password')
    SUBMIT_BTN     = (By.CSS_SELECTOR, 'button[type="submit"]')
    SHOW_PASS_BTN  = (By.CSS_SELECTOR, 'button[type="button"]')
    ERROR_BANNER   = (By.CSS_SELECTOR, '.bg-destructive\\/10, [class*="destructive"]')
    LOGO_LINK      = (By.CSS_SELECTOR, 'a[href="/"]')
    FORGOT_LINK    = (By.XPATH, '//a[contains(@href,"forgot-password")]')
    REGISTER_LINK  = (By.XPATH, '//a[contains(@href,"register")]')
    LOADING_SPINNER = (By.CSS_SELECTOR, '.animate-spin')
    VERIFY_NOW_BTN  = (By.XPATH, '//button[contains(text(),"Verify now")]')

    def open(self):
        """Navigate to login page."""
        self.navigate_to(routes.LOGIN)
        return self

    def enter_email(self, email: str):
        self.type(self.EMAIL_INPUT, email)
        return self

    def enter_password(self, password: str):
        self.type(self.PASSWORD_INPUT, password)
        return self

    def toggle_password_visibility(self):
        self.click(self.SHOW_PASS_BTN)
        return self

    def click_submit(self):
        self.click(self.SUBMIT_BTN)
        return self

    def login(self, email: str, password: str):
        """Full login action: fill form and submit."""
        self.enter_email(email)
        self.enter_password(password)
        self.click_submit()
        return self

    def is_submit_disabled(self) -> bool:
        elem = self.find(self.SUBMIT_BTN)
        return elem.get_attribute('disabled') is not None

    def get_error_message(self) -> str:
        if self.is_present(self.ERROR_BANNER, 3):
            return self.get_text(self.ERROR_BANNER)
        return ''

    def is_error_displayed(self) -> bool:
        return self.is_displayed(self.ERROR_BANNER, 3)

    def click_forgot_password(self):
        self.click(self.FORGOT_LINK)
        return self

    def click_register(self):
        self.click(self.REGISTER_LINK)
        return self

    def click_logo(self):
        self.click(self.LOGO_LINK)
        return self

    def is_loading(self) -> bool:
        return self.is_present(self.LOADING_SPINNER, 3)

    def wait_for_redirect_to_dashboard(self):
        self.wait.until_url_contains('dashboard', timeout=15)

    def get_email_input_type(self) -> str:
        return self.get_attribute(self.EMAIL_INPUT, 'type')

    def get_password_input_type(self) -> str:
        return self.get_attribute(self.PASSWORD_INPUT, 'type')
