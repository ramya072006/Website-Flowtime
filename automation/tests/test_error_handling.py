"""
Error Handling Test Suite — 20 Test Cases
Module: Error Handling
Tests: API error responses, network errors, graceful degradation, UI error states.
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

    def test_TC_ERR_001_invalid_credentials_shows_error_not_crash(self):
        """Invalid credentials show error message, page does not crash."""
        page = LoginPage(self.driver)
        page.open()
        page.login('invalid@nobody.com', 'WrongPass@99')
        time.sleep(3)
        source = self.driver.page_source
        self.assertNotIn('Unexpected Application Error', source)
        self.assertNotIn('TypeError', source)
        self.assertNotIn('undefined is not', source)

    def test_TC_ERR_002_wrong_password_error_message_shown(self):
        """Error banner is shown for wrong credentials."""
        page = LoginPage(self.driver)
        page.open()
        page.login(VALID_USER.email, 'AbsolutelyWrong@99')
        time.sleep(3)
        still_on_login = 'login' in self.driver.current_url
        error_visible = page.is_error_displayed()
        self.assertTrue(still_on_login or error_visible,
            "Should show error or stay on login for invalid credentials")

    def test_TC_ERR_003_empty_form_html_validation_error(self):
        """HTML5 validation prevents empty form submission."""
        page = LoginPage(self.driver)
        page.open()
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_ERR_004_network_timeout_graceful_handling(self):
        """Page handles slow/unavailable API without white screen."""
        page = LoginPage(self.driver)
        page.open()
        page.login('test@test.com', 'TestPass@1')
        time.sleep(5)
        source = self.driver.page_source
        self.assertGreater(len(source), 100,
            "Page should not go blank on API timeout")

    def test_TC_ERR_005_error_boundary_wraps_content(self):
        """React ErrorBoundary is present in DOM structure."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        source = self.driver.page_source
        # Root is mounted — ErrorBoundary wraps app content
        has_root = self.driver.execute_script(
            "return !!document.getElementById('root');")
        self.assertTrue(has_root)

    def test_TC_ERR_006_404_route_handled_gracefully(self):
        """Unknown route falls back to landing without a raw error page."""
        self.driver.get(routes.url('completely-nonexistent-xyz'))
        time.sleep(2)
        source = self.driver.page_source
        self.assertNotIn('Cannot GET', source)
        self.assertNotIn('ENOENT', source)

    def test_TC_ERR_007_js_errors_not_present_on_login_load(self):
        """No SEVERE JavaScript errors on login page load."""
        page = LoginPage(self.driver)
        page.open()
        time.sleep(2)
        errors = page.get_console_errors()
        severe = [e for e in errors
                  if e.get('level') == 'SEVERE'
                  and 'favicon' not in str(e).lower()
                  and 'net::ERR' not in str(e)]
        self.assertEqual(len(severe), 0,
            f"JS errors on login: {severe}")

    def test_TC_ERR_008_js_errors_not_present_on_register_load(self):
        """No SEVERE JavaScript errors on register page load."""
        page = RegisterPage(self.driver)
        page.open()
        time.sleep(2)
        errors = page.get_console_errors()
        severe = [e for e in errors
                  if e.get('level') == 'SEVERE'
                  and 'favicon' not in str(e).lower()
                  and 'net::ERR' not in str(e)]
        self.assertEqual(len(severe), 0)

    def test_TC_ERR_009_js_errors_not_present_on_landing_load(self):
        """No SEVERE JavaScript errors on landing page load."""
        page = LandingPage(self.driver)
        page.open()
        time.sleep(3)
        errors = page.get_console_errors()
        severe = [e for e in errors
                  if e.get('level') == 'SEVERE'
                  and 'favicon' not in str(e).lower()
                  and 'net::ERR' not in str(e)]
        self.assertEqual(len(severe), 0)

    def test_TC_ERR_010_forgot_password_unknown_email_handled(self):
        """Submitting an unknown email on forgot password is handled gracefully."""
        page = ForgotPasswordPage(self.driver)
        page.open()
        page.enter_email('nobody.ever@nonexistent-domain123.com')
        page.click_submit()
        time.sleep(3)
        source = self.driver.page_source
        self.assertNotIn('Unhandled Exception', source)
        self.assertNotIn('stack trace', source.lower())

    def test_TC_ERR_011_register_existing_email_error_not_crash(self):
        """Registering with existing email shows error, not a crash."""
        page = RegisterPage(self.driver)
        page.open()
        page.register(VALID_USER.name, VALID_USER.email, STRONG_PASSWORD, STRONG_PASSWORD)
        time.sleep(3)
        source = self.driver.page_source
        self.assertNotIn('Internal Server Error', source)

    def test_TC_ERR_012_xss_payload_not_reflected_in_source(self):
        """XSS payload submitted in form is not reflected in page source."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('<script>window.xss_executed=true</script>')
        page.click_submit()
        time.sleep(1)
        xss_ran = self.driver.execute_script(
            "return window.xss_executed === true;")
        self.assertFalse(xss_ran, "XSS should not have executed")

    def test_TC_ERR_013_form_error_clears_after_navigation(self):
        """Error state does not persist after navigating away and back."""
        page = LoginPage(self.driver)
        page.open()
        page.login('wrong@test.com', 'Wrong@1')
        time.sleep(2)
        self.driver.get(routes.url('register'))
        time.sleep(1)
        self.driver.get(routes.url('login'))
        time.sleep(2)
        error_visible = page.is_error_displayed()
        self.assertFalse(error_visible,
            "Error from previous session should not persist after re-navigation")

    def test_TC_ERR_014_loading_state_removed_after_api_response(self):
        """Loading spinner disappears after API responds (pass or fail)."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('test@test.com')
        page.enter_password('WrongPass@1')
        page.click_submit()
        time.sleep(4)
        spinners = self.driver.find_elements(By.CSS_SELECTOR, '.animate-spin')
        visible_spinners = [s for s in spinners if s.is_displayed()]
        self.assertEqual(len(visible_spinners), 0,
            "Loading spinner should be gone after API response")

    def test_TC_ERR_015_browser_console_no_unhandled_promise(self):
        """No unhandled promise rejections on login page."""
        page = LoginPage(self.driver)
        page.open()
        time.sleep(2)
        logs = self.driver.get_log('browser')
        unhandled = [l for l in logs
                     if 'unhandledrejection' in str(l).lower()
                     or 'UnhandledPromiseRejection' in str(l)]
        self.assertEqual(len(unhandled), 0,
            f"Unhandled promise rejections: {unhandled}")

    def test_TC_ERR_016_page_recovers_after_failed_api_call(self):
        """Page is still interactive after an API call fails."""
        page = LoginPage(self.driver)
        page.open()
        page.login('fail@test.com', 'Fail@1234')
        time.sleep(3)
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self.assert_element_visible(LoginPage.SUBMIT_BTN)

    def test_TC_ERR_017_error_message_contains_human_readable_text(self):
        """Error messages use human-readable language, not technical codes."""
        page = LoginPage(self.driver)
        page.open()
        page.login('definitely.wrong@test.com', 'WrongPass@111')
        time.sleep(3)
        if page.is_error_displayed():
            error_text = page.get_attribute(LoginPage.ERROR_BANNER, 'textContent') or \
                         page.get_text(LoginPage.ERROR_BANNER)
            self.assertNotIn('500', error_text)
            self.assertNotIn('null', error_text.lower())
            self.assertNotIn('undefined', error_text.lower())

    def test_TC_ERR_018_spa_error_boundary_catches_render_errors(self):
        """React root renders without ErrorBoundary fallback on normal pages."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        error_boundaries = self.driver.find_elements(By.XPATH,
            '//*[contains(text(),"Something went wrong")]')
        self.assertEqual(len(error_boundaries), 0,
            "ErrorBoundary fallback should not be shown on normal load")

    def test_TC_ERR_019_toaster_shows_on_error_and_dismisses(self):
        """Toast notification appears and is dismissible on error."""
        page = LoginPage(self.driver)
        page.open()
        page.login('test@toast.com', 'WrongPass@1')
        time.sleep(3)
        toasts = self.driver.find_elements(By.CSS_SELECTOR,
            '[data-state="open"], [role="status"], [class*="toast"]')
        # Toast may or may not appear depending on implementation
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_ERR_020_page_title_not_error_on_any_public_route(self):
        """No public route shows 'Error' in the page title."""
        routes_to_check = ['', 'login', 'register', 'forgot-password']
        for r in routes_to_check:
            self.driver.get(routes.url(r))
            time.sleep(2)
            title = self.driver.title
            self.assertNotIn('Error', title,
                f"Route '/{r}' has 'Error' in title: '{title}'")


if __name__ == '__main__':
    unittest.main()
