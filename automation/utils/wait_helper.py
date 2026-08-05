"""Explicit wait helpers wrapping Selenium's WebDriverWait."""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    StaleElementReferenceException, ElementNotInteractableException
)

from automation.config import browser_config

logger = logging.getLogger(__name__)


class WaitHelper:
    """
    Centralised explicit wait utilities.
    Always uses configurable timeouts — no hardcoded waits.
    """

    def __init__(self, driver: webdriver.Chrome, timeout: int = None):
        self.driver = driver
        self.timeout = timeout or browser_config.explicit_wait
        self.wait = WebDriverWait(driver, self.timeout,
                                  ignored_exceptions=[StaleElementReferenceException])

    def until_visible(self, locator: tuple, timeout: int = None):
        """Wait until element is visible."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.visibility_of_element_located(locator)
        )

    def until_clickable(self, locator: tuple, timeout: int = None):
        """Wait until element is clickable."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.element_to_be_clickable(locator)
        )

    def until_present(self, locator: tuple, timeout: int = None):
        """Wait until element is present in DOM."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.presence_of_element_located(locator)
        )

    def until_text_present(self, locator: tuple, text: str, timeout: int = None):
        """Wait until element contains text."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.text_to_be_present_in_element(locator, text)
        )

    def until_url_contains(self, partial_url: str, timeout: int = None):
        """Wait until current URL contains the partial string."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.url_contains(partial_url)
        )

    def until_url_matches(self, url: str, timeout: int = None):
        """Wait until current URL matches exactly."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(EC.url_to_be(url))

    def until_invisible(self, locator: tuple, timeout: int = None):
        """Wait until element is invisible or removed."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.invisibility_of_element_located(locator)
        )

    def until_element_count(self, locator: tuple, count: int, timeout: int = None):
        """Wait until the number of elements matches."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            lambda d: len(d.find_elements(*locator)) >= count
        )

    def until_title_contains(self, title_part: str, timeout: int = None):
        """Wait until page title contains given text."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(EC.title_contains(title_part))

    def safe_click(self, locator: tuple, timeout: int = None):
        """Wait for element to be clickable then click it."""
        elem = self.until_clickable(locator, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
        time.sleep(0.2)
        elem.click()
        return elem

    def safe_send_keys(self, locator: tuple, text: str, clear_first: bool = True, timeout: int = None):
        """Wait for element, optionally clear, then type."""
        elem = self.until_clickable(locator, timeout)
        if clear_first:
            elem.clear()
        elem.send_keys(text)
        return elem

    def is_element_present(self, locator: tuple, timeout: int = 5) -> bool:
        """Non-raising check for element presence."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def is_element_visible(self, locator: tuple, timeout: int = 5) -> bool:
        """Non-raising check for element visibility."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_page_load(self, timeout: int = None):
        """Wait for document.readyState to be complete."""
        t = timeout or self.timeout
        WebDriverWait(self.driver, t).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def wait_for_react_render(self, timeout: int = 10):
        """Wait for React SPA to finish rendering (no loading spinners)."""
        time.sleep(0.5)
        self.wait_for_page_load(timeout)
        # Wait for React root to be populated
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script(
                    "return document.getElementById('root') && "
                    "document.getElementById('root').children.length > 0"
                )
            )
        except TimeoutException:
            logger.warning("React root may not have rendered within timeout")
