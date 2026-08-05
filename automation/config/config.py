"""
FlowTime Automation Framework — Central Configuration
All configuration is driven by environment variables with sane defaults.
BASE_URL MUST point to the live GitHub Pages deployment.
Hardcoded URLs are forbidden per the test specification.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env.test'))

# ─────────────────────────────────────────────────────────────────────────────
# Core URL Configuration
# ─────────────────────────────────────────────────────────────────────────────

def _get_base_url() -> str:
    """
    Resolve BASE_URL strictly from environment.
    Never returns localhost or any preview/local URL in CI mode.
    """
    url = os.getenv('BASE_URL', '').strip().rstrip('/')
    ci = os.getenv('CI', '').lower() in ('true', '1', 'yes')

    if not url:
        # Derive from GITHUB_ vars when available
        owner = os.getenv('GITHUB_REPOSITORY_OWNER', '')
        repo_full = os.getenv('GITHUB_REPOSITORY', '')
        repo = repo_full.split('/')[-1] if '/' in repo_full else repo_full
        if owner and repo:
            url = f'https://{owner}.github.io/{repo}'
        else:
            url = os.getenv('PAGES_URL', 'https://example.github.io/taskmanagementAI')

    # Safety gate: never allow localhost in CI
    if ci and ('localhost' in url or '127.0.0.1' in url or '0.0.0.0' in url):
        raise ValueError(
            f"❌ BASE_URL '{url}' points to localhost — Selenium MUST run against "
            "the live GitHub Pages deployment. Set BASE_URL to the GitHub Pages URL."
        )

    return url.rstrip('/') + '/'


@dataclass
class BrowserConfig:
    headless: bool = field(default_factory=lambda: os.getenv('HEADLESS', 'true').lower() == 'true')
    window_width: int = 1920
    window_height: int = 1080
    implicit_wait: int = 10
    explicit_wait: int = 30
    page_load_timeout: int = 60
    browser: str = field(default_factory=lambda: os.getenv('BROWSER', 'chrome').lower())
    chrome_args: list = field(default_factory=lambda: [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-extensions',
        '--disable-infobars',
        '--disable-notifications',
        '--disable-popup-blocking',
        '--disable-blink-features=AutomationControlled',
        '--remote-debugging-port=9222',
        '--window-size=1920,1080',
    ])


@dataclass
class TestConfig:
    base_url: str = field(default_factory=_get_base_url)
    test_email: str = field(default_factory=lambda: os.getenv('TEST_EMAIL', 'selenium.test@flowtime-demo.com'))
    test_password: str = field(default_factory=lambda: os.getenv('TEST_PASSWORD', 'SeleniumTest@123'))
    test_name: str = field(default_factory=lambda: os.getenv('TEST_NAME', 'Selenium Tester'))
    admin_email: str = field(default_factory=lambda: os.getenv('ADMIN_EMAIL', 'admin@flowtime-demo.com'))
    admin_password: str = field(default_factory=lambda: os.getenv('ADMIN_PASSWORD', 'AdminTest@123'))
    retry_count: int = field(default_factory=lambda: int(os.getenv('RETRY_COUNT', '2')))
    parallel_workers: int = field(default_factory=lambda: int(os.getenv('PARALLEL_WORKERS', '4')))
    screenshot_on_failure: bool = True
    screenshot_on_pass: bool = False
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    ci_mode: bool = field(default_factory=lambda: os.getenv('CI', '').lower() in ('true', '1'))


@dataclass
class PathConfig:
    root: str = field(default_factory=lambda: os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @property
    def reports(self) -> str:
        return os.path.join(self.root, 'reports')

    @property
    def screenshots(self) -> str:
        return os.path.join(self.root, 'screenshots')

    @property
    def logs(self) -> str:
        return os.path.join(self.root, 'logs')

    @property
    def excel(self) -> str:
        return os.path.join(self.reports, 'Excel')

    @property
    def html(self) -> str:
        return os.path.join(self.reports, 'HTML')

    @property
    def json_dir(self) -> str:
        return os.path.join(self.reports, 'JSON')

    @property
    def summary(self) -> str:
        return os.path.join(self.reports, 'Summary')

    @property
    def history(self) -> str:
        return os.path.join(self.reports, 'history')

    def ensure_all(self):
        for d in [self.reports, self.screenshots, self.logs,
                  self.excel, self.html, self.json_dir, self.summary, self.history]:
            os.makedirs(d, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Singleton instances
# ─────────────────────────────────────────────────────────────────────────────
browser_config = BrowserConfig()
test_config = TestConfig()
path_config = PathConfig()

# App routes (relative to BASE_URL)
class Routes:
    HOME = ''
    LOGIN = 'login'
    REGISTER = 'register'
    FORGOT_PASSWORD = 'forgot-password'
    RESET_PASSWORD = 'reset-password'
    VERIFY_OTP = 'verify-otp'
    DASHBOARD = 'dashboard'
    TASKS = 'tasks'
    HABITS = 'habits'
    CALENDAR = 'calendar'
    ANALYTICS = 'analytics'
    FOCUS = 'focus'
    NOTIFICATIONS = 'notifications'
    SETTINGS = 'settings'
    AI = 'ai'
    TEAM = 'team'

    @staticmethod
    def url(route: str) -> str:
        base = test_config.base_url.rstrip('/')
        return f"{base}/{route.lstrip('/')}" if route else base + '/'


routes = Routes()
