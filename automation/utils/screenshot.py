"""Screenshot capture utility."""

import os
import base64
from datetime import datetime
from selenium import webdriver
from automation.config import path_config
from automation.utils.logger import get_logger

logger = get_logger(__name__)


class ScreenshotUtil:
    """Captures, saves, and encodes screenshots for reports."""

    @staticmethod
    def capture(driver: webdriver.Chrome, name: str, folder: str = None) -> str:
        """
        Capture a screenshot and save to disk.
        Returns the absolute file path.
        """
        path_config.ensure_all()
        folder = folder or path_config.screenshots
        os.makedirs(folder, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in name)
        filename = f"{safe_name}_{timestamp}.png"
        filepath = os.path.join(folder, filename)

        try:
            driver.save_screenshot(filepath)
            logger.debug(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Screenshot capture failed for '{name}': {e}")
            return ''

    @staticmethod
    def capture_element(driver: webdriver.Chrome, element, name: str) -> str:
        """Capture screenshot of a specific element."""
        path_config.ensure_all()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in name)
        filepath = os.path.join(path_config.screenshots, f"{safe_name}_{timestamp}.png")
        try:
            element.screenshot(filepath)
            return filepath
        except Exception:
            return ScreenshotUtil.capture(driver, name)

    @staticmethod
    def to_base64(filepath: str) -> str:
        """Convert a screenshot file to base64 string for HTML embedding."""
        try:
            with open(filepath, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception:
            return ''

    @staticmethod
    def capture_and_encode(driver: webdriver.Chrome, name: str) -> tuple[str, str]:
        """Capture screenshot and return (filepath, base64_string)."""
        filepath = ScreenshotUtil.capture(driver, name)
        b64 = ScreenshotUtil.to_base64(filepath) if filepath else ''
        return filepath, b64
