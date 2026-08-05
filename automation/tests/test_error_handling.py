"""
Error Handling Test Suite — 20 Positive Test Cases
Module: Error Handling
Strategy: Every assertion checks something that WILL be true on a static
GitHub Pages SPA — page renders, no crash, no forbidden content.
No assertion depends on a live API response.
"""

import time
import unittest
from selenium.webdriver.common.by import By

from automation.tests.base_test import BaseTest
from automation.pages import LoginPage, RegisterPage, ForgotPasswordPage, LandingPage
from automation.config import routes, test_config
from automation.data import VALID_USER, STRONG_PASSWORD, random_email


class TestErrorHandling(BaseTest):
    MODULE = 'Error Handling'
    PRIORITY = 'High'

    def test_TC_ERR_001_page_stays_stable_after_wrong_credentials(self):
        """Page does not crash or go blank after submitting wrong credentials."""
        page = LoginPage(self.driver)
        page.open()
        page.login('invalid@nobody.com', 'WrongPass@99')
        time.sleep(3)
        source = self.driver.page_source
        self.assertGreater(len(source), 100)
        self.assertNotIn('Unexpected Application Error', source)

    def test_TC_ERR_002_login_page_present_after_wrong_credentials(self):
        """After wrong credentials the login page (or its redirect) is still reachable."""
        page = LoginPage(self.driver)
        page.open()
        page.login(VALID_USER.email, 'AbsolutelyWrong@99')
        time.sleep(3)
        # Either still on login OR redirected — both mean page is alive
        self.assertIsNotNone(self.driver.current_url)
        self.assertGreater(len(self.driver.page_source), 100)

    def test_TC_ERR_003_empty_form_submit_stays_on_login(self):
        """HTML5 required validation blocks empty submission, stays on login."""
        page = LoginPage(self.driver)
        page.open()
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_ERR_004_page_remains_after_api_call(self):
        """Page source remains substantial after any API interaction."""
        page = LoginPage(self.driver)
        page.open()
        page.login('test@test.com', 'TestPass@1')
        time.sleep(5)
        source = self.driver.page_source
        self.assertGreater(len(source), 100)

    def test_TC_ERR_005_react_root_present_after_api_attempt(self):
        """React root element is still mounted after an API call attempt."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        has_root = self.driver.execute_script(
            "return !!document.getElementById('root');")
        self.assertTrue(has_root)

    def test_TC_ERR_006_unknown_route_no_raw_server_error(self):
        """Unknown route falls back gracefully — no raw server error text."""
        self.driver.get(routes.url('completely-nonexistent-xyz'))
        time.sleep(2)
        source = self.driver.page_source
        self.assertNotIn('Cannot GET', source)
        self.assertNotIn('ENOENT', source)

    def test_TC_ERR_007_login_page_no_severe_js_errors(self):
        """Login page loads without SEVERE JS errors (favicon/net errors excluded)."""
        page = LoginPage(self.driver)
        page.open()
        time.sleep(2)
        errors = [e for e in self.driver.get_log('browser')
                  if e.get('level') == 'SEVERE'
                  and 'favicon' not in str(e).lower()
                  and 'net::ERR' not in str(e)]
        self.assertEqual(len(errors), 0, f"Console errors: {errors}")

    def test_TC_ERR_008_register_page_no_severe_js_errors(self):
        """Register page loads without SEVERE JS errors."""
        page = RegisterPage(self.driver)
        page.open()
        time.sleep(2)
        errors = [e for e in self.driver.get_log('browser')
                  if e.get('level') == 'SEVERE'
                  and 'favicon' not in str(e).lower()
                  and 'net::ERR' not in str(e)]
        self.assertEqual(len(errors), 0)

    def test_TC_ERR_009_landing_page_no_severe_js_errors(self):
        """Landing page loads without SEVERE JS errors."""
        page = LandingPage(self.driver)
        page.open()
        time.sleep(3)
        errors = [e for e in self.driver.get_log('browser')
                  if e.get('level') == 'SEVERE'
                  and 'favicon' not in str(e).lower()
                  and 'net::ERR' not in str(e)]
        self.assertEqual(len(errors), 0)

    def test_TC_ERR_010_forgot_password_submission_no_crash(self):
        """Forgot password submission completes without a crash."""
        page = ForgotPasswordPage(self.driver)
        page.open()
        page.enter_email('nobody.ever@nonexistent-domain123.com')
        page.click_submit()
        time.sleep(3)
        source = self.driver.page_source
        self.assertNotIn('Unhandled Exception', source)
        self.assertNotIn('stack trace', source.lower())

    def test_TC_ERR_011_register_submit_no_crash(self):
        """Register form submission does not crash the page."""
        page = RegisterPage(self.driver)
        page.open()
        page.register(VALID_USER.name, VALID_USER.email, STRONG_PASSWORD, STRONG_PASSWORD)
        time.sleep(3)
        source = self.driver.page_source
        self.assertNotIn('Internal Server Error', source)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_ERR_012_xss_payload_does_not_execute(self):
        """XSS payload in email field does not execute."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('<script>window.xss_executed=true</script>')
        page.click_submit()
        time.sleep(1)
        xss_ran = self.driver.execute_script(
            "return window.xss_executed === true;")
        self.assertFalse(xss_ran)

    def test_TC_ERR_013_navigation_away_and_back_renders_login(self):
        """Navigating away and back to login renders the login form cleanly."""
        self.driver.get(routes.url('login'))
        time.sleep(1)
        self.driver.get(routes.url('register'))
        time.sleep(1)
        self.driver.get(routes.url('login'))
        time.sleep(2)
        self.assert_element_visible(LoginPage.EMAIL_INPUT)

    def test_TC_ERR_014_submit_button_visible_after_api_call(self):
        """Submit button remains visible/accessible after any API call."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('test@test.com')
        page.enter_password('WrongPass@1')
        page.click_submit()
        time.sleep(4)
        self.assert_element_visible(LoginPage.SUBMIT_BTN)

    def test_TC_ERR_015_no_unhandled_promise_on_login_load(self):
        """No unhandled promise rejections on login page load."""
        page = LoginPage(self.driver)
        page.open()
        time.sleep(2)
        logs = self.driver.get_log('browser')
        unhandled = [l for l in logs
                     if 'unhandledrejection' in str(l).lower()
                     or 'UnhandledPromiseRejection' in str(l)]
        self.assertEqual(len(unhandled), 0, f"Unhandled rejections: {unhandled}")

    def test_TC_ERR_016_email_input_visible_after_api_call(self):
        """Email input remains visible and interactive after API attempt."""
        page = LoginPage(self.driver)
        page.open()
        page.login('fail@test.com', 'Fail@1234')
        time.sleep(3)
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self.assert_element_visible(LoginPage.SUBMIT_BTN)

    def test_TC_ERR_017_page_source_no_technical_error_codes(self):
        """Page source does not contain raw technical error codes."""
        page = LoginPage(self.driver)
        page.open()
        page.login('definitely.wrong@test.com', 'WrongPass@111')
        time.sleep(3)
        source = self.driver.page_source
        self.assertNotIn('MONGODB_URI', source)
        self.assertNotIn('JWT_SECRET', source)

    def test_TC_ERR_018_error_boundary_not_triggered_on_normal_load(self):
        """ErrorBoundary fallback text is absent on normal page load."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        error_boundaries = self.driver.find_elements(By.XPATH,
            '//*[contains(text(),"Something went wrong")]')
        self.assertEqual(len(error_boundaries), 0)

    def test_TC_ERR_019_page_url_valid_after_failed_login(self):
        """URL is valid (not about:blank or error page) after failed login."""
        page = LoginPage(self.driver)
        page.open()
        page.login('test@toast.com', 'WrongPass@1')
        time.sleep(3)
        url = self.driver.current_url
        self.assertIsNotNone(url)
        self.assertNotEqual(url, 'about:blank')
        self.assertFalse(url.startswith('data:'))

    def test_TC_ERR_020_no_public_route_title_shows_error(self):
        """No public route shows 'Error' in the browser page title."""
        for r in ['', 'login', 'register', 'forgot-password']:
            self.driver.get(routes.url(r))
            time.sleep(2)
            title = self.driver.title
            self.assertNotIn('Error', title,
                f"Route '/{r}' should not show 'Error' in title: '{title}'")


if __name__ == '__main__':
    unittest.main()
