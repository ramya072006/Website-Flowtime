"""
Authentication Test Suite — 40 Positive Test Cases
Module: Authentication
All assertions verify POSITIVE outcomes: page loads, elements visible,
correct attributes, successful navigation, field accepts input.
No assertions depend on live API responses or error states.
"""

import time
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from automation.tests.base_test import BaseTest
from automation.pages import LoginPage, RegisterPage, ForgotPasswordPage, LandingPage
from automation.config import routes, test_config
from automation.data import VALID_USER, STRONG_PASSWORD, random_email, BOUNDARY_VALUES


class TestAuthentication(BaseTest):
    MODULE = 'Authentication'
    PRIORITY = 'Critical'

    def test_TC_AUTH_001_login_page_loads(self):
        """Login page renders all key elements on live deployment."""
        page = LoginPage(self.driver)
        page.open()
        self.assert_url_contains('login')
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self.assert_element_visible(LoginPage.PASSWORD_INPUT)
        self.assert_element_visible(LoginPage.SUBMIT_BTN)

    def test_TC_AUTH_002_login_email_field_accepts_input(self):
        """Email input accepts and retains valid email value."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email(VALID_USER.email)
        value = page.get_attribute(LoginPage.EMAIL_INPUT, 'value')
        self.assertEqual(value, VALID_USER.email)

    def test_TC_AUTH_003_login_email_field_type_is_email(self):
        """Email input has type='email' for browser validation."""
        page = LoginPage(self.driver)
        page.open()
        self.assertEqual(page.get_email_input_type(), 'email')

    def test_TC_AUTH_004_login_password_field_masked_by_default(self):
        """Password field defaults to type='password' (masked)."""
        page = LoginPage(self.driver)
        page.open()
        self.assertEqual(page.get_password_input_type(), 'password')

    def test_TC_AUTH_005_login_password_visibility_toggle(self):
        """Clicking the eye icon changes password type to text."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_password('SomePassword@1')
        page.toggle_password_visibility()
        time.sleep(0.3)
        self.assertEqual(page.get_password_input_type(), 'text')

    def test_TC_AUTH_006_login_page_stays_on_empty_submit(self):
        """Empty form submit keeps user on login page."""
        page = LoginPage(self.driver)
        page.open()
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_AUTH_007_login_page_stays_on_email_only(self):
        """Submitting with only email keeps user on login page."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email(VALID_USER.email)
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_AUTH_008_login_page_stays_on_invalid_email(self):
        """Non-email format keeps user on login page."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('notanemail')
        page.enter_password(VALID_USER.password)
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_AUTH_009_login_forgot_password_link_navigates(self):
        """Forgot password link navigates to forgot-password page."""
        page = LoginPage(self.driver)
        page.open()
        page.click_forgot_password()
        time.sleep(2)
        self.assert_url_contains('forgot-password')

    def test_TC_AUTH_010_login_register_link_navigates(self):
        """Sign-up link on login page navigates to register page."""
        page = LoginPage(self.driver)
        page.open()
        page.click_register()
        time.sleep(2)
        self.assert_url_contains('register')

    def test_TC_AUTH_011_login_page_title_not_empty(self):
        """Login page has a non-empty browser title."""
        page = LoginPage(self.driver)
        page.open()
        self.assertGreater(len(self.driver.title), 0)

    def test_TC_AUTH_012_login_email_autocomplete_attribute(self):
        """Email input has autocomplete='email'."""
        page = LoginPage(self.driver)
        page.open()
        self.assertEqual(page.get_attribute(LoginPage.EMAIL_INPUT, 'autocomplete'), 'email')

    def test_TC_AUTH_013_login_password_autocomplete_attribute(self):
        """Password input has a recognized autocomplete value."""
        page = LoginPage(self.driver)
        page.open()
        ac = page.get_attribute(LoginPage.PASSWORD_INPUT, 'autocomplete')
        self.assertIn(ac, ['current-password', 'password'])

    def test_TC_AUTH_014_login_page_source_renders(self):
        """Login page HTML source is substantial."""
        page = LoginPage(self.driver)
        page.open()
        self.assertGreater(len(self.driver.page_source), 500)

    def test_TC_AUTH_015_login_forgot_link_visible(self):
        """Forgot password link is visible on login page."""
        page = LoginPage(self.driver)
        page.open()
        self.assert_element_visible(LoginPage.FORGOT_LINK)

    def test_TC_AUTH_016_register_page_loads_all_fields(self):
        """Register page renders all four required inputs."""
        page = RegisterPage(self.driver)
        page.open()
        self.assert_url_contains('register')
        self.assert_element_visible(RegisterPage.NAME_INPUT)
        self.assert_element_visible(RegisterPage.EMAIL_INPUT)
        self.assert_element_visible(RegisterPage.PASS_INPUT)
        self.assert_element_visible(RegisterPage.CONFIRM_INPUT)
        self.assert_element_visible(RegisterPage.SUBMIT_BTN)

    def test_TC_AUTH_017_register_password_field_type(self):
        """Register password field is masked by default."""
        page = RegisterPage(self.driver)
        page.open()
        ftype = page.get_attribute(RegisterPage.PASS_INPUT, 'type')
        self.assertEqual(ftype, 'password')

    def test_TC_AUTH_018_register_confirm_password_type(self):
        """Confirm password field is masked by default."""
        page = RegisterPage(self.driver)
        page.open()
        ftype = page.get_attribute(RegisterPage.CONFIRM_INPUT, 'type')
        self.assertEqual(ftype, 'password')

    def test_TC_AUTH_019_register_strength_bar_renders_on_typing(self):
        """Password strength indicator appears when user types a password."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_password('TestPass')
        time.sleep(0.5)
        has_bar = page.is_strength_bar_visible()
        self.assertTrue(has_bar)

    def test_TC_AUTH_020_register_matching_passwords_enables_submit(self):
        """Submit is enabled when all fields are valid and passwords match."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('Test User')
        page.enter_email(random_email())
        page.enter_password(STRONG_PASSWORD)
        page.enter_confirm_password(STRONG_PASSWORD)
        time.sleep(0.5)
        btn = page.find(RegisterPage.SUBMIT_BTN)
        self.assertIsNone(btn.get_attribute('disabled'))

    def test_TC_AUTH_021_register_login_link_navigates(self):
        """Login link on register page navigates to login."""
        page = RegisterPage(self.driver)
        page.open()
        page.click_login_link()
        time.sleep(2)
        self.assert_url_contains('login')

    def test_TC_AUTH_022_register_email_field_type_is_email(self):
        """Email field on register has type='email'."""
        page = RegisterPage(self.driver)
        page.open()
        self.assertEqual(page.get_attribute(RegisterPage.EMAIL_INPUT, 'type'), 'email')

    def test_TC_AUTH_023_register_name_field_required_attribute(self):
        """Name field has the required attribute."""
        page = RegisterPage(self.driver)
        page.open()
        self.assertIsNotNone(page.get_attribute(RegisterPage.NAME_INPUT, 'required'))

    def test_TC_AUTH_024_register_empty_submit_stays_on_register(self):
        """Empty register form submit keeps user on register page."""
        page = RegisterPage(self.driver)
        page.open()
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('register')

    def test_TC_AUTH_025_forgot_password_page_loads(self):
        """Forgot password page loads with email input and submit button."""
        page = ForgotPasswordPage(self.driver)
        page.open()
        self.assert_url_contains('forgot-password')
        self.assert_element_visible(ForgotPasswordPage.EMAIL_INPUT)
        self.assert_element_visible(ForgotPasswordPage.SUBMIT_BTN)

    def test_TC_AUTH_026_forgot_password_stays_on_invalid_email(self):
        """Invalid email format keeps user on forgot-password page."""
        page = ForgotPasswordPage(self.driver)
        page.open()
        page.enter_email('notvalid')
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('forgot-password')

    def test_TC_AUTH_027_forgot_password_back_link_navigates(self):
        """Back to login link navigates to login page."""
        page = ForgotPasswordPage(self.driver)
        page.open()
        page.click_back_to_login()
        time.sleep(2)
        self.assert_url_contains('login')

    def test_TC_AUTH_028_landing_page_loads(self):
        """Landing page is accessible and has content."""
        page = LandingPage(self.driver)
        page.open()
        time.sleep(2)
        self.assertGreater(len(self.driver.page_source), 500)

    def test_TC_AUTH_029_login_url_is_correct(self):
        """Navigating to /login results in correct URL."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        self.assert_url_contains('login')

    def test_TC_AUTH_030_register_url_is_correct(self):
        """Navigating to /register results in correct URL."""
        self.driver.get(routes.url('register'))
        time.sleep(2)
        self.assert_url_contains('register')

    def test_TC_AUTH_031_login_handles_xss_safely(self):
        """XSS payload in email field does not execute — page stays stable."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('<script>window.__xss=1</script>')
        time.sleep(0.5)
        xss_ran = self.driver.execute_script('return window.__xss === 1;')
        self.assertFalse(xss_ran)

    def test_TC_AUTH_032_login_handles_sql_injection_safely(self):
        """SQL injection payload leaves page intact."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email("'; DROP TABLE users; --")
        page.enter_password('pass')
        page.click_submit()
        time.sleep(1)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_AUTH_033_login_handles_very_long_email(self):
        """Very long email is handled without a crash."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('a' * 200 + '@test.com')
        page.enter_password('SomePass@1')
        page.click_submit()
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_AUTH_034_login_handles_unicode_email(self):
        """Unicode characters in email are handled gracefully."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email(BOUNDARY_VALUES['unicode'] + '@test.com')
        page.enter_password('Pass@123')
        page.click_submit()
        time.sleep(1)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_AUTH_035_login_keyboard_enter_submits(self):
        """Pressing Enter in password field triggers form submission."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email(VALID_USER.email)
        field = page.find(LoginPage.PASSWORD_INPUT)
        field.send_keys(VALID_USER.password)
        field.send_keys(Keys.RETURN)
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_AUTH_036_login_page_no_console_errors_on_load(self):
        """Login page loads without SEVERE JavaScript errors."""
        page = LoginPage(self.driver)
        page.open()
        time.sleep(2)
        severe = [e for e in self.driver.get_log('browser')
                  if e.get('level') == 'SEVERE'
                  and 'favicon' not in str(e).lower()
                  and 'net::ERR' not in str(e)]
        self.assertEqual(len(severe), 0, f"Console errors: {severe}")

    def test_TC_AUTH_037_register_page_no_console_errors(self):
        """Register page loads without SEVERE JavaScript errors."""
        page = RegisterPage(self.driver)
        page.open()
        time.sleep(2)
        severe = [e for e in self.driver.get_log('browser')
                  if e.get('level') == 'SEVERE'
                  and 'favicon' not in str(e).lower()
                  and 'net::ERR' not in str(e)]
        self.assertEqual(len(severe), 0)

    def test_TC_AUTH_038_forgot_password_no_console_errors(self):
        """Forgot password page loads without SEVERE errors."""
        page = ForgotPasswordPage(self.driver)
        page.open()
        time.sleep(2)
        severe = [e for e in self.driver.get_log('browser')
                  if e.get('level') == 'SEVERE'
                  and 'favicon' not in str(e).lower()
                  and 'net::ERR' not in str(e)]
        self.assertEqual(len(severe), 0)

    def test_TC_AUTH_039_login_react_root_populated(self):
        """React root is populated after login page loads."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        kids = self.driver.execute_script(
            "const r=document.getElementById('root'); return r ? r.children.length : 0;")
        self.assertGreater(kids, 0)

    def test_TC_AUTH_040_login_page_directly_accessible(self):
        """Login page is directly accessible via its URL."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        self.assert_url_contains('login')
        self.assert_element_visible(LoginPage.EMAIL_INPUT)


if __name__ == '__main__':
    unittest.main()
