"""
BasePage — parent class for all Page Object Model classes.
Provides shared utilities: navigation, waits, screenshots, JS execution.
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import JavascriptException

from automation.config import test_config, routes
from automation.utils.wait_helper import WaitHelper
from automation.utils.screenshot import ScreenshotUtil

logger = logging.getLogger(__name__)


class BasePage:
    """Base Page Object — all page classes extend this."""

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WaitHelper(driver)
        self.actions = ActionChains(driver)
        self.base_url = test_config.base_url.rstrip('/')

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate_to(self, route: str = ''):
        """Navigate to a route relative to BASE_URL."""
        url = routes.url(route)
        logger.debug(f"Navigating to: {url}")
        self.driver.get(url)
        self.wait.wait_for_react_render()

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_title(self) -> str:
        return self.driver.title

    def get_page_source(self) -> str:
        return self.driver.page_source

    def refresh(self):
        self.driver.refresh()
        self.wait.wait_for_react_render()

    def go_back(self):
        self.driver.back()
        self.wait.wait_for_react_render()

    def go_forward(self):
        self.driver.forward()
        self.wait.wait_for_react_render()

    # ── Elements ──────────────────────────────────────────────────────────────

    def find(self, locator: tuple):
        return self.wait.until_visible(locator)

    def find_all(self, locator: tuple) -> list:
        self.wait.until_present(locator)
        return self.driver.find_elements(*locator)

    def click(self, locator: tuple):
        self.wait.safe_click(locator)

    def type(self, locator: tuple, text: str, clear_first: bool = True):
        self.wait.safe_send_keys(locator, text, clear_first)

    def get_text(self, locator: tuple) -> str:
        return self.find(locator).text.strip()

    def get_attribute(self, locator: tuple, attr: str) -> str:
        return self.find(locator).get_attribute(attr) or ''

    def is_displayed(self, locator: tuple, timeout: int = 5) -> bool:
        return self.wait.is_element_visible(locator, timeout)

    def is_present(self, locator: tuple, timeout: int = 5) -> bool:
        return self.wait.is_element_present(locator, timeout)

    def scroll_to(self, locator: tuple):
        elem = self.find(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_top(self):
        self.driver.execute_script("window.scrollTo(0, 0);")

    def hover(self, locator: tuple):
        elem = self.find(locator)
        self.actions.move_to_element(elem).perform()

    def js_click(self, locator: tuple):
        elem = self.find(locator)
        self.driver.execute_script("arguments[0].click();", elem)

    def js_set_value(self, locator: tuple, value: str):
        elem = self.find(locator)
        self.driver.execute_script(f"arguments[0].value = '{value}';", elem)

    def press_key(self, key):
        self.actions.send_keys(key).perform()

    def press_escape(self):
        self.press_key(Keys.ESCAPE)

    def press_enter(self, locator: tuple = None):
        if locator:
            self.find(locator).send_keys(Keys.RETURN)
        else:
            self.actions.send_keys(Keys.RETURN).perform()

    def clear_field(self, locator: tuple):
        elem = self.find(locator)
        elem.send_keys(Keys.CONTROL + 'a')
        elem.send_keys(Keys.DELETE)

    # ── Screenshots ───────────────────────────────────────────────────────────

    def screenshot(self, name: str) -> str:
        return ScreenshotUtil.capture(self.driver, name)

    # ── Browser Logs ──────────────────────────────────────────────────────────

    def get_console_logs(self) -> list:
        try:
            return self.driver.get_log('browser')
        except Exception:
            return []

    def get_console_errors(self) -> list:
        logs = self.get_console_logs()
        return [l for l in logs if l.get('level') in ('SEVERE', 'ERROR')]

    # ── Assertions ────────────────────────────────────────────────────────────

    def assert_url_contains(self, partial: str):
        current = self.get_current_url()
        assert partial in current, f"Expected URL to contain '{partial}', got: {current}"

    def assert_title_contains(self, text: str):
        title = self.get_title()
        assert text in title, f"Expected title to contain '{text}', got: '{title}'"

    def assert_element_visible(self, locator: tuple, message: str = ''):
        assert self.is_displayed(locator), \
            message or f"Expected element {locator} to be visible"

    def assert_text_equals(self, locator: tuple, expected: str):
        actual = self.get_text(locator)
        assert actual == expected, f"Expected text '{expected}', got '{actual}'"

    def assert_text_contains(self, locator: tuple, expected: str):
        actual = self.get_text(locator)
        assert expected in actual, f"Expected text to contain '{expected}', got '{actual}'"

    # ── Page load performance ─────────────────────────────────────────────────

    def get_page_load_time_ms(self) -> float:
        """Return page load time in milliseconds via Navigation Timing API."""
        try:
            return self.driver.execute_script(
                "const t = performance.timing; "
                "return t.loadEventEnd - t.navigationStart;"
            ) or 0.0
        except JavascriptException:
            return 0.0

    def get_dom_ready_time_ms(self) -> float:
        """Return DOM interactive time in milliseconds."""
        try:
            return self.driver.execute_script(
                "const t = performance.timing; "
                "return t.domInteractive - t.navigationStart;"
            ) or 0.0
        except JavascriptException:
            return 0.0

    def wait_for_url_change(self, old_url: str, timeout: int = 30):
        """Wait until the URL is different from old_url."""
        from selenium.webdriver.support.ui import WebDriverWait
        WebDriverWait(self.driver, timeout).until(lambda d: d.current_url != old_url)
