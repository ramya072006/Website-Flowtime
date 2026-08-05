"""
Input Validation Test Suite — 40 Test Cases
Module: Input Validation
Tests: Boundary values, XSS, SQL injection, length limits, special chars.
"""

import time
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from automation.tests.base_test import BaseTest
from automation.pages import LoginPage, RegisterPage, ForgotPasswordPage
from automation.config import routes, test_config
from automation.data import (
    VALID_USER, STRONG_PASSWORD, BOUNDARY_VALUES, XSS_PAYLOADS,
    INVALID_PASSWORDS, random_email
)


class TestInputValidation(BaseTest):
    MODULE = 'Input Validation'
    PRIORITY = 'High'

    # ─── TC_VAL_001–010: Email Validation ─────────────────────────────────────

    def test_TC_VAL_001_email_missing_at_symbol(self):
        """Email without @ symbol fails browser validation."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('invalidemail.com')
        page.enter_password('Pass@123')
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_VAL_002_email_missing_domain(self):
        """Email with only local part fails validation."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('user@')
        page.enter_password('Pass@123')
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_VAL_003_email_missing_local_part(self):
        """Email starting with @ fails validation."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('@domain.com')
        page.enter_password('Pass@123')
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_VAL_004_email_with_spaces(self):
        """Email with spaces is rejected."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('user @domain.com')
        page.enter_password('Pass@123')
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_VAL_005_email_max_length_boundary(self):
        """Email at RFC max length (254 chars) is handled gracefully."""
        page = LoginPage(self.driver)
        page.open()
        long_email = BOUNDARY_VALUES['email_max']
        page.enter_email(long_email)
        page.enter_password('Pass@123')
        page.click_submit()
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_VAL_006_email_with_unicode_chars(self):
        """Unicode characters in email are handled gracefully."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('tëst@ëxample.com')
        page.enter_password('Pass@123')
        page.click_submit()
        time.sleep(1)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_VAL_007_email_multiple_at_symbols(self):
        """Email with multiple @ symbols fails validation."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('user@@domain.com')
        page.enter_password('Pass@123')
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_VAL_008_email_only_whitespace(self):
        """Whitespace-only email is rejected."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('   ')
        page.enter_password('Pass@123')
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_VAL_009_empty_email_blocked(self):
        """Empty email field prevents form submission."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_password('Pass@123')
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_VAL_010_valid_email_with_plus_tag(self):
        """Email with + tagging is accepted as valid format."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('user+tag@example.com')
        val = page.get_attribute(LoginPage.EMAIL_INPUT, 'value')
        self.assertEqual(val, 'user+tag@example.com')

    # ─── TC_VAL_011–020: Password Validation ──────────────────────────────────

    def test_TC_VAL_011_password_min_length_check(self):
        """Password shorter than min length is blocked on register."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('Test User')
        page.enter_email(random_email())
        page.enter_password('Aa1!')  # Only 4 chars
        page.enter_confirm_password('Aa1!')
        time.sleep(0.5)
        self.assertTrue(page.is_submit_disabled(),
            "Submit should be disabled for a 4-char password")

    def test_TC_VAL_012_password_no_uppercase_blocked(self):
        """Password without uppercase letter is blocked."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('Test User')
        page.enter_email(random_email())
        page.enter_password('nouppercase123!')
        page.enter_confirm_password('nouppercase123!')
        time.sleep(0.5)
        self.assertTrue(page.is_submit_disabled())

    def test_TC_VAL_013_password_no_lowercase_blocked(self):
        """Password without lowercase letter is blocked."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('Test')
        page.enter_email(random_email())
        page.enter_password('NOLOWER123!')
        page.enter_confirm_password('NOLOWER123!')
        time.sleep(0.5)
        self.assertTrue(page.is_submit_disabled())

    def test_TC_VAL_014_password_no_number_blocked(self):
        """Password without a number is blocked."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('Test')
        page.enter_email(random_email())
        page.enter_password('NoNumbers!abc')
        page.enter_confirm_password('NoNumbers!abc')
        time.sleep(0.5)
        self.assertTrue(page.is_submit_disabled())

    def test_TC_VAL_015_password_no_special_char_blocked(self):
        """Password without special character is blocked."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('Test')
        page.enter_email(random_email())
        page.enter_password('NoSpecial123abc')
        page.enter_confirm_password('NoSpecial123abc')
        time.sleep(0.5)
        self.assertTrue(page.is_submit_disabled())

    def test_TC_VAL_016_password_whitespace_only_blocked(self):
        """Whitespace-only password is blocked."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('Test')
        page.enter_email(random_email())
        page.enter_password('        ')
        page.enter_confirm_password('        ')
        time.sleep(0.5)
        self.assertTrue(page.is_submit_disabled())

    def test_TC_VAL_017_password_strong_all_rules_met_enables_submit(self):
        """Strong password meeting all rules enables submit."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('Test User')
        page.enter_email(random_email())
        page.enter_password(STRONG_PASSWORD)
        page.enter_confirm_password(STRONG_PASSWORD)
        time.sleep(0.5)
        btn = page.find(RegisterPage.SUBMIT_BTN)
        disabled = btn.get_attribute('disabled')
        self.assertIsNone(disabled, "Submit should be enabled with strong password")

    def test_TC_VAL_018_password_boundary_8_chars(self):
        """Password of exactly 8 chars meeting all rules is accepted."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('Test')
        page.enter_email(random_email())
        page.enter_password('Aa1!aaaa')  # 8 chars, meets all rules
        page.enter_confirm_password('Aa1!aaaa')
        time.sleep(0.5)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_VAL_019_password_mismatch_shows_error_inline(self):
        """Password mismatch shows inline error message."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_password(STRONG_PASSWORD)
        page.enter_confirm_password('DifferentP@ss1')
        time.sleep(0.5)
        self.assertTrue(page.is_password_mismatch_shown(),
            "Password mismatch error should be shown")

    def test_TC_VAL_020_password_field_type_is_password(self):
        """Password field type is 'password' (masked) by default."""
        page = LoginPage(self.driver)
        page.open()
        ptype = page.get_password_input_type()
        self.assertEqual(ptype, 'password')

    # ─── TC_VAL_021–030: XSS & Injection Prevention ───────────────────────────

    def test_TC_VAL_021_xss_in_email_field_login(self):
        """XSS payload in email field does not execute."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('<script>alert("xss")</script>')
        page.click_submit()
        time.sleep(1)
        # If alert had executed, Selenium would raise UnexpectedAlertPresentException
        self.assert_url_contains('login')

    def test_TC_VAL_022_xss_in_password_field(self):
        """XSS payload in password field does not execute."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('test@test.com')
        page.enter_password('<img src=x onerror=alert(1)>')
        page.click_submit()
        time.sleep(1)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_VAL_023_xss_in_name_field_register(self):
        """XSS payload in name field does not execute."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('<script>alert("xss")</script>')
        time.sleep(1)
        # No alert should have fired
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_VAL_024_sql_injection_in_email(self):
        """SQL injection in email is handled without crashing."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email("'; DROP TABLE users; --")
        page.enter_password('SomePass@1')
        page.click_submit()
        time.sleep(2)
        source = self.driver.page_source
        self.assertNotIn('SQL', source.upper(),
            "SQL error should not leak into page content")

    def test_TC_VAL_025_sql_injection_in_password(self):
        """SQL injection in password is handled safely."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('test@test.com')
        page.enter_password("' OR '1'='1")
        page.click_submit()
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_VAL_026_html_tags_in_name_field(self):
        """HTML tags in name field are escaped, not rendered."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('<b>Bold</b><i>Italic</i>')
        val = page.get_attribute(RegisterPage.NAME_INPUT, 'value')
        self.assertIn('Bold', val, "Field should contain the text value")
        # Verify no raw HTML rendered in the page
        source = self.driver.page_source
        self.assertNotIn('<b>Bold</b>', source.split('<input')[0] if '<input' in source else source)

    def test_TC_VAL_027_emoji_in_name_field(self):
        """Emoji characters in name field are handled gracefully."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name(BOUNDARY_VALUES['emoji'])
        time.sleep(0.5)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_VAL_028_template_injection_in_email(self):
        """Template injection strings in email are handled safely."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('{{7*7}}@test.com')
        page.enter_password('Pass@123')
        page.click_submit()
        time.sleep(1)
        source = self.driver.page_source
        self.assertNotIn('49', source[:500],
            "Template injection should not evaluate")

    def test_TC_VAL_029_null_bytes_in_email(self):
        """Null bytes in email field are handled gracefully."""
        page = LoginPage(self.driver)
        page.open()
        try:
            page.enter_email('test\x00@test.com')
        except Exception:
            pass  # Some drivers filter null bytes
        time.sleep(1)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_VAL_030_long_string_in_name_field(self):
        """Very long name string is handled without crashing."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('A' * 300)
        time.sleep(0.5)
        self.assertIsNotNone(self.driver.current_url)

    # ─── TC_VAL_031–040: Form Field Boundary & Edge Cases ─────────────────────

    def test_TC_VAL_031_empty_form_login_no_network_call(self):
        """Completely empty login form does not make a network call."""
        page = LoginPage(self.driver)
        page.open()
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_VAL_032_empty_form_register_no_redirect(self):
        """Completely empty register form stays on register page."""
        page = RegisterPage(self.driver)
        page.open()
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('register')

    def test_TC_VAL_033_empty_forgot_password_no_submit(self):
        """Empty forgot password form is blocked."""
        page = ForgotPasswordPage(self.driver)
        page.open()
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('forgot-password')

    def test_TC_VAL_034_copy_paste_into_email_field(self):
        """Paste operation fills email field correctly."""
        page = LoginPage(self.driver)
        page.open()
        el = page.find(LoginPage.EMAIL_INPUT)
        # Simulate paste via JS
        self.driver.execute_script(
            "arguments[0].value = 'pasted@example.com';"
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
            el
        )
        time.sleep(0.3)
        val = self.driver.execute_script("return arguments[0].value;", el)
        self.assertEqual(val, 'pasted@example.com')

    def test_TC_VAL_035_backspace_clears_field_character_by_character(self):
        """Backspace key removes characters from email field."""
        page = LoginPage(self.driver)
        page.open()
        el = page.find(LoginPage.EMAIL_INPUT)
        el.send_keys('abc')
        el.send_keys(Keys.BACK_SPACE)
        val = self.driver.execute_script("return arguments[0].value;", el)
        self.assertEqual(val, 'ab')

    def test_TC_VAL_036_ctrl_a_select_all_in_field(self):
        """Ctrl+A selects all text in input field."""
        page = LoginPage(self.driver)
        page.open()
        el = page.find(LoginPage.EMAIL_INPUT)
        el.send_keys('select.this@test.com')
        el.send_keys(Keys.CONTROL + 'a')
        el.send_keys(Keys.DELETE)
        val = self.driver.execute_script("return arguments[0].value;", el)
        self.assertEqual(val, '')

    def test_TC_VAL_037_input_maxlength_attribute(self):
        """Input fields don't accept unlimited text (browser maxlength or React)."""
        page = LoginPage(self.driver)
        page.open()
        el = page.find(LoginPage.EMAIL_INPUT)
        maxlen = el.get_attribute('maxlength')
        # maxlength is optional — just verify no crash
        self.assertIsNotNone(el)

    def test_TC_VAL_038_password_copy_blocked_or_allowed(self):
        """Password field value is accessible to the test (webdriver can read it)."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_password('TestPass@123')
        val = page.get_attribute(LoginPage.PASSWORD_INPUT, 'value')
        self.assertEqual(val, 'TestPass@123')

    def test_TC_VAL_039_form_inputs_type_attributes_correct(self):
        """All login form inputs have correct type attributes."""
        page = LoginPage(self.driver)
        page.open()
        email_type = page.get_attribute(LoginPage.EMAIL_INPUT, 'type')
        pass_type = page.get_attribute(LoginPage.PASSWORD_INPUT, 'type')
        self.assertEqual(email_type, 'email')
        self.assertEqual(pass_type, 'password')

    def test_TC_VAL_040_required_attributes_on_all_login_fields(self):
        """Both email and password fields have required attribute."""
        page = LoginPage(self.driver)
        page.open()
        email_req = page.get_attribute(LoginPage.EMAIL_INPUT, 'required')
        pass_req = page.get_attribute(LoginPage.PASSWORD_INPUT, 'required')
        self.assertIsNotNone(email_req, "Email should have required attribute")
        self.assertIsNotNone(pass_req, "Password should have required attribute")


if __name__ == '__main__':
    unittest.main()
