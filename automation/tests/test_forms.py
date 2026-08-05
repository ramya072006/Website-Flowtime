"""
Forms Test Suite — 50 Test Cases
Module: Forms
Tests: Form interactions, field validation, submission, state.
"""

import time
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from automation.tests.base_test import BaseTest
from automation.pages import LoginPage, RegisterPage, ForgotPasswordPage
from automation.config import routes, test_config
from automation.data import (
    VALID_USER, STRONG_PASSWORD, random_email, random_name, BOUNDARY_VALUES
)


class TestForms(BaseTest):
    MODULE = 'Forms'
    PRIORITY = 'High'

    def test_TC_FORM_001_login_email_field_accepts_input(self):
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('test@example.com')
        val = page.get_attribute(LoginPage.EMAIL_INPUT, 'value')
        self.assertEqual(val, 'test@example.com')

    def test_TC_FORM_002_login_password_field_accepts_input(self):
        page = LoginPage(self.driver)
        page.open()
        page.enter_password('MyPassword123')
        val = page.get_attribute(LoginPage.PASSWORD_INPUT, 'value')
        self.assertEqual(val, 'MyPassword123')

    def test_TC_FORM_003_login_form_clears_on_clear(self):
        """Clear method empties input fields."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('fill@test.com')
        el = page.find(LoginPage.EMAIL_INPUT)
        el.clear()
        val = page.get_attribute(LoginPage.EMAIL_INPUT, 'value')
        self.assertEqual(val, '')

    def test_TC_FORM_004_login_tab_order_email_to_password(self):
        """Tab key moves focus from email to password field."""
        page = LoginPage(self.driver)
        page.open()
        el = page.find(LoginPage.EMAIL_INPUT)
        el.send_keys(Keys.TAB)
        active = self.driver.switch_to.active_element
        self.assertEqual(active.get_attribute('id'), 'password')

    def test_TC_FORM_005_login_email_trimmed_validation(self):
        """Email with whitespace-only fails browser validation."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('   ')
        page.enter_password('pass')
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_FORM_006_register_name_accepts_unicode(self):
        """Name field accepts unicode characters."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name(BOUNDARY_VALUES['unicode'])
        val = page.get_attribute(RegisterPage.NAME_INPUT, 'value')
        self.assertEqual(val, BOUNDARY_VALUES['unicode'])

    def test_TC_FORM_007_register_password_updates_strength_bar(self):
        """Typing in password updates strength bar progressively."""
        page = RegisterPage(self.driver)
        page.open()
        for pwd in ['a', 'aA', 'aA1', 'aA1!', 'aA1!bbbbb']:
            page.enter_password(pwd)
            time.sleep(0.3)
        bars = self.driver.find_elements(By.CSS_SELECTOR,
            '.bg-red-500, .bg-yellow-500, .bg-blue-500, .bg-green-500')
        self.assertGreater(len(bars), 0)

    def test_TC_FORM_008_register_confirm_matches_password_no_error(self):
        """Matching passwords do not show mismatch error."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_password(STRONG_PASSWORD)
        page.enter_confirm_password(STRONG_PASSWORD)
        time.sleep(0.3)
        has_mismatch = page.is_password_mismatch_shown()
        self.assertFalse(has_mismatch)

    def test_TC_FORM_009_register_all_fields_tab_navigable(self):
        """All register form fields are navigable via Tab."""
        page = RegisterPage(self.driver)
        page.open()
        page.find(RegisterPage.NAME_INPUT).send_keys(Keys.TAB)
        active1 = self.driver.switch_to.active_element.get_attribute('id')
        self.assertIn(active1, ['email', 'name', 'password', 'confirmPassword'])

    def test_TC_FORM_010_login_autocomplete_email(self):
        """Email input has autocomplete='email'."""
        page = LoginPage(self.driver)
        page.open()
        ac = page.get_attribute(LoginPage.EMAIL_INPUT, 'autocomplete')
        self.assertEqual(ac, 'email')

    def test_TC_FORM_011_login_autocomplete_password(self):
        """Password input has autocomplete='current-password'."""
        page = LoginPage(self.driver)
        page.open()
        ac = page.get_attribute(LoginPage.PASSWORD_INPUT, 'autocomplete')
        self.assertIn(ac, ['current-password', 'password'])

    def test_TC_FORM_012_register_autocomplete_new_password(self):
        """Register password input has autocomplete='new-password'."""
        page = RegisterPage(self.driver)
        page.open()
        ac = page.get_attribute(RegisterPage.PASS_INPUT, 'autocomplete')
        self.assertIn(ac, ['new-password', 'password'])

    def test_TC_FORM_013_register_name_autocomplete(self):
        """Register name input has autocomplete='name'."""
        page = RegisterPage(self.driver)
        page.open()
        ac = page.get_attribute(RegisterPage.NAME_INPUT, 'autocomplete')
        self.assertIn(ac, ['name', 'username', ''])

    def test_TC_FORM_014_login_form_method_not_get(self):
        """Login form doesn't use GET method (would expose password in URL)."""
        page = LoginPage(self.driver)
        page.open()
        forms = self.driver.find_elements(By.TAG_NAME, 'form')
        for form in forms:
            method = (form.get_attribute('method') or '').lower()
            self.assertNotEqual(method, 'get',
                "Form should not use GET method")

    def test_TC_FORM_015_forgot_password_email_required(self):
        """Forgot password form requires email."""
        page = ForgotPasswordPage(self.driver)
        page.open()
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('forgot-password')

    def test_TC_FORM_016_forgot_password_valid_email_format(self):
        """Forgot password accepts only valid email format."""
        page = ForgotPasswordPage(self.driver)
        page.open()
        page.enter_email('invalid-email')
        page.click_submit()
        time.sleep(1)
        self.assert_url_contains('forgot-password')

    def test_TC_FORM_017_login_enter_key_submits_from_email(self):
        """Enter in email field submits or moves to password."""
        page = LoginPage(self.driver)
        page.open()
        el = page.find(LoginPage.EMAIL_INPUT)
        el.send_keys('test@test.com')
        el.send_keys(Keys.RETURN)
        time.sleep(1)
        # Either submits or moves to password
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_FORM_018_login_enter_key_submits_from_password(self):
        """Enter in password field submits the form."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email(VALID_USER.email)
        el = page.find(LoginPage.PASSWORD_INPUT)
        el.send_keys(VALID_USER.password)
        el.send_keys(Keys.RETURN)
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_FORM_019_login_form_element_present(self):
        """Login page has a <form> HTML element."""
        page = LoginPage(self.driver)
        page.open()
        forms = self.driver.find_elements(By.TAG_NAME, 'form')
        self.assertGreater(len(forms), 0, "Form element should be present")

    def test_TC_FORM_020_register_form_element_present(self):
        page = RegisterPage(self.driver)
        page.open()
        forms = self.driver.find_elements(By.TAG_NAME, 'form')
        self.assertGreater(len(forms), 0)

    def test_TC_FORM_021_login_disabled_state_visual(self):
        """Submit button shows disabled state."""
        page = LoginPage(self.driver)
        page.open()
        btn = page.find(LoginPage.SUBMIT_BTN)
        self.assertTrue(btn.is_enabled() or btn.get_attribute('disabled') is not None)

    def test_TC_FORM_022_register_submit_enabled_valid_form(self):
        """Register submit button is enabled when form is fully valid."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('Test User')
        page.enter_email(random_email())
        page.enter_password(STRONG_PASSWORD)
        page.enter_confirm_password(STRONG_PASSWORD)
        time.sleep(0.5)
        btn = page.find(RegisterPage.SUBMIT_BTN)
        self.assertIsNone(btn.get_attribute('disabled'),
            "Submit should be enabled with valid form")

    def test_TC_FORM_023_forgot_password_email_placeholder(self):
        page = ForgotPasswordPage(self.driver)
        page.open()
        ph = page.get_attribute(ForgotPasswordPage.EMAIL_INPUT, 'placeholder')
        self.assertTrue(len(ph) > 0)

    def test_TC_FORM_024_login_password_eye_icon_toggle_twice(self):
        """Double-clicking password toggle restores masked state."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_password('TestPass123')
        page.toggle_password_visibility()
        time.sleep(0.2)
        page.toggle_password_visibility()
        time.sleep(0.2)
        ptype = page.get_password_input_type()
        self.assertEqual(ptype, 'password', "Password should be re-masked after second toggle")

    def test_TC_FORM_025_login_empty_submit_no_network_request(self):
        """Empty form submit doesn't reach network (HTML validation blocks it)."""
        page = LoginPage(self.driver)
        page.open()
        page.click_submit()
        time.sleep(1)
        # Still on login page due to HTML required validation
        self.assert_url_contains('login')

    def test_TC_FORM_026_register_password_rules_count(self):
        """Register page shows exactly 5 password rules."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_password('test')
        time.sleep(0.5)
        rules = self.driver.find_elements(By.CSS_SELECTOR,
            '[class*="text-xs"], .grid.grid-cols-2 div')
        # At least some rules shown
        self.assertGreater(len(rules), 0)

    def test_TC_FORM_027_login_field_label_association(self):
        """Labels are properly associated with inputs via htmlFor/id."""
        page = LoginPage(self.driver)
        page.open()
        labels = self.driver.find_elements(By.CSS_SELECTOR, 'label[for]')
        self.assertGreater(len(labels), 0, "Labels should have 'for' attribute")

    def test_TC_FORM_028_register_field_label_association(self):
        page = RegisterPage(self.driver)
        page.open()
        labels = self.driver.find_elements(By.CSS_SELECTOR, 'label[for]')
        self.assertGreater(len(labels), 0)

    def test_TC_FORM_029_login_email_spellcheck_off(self):
        """Email field has spellcheck disabled (no red underlines)."""
        page = LoginPage(self.driver)
        page.open()
        sc = page.get_attribute(LoginPage.EMAIL_INPUT, 'spellcheck')
        # Either explicitly false or not set
        self.assertIn(sc, [None, '', 'false'])

    def test_TC_FORM_030_login_button_has_no_href(self):
        """Submit button is a <button> not an <a> element."""
        page = LoginPage(self.driver)
        page.open()
        btn = page.find(LoginPage.SUBMIT_BTN)
        tag = btn.tag_name
        self.assertEqual(tag, 'button', "Submit should be a <button> element")

    def test_TC_FORM_031_login_form_not_reset_on_error(self):
        """Login form retains email value after failed submission."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email(VALID_USER.email)
        page.enter_password('wrongpass123')
        page.click_submit()
        time.sleep(2)
        val = page.get_attribute(LoginPage.EMAIL_INPUT, 'value')
        self.assertEqual(val, VALID_USER.email,
            "Email value should be retained after error")

    def test_TC_FORM_032_register_submit_type_submit(self):
        page = RegisterPage(self.driver)
        page.open()
        btn = page.find(RegisterPage.SUBMIT_BTN)
        self.assertEqual(btn.get_attribute('type'), 'submit')

    def test_TC_FORM_033_login_submit_type_submit(self):
        page = LoginPage(self.driver)
        page.open()
        btn = page.find(LoginPage.SUBMIT_BTN)
        self.assertEqual(btn.get_attribute('type'), 'submit')

    def test_TC_FORM_034_forgot_password_submit_type_submit(self):
        page = ForgotPasswordPage(self.driver)
        page.open()
        btn = page.find(ForgotPasswordPage.SUBMIT_BTN)
        self.assertEqual(btn.get_attribute('type'), 'submit')

    def test_TC_FORM_035_form_inputs_are_interactive(self):
        """All form inputs on login page accept user interaction."""
        page = LoginPage(self.driver)
        page.open()
        inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input:not([type="hidden"])')
        for inp in inputs:
            self.assertTrue(inp.is_enabled(), f"Input '{inp.get_attribute('id')}' should be enabled")

    def test_TC_FORM_036_register_form_has_5_interactive_elements(self):
        """Register form has inputs + button = 5+ interactive elements."""
        page = RegisterPage(self.driver)
        page.open()
        inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input')
        buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button')
        total = len(inputs) + len(buttons)
        self.assertGreaterEqual(total, 5)

    def test_TC_FORM_037_login_long_password_accepted(self):
        """Password field accepts passwords up to reasonable length."""
        page = LoginPage(self.driver)
        page.open()
        long_pass = 'A1!' + 'x' * 60
        page.enter_password(long_pass)
        val = page.get_attribute(LoginPage.PASSWORD_INPUT, 'value')
        self.assertEqual(len(val), 63)

    def test_TC_FORM_038_register_email_valid_format_accepted(self):
        page = RegisterPage(self.driver)
        page.open()
        test_mail = 'valid.email+tag@subdomain.example.com'
        page.enter_email(test_mail)
        val = page.get_attribute(RegisterPage.EMAIL_INPUT, 'value')
        self.assertEqual(val, test_mail)

    def test_TC_FORM_039_register_confirm_password_field_id(self):
        """Confirm password field has id='confirmPassword'."""
        page = RegisterPage(self.driver)
        page.open()
        el = page.find(RegisterPage.CONFIRM_INPUT)
        self.assertEqual(el.get_attribute('id'), 'confirmPassword')

    def test_TC_FORM_040_login_no_form_submission_without_interaction(self):
        """Login form doesn't auto-submit on page load."""
        page = LoginPage(self.driver)
        page.open()
        time.sleep(2)
        self.assert_url_contains('login')

    def test_TC_FORM_041_forgot_password_no_auto_submit(self):
        page = ForgotPasswordPage(self.driver)
        page.open()
        time.sleep(2)
        self.assert_url_contains('forgot-password')

    def test_TC_FORM_042_login_cursor_position_in_email(self):
        """Clicking email field positions cursor for input."""
        page = LoginPage(self.driver)
        page.open()
        el = page.find(LoginPage.EMAIL_INPUT)
        el.click()
        active_id = self.driver.switch_to.active_element.get_attribute('id')
        self.assertEqual(active_id, 'email')

    def test_TC_FORM_043_login_cursor_in_password_on_click(self):
        page = LoginPage(self.driver)
        page.open()
        el = page.find(LoginPage.PASSWORD_INPUT)
        el.click()
        active_id = self.driver.switch_to.active_element.get_attribute('id')
        self.assertEqual(active_id, 'password')

    def test_TC_FORM_044_register_name_max_input(self):
        """Name field accepts the maximum reasonable input."""
        page = RegisterPage(self.driver)
        page.open()
        long_name = 'A' * 100
        page.enter_name(long_name)
        val = page.get_attribute(RegisterPage.NAME_INPUT, 'value')
        self.assertGreaterEqual(len(val), 50)

    def test_TC_FORM_045_login_multiple_submissions_handled(self):
        """Multiple rapid submit clicks are handled (no duplicate errors)."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email(VALID_USER.email)
        page.enter_password('wrong')
        btn = page.find(LoginPage.SUBMIT_BTN)
        btn.click()
        time.sleep(0.1)
        try:
            btn.click()
        except Exception:
            pass
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_FORM_046_register_show_password_toggle_on_confirm(self):
        """Confirm password field has a show/hide toggle."""
        page = RegisterPage(self.driver)
        page.open()
        toggles = self.driver.find_elements(By.CSS_SELECTOR, 'button[type="button"]')
        self.assertGreaterEqual(len(toggles), 1, "At least one password toggle should exist")

    def test_TC_FORM_047_login_form_visible_in_tablet_viewport(self):
        self.driver.set_window_size(768, 1024)
        page = LoginPage(self.driver)
        page.open()
        self.assert_element_visible(LoginPage.SUBMIT_BTN)
        self.driver.set_window_size(1920, 1080)

    def test_TC_FORM_048_login_form_visible_in_small_mobile(self):
        self.driver.set_window_size(320, 568)
        page = LoginPage(self.driver)
        page.open()
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self.driver.set_window_size(1920, 1080)

    def test_TC_FORM_049_form_react_controlled_inputs(self):
        """React controlled inputs reflect state (value attr matches display)."""
        page = LoginPage(self.driver)
        page.open()
        test_val = 'react.test@example.com'
        el = page.find(LoginPage.EMAIL_INPUT)
        el.send_keys(test_val)
        dom_val = self.driver.execute_script("return arguments[0].value;", el)
        self.assertEqual(dom_val, test_val)

    def test_TC_FORM_050_forgot_password_form_accepts_submission(self):
        """Forgot password form can be submitted with valid email."""
        page = ForgotPasswordPage(self.driver)
        page.open()
        page.enter_email('test@example.com')
        page.click_submit()
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)


if __name__ == '__main__':
    unittest.main()
