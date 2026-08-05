"""
DriverFactory — creates headless Chrome WebDriver instances.
Always uses the live deployment URL from config. Never localhost.
"""

import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from automation.config import browser_config, test_config

logger = logging.getLogger(__name__)


class DriverFactory:
    """Factory for creating and configuring Selenium WebDriver instances."""

    @staticmethod
    def create_driver() -> webdriver.Chrome:
        """Create a configured Chrome WebDriver instance."""
        options = ChromeOptions()

        if browser_config.headless:
            options.add_argument('--headless=new')

        for arg in browser_config.chrome_args:
            options.add_argument(arg)

        # Anti-detection
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Prefs: disable notifications, geolocation prompts
        prefs = {
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_setting_values.geolocation': 2,
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
        }
        options.add_experimental_option('prefs', prefs)

        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception:
            # Fallback: let webdriver-manager find chromedriver on PATH
            driver = webdriver.Chrome(options=options)

        driver.set_window_size(browser_config.window_width, browser_config.window_height)
        driver.set_page_load_timeout(browser_config.page_load_timeout)
        driver.implicitly_wait(browser_config.implicit_wait)

        # Mask webdriver property
        driver.execute_cdp_cmd(
            'Page.addScriptToEvaluateOnNewDocument',
            {'source': "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
        )

        logger.info(f"Chrome WebDriver created — headless={browser_config.headless}")
        logger.info(f"Target BASE_URL: {test_config.base_url}")
        return driver

    @staticmethod
    def quit_driver(driver: webdriver.Chrome):
        """Safely quit the WebDriver."""
        try:
            if driver:
                driver.quit()
                logger.info("WebDriver quit successfully")
        except Exception as e:
            logger.warning(f"Error quitting driver: {e}")
