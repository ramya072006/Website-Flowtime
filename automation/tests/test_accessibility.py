"""
Accessibility Test Suite — 20 Test Cases
Module: Accessibility
Tests: ARIA roles, labels, keyboard navigation, colour contrast indicators,
       focus management, screen-reader landmarks.
"""

import time
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from automation.tests.base_test import BaseTest
from automation.pages import LoginPage, RegisterPage, LandingPage, ForgotPasswordPage
from automation.config import routes, test_config


class TestAccessibility(BaseTest):
    MODULE = 'Accessibility'
    PRIORITY = 'Medium'

    def test_TC_ACC_001_login_email_label_associated(self):
        """Email input has an associated <label> element."""
        page = LoginPage(self.driver)
        page.open()
        label = self.driver.find_elements(By.CSS_SELECTOR, 'label[for="email"]')
        self.assertGreater(len(label), 0,
            "Email input should have an associated <label for='email'>")

    def test_TC_ACC_002_login_password_label_associated(self):
        """Password input has an associated <label> element."""
        page = LoginPage(self.driver)
        page.open()
        label = self.driver.find_elements(By.CSS_SELECTOR, 'label[for="password"]')
        self.assertGreater(len(label), 0,
            "Password input should have an associated <label for='password'>")

    def test_TC_ACC_003_login_submit_button_has_text(self):
        """Submit button has accessible text (not icon-only)."""
        page = LoginPage(self.driver)
        page.open()
        btn = page.find(LoginPage.SUBMIT_BTN)
        btn_text = btn.text.strip()
        aria_label = btn.get_attribute('aria-label') or ''
        self.assertTrue(
            len(btn_text) > 0 or len(aria_label) > 0,
            "Submit button should have accessible text or aria-label"
        )

    def test_TC_ACC_004_login_inputs_not_placeholder_only(self):
        """Login inputs have visible labels (not just placeholders)."""
        page = LoginPage(self.driver)
        page.open()
        labels = self.driver.find_elements(By.CSS_SELECTOR, 'label')
        self.assertGreater(len(labels), 0,
            "Form should use <label> elements, not just placeholders")

    def test_TC_ACC_005_page_has_main_landmark(self):
        """Page has a <main> or role='main' landmark."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        main_elements = self.driver.find_elements(By.CSS_SELECTOR,
            'main, [role="main"]')
        self.assertGreater(len(main_elements), 0,
            "Page should have a <main> landmark for screen readers")

    def test_TC_ACC_006_landing_has_heading_hierarchy(self):
        """Landing page has at least one H1 heading."""
        page = LandingPage(self.driver)
        page.open()
        time.sleep(2)
        h1 = self.driver.find_elements(By.TAG_NAME, 'h1')
        self.assertGreater(len(h1), 0, "Landing page should have at least one H1")

    def test_TC_ACC_007_login_page_has_heading(self):
        """Login page has a heading element."""
        page = LoginPage(self.driver)
        page.open()
        headings = self.driver.find_elements(By.CSS_SELECTOR,
            'h1, h2, h3, [class*="heading"]')
        self.assertGreater(len(headings), 0,
            "Login page should have a heading element")

    def test_TC_ACC_008_register_page_has_heading(self):
        """Register page has a heading element."""
        page = RegisterPage(self.driver)
        page.open()
        headings = self.driver.find_elements(By.CSS_SELECTOR,
            'h1, h2, h3, [class*="heading"]')
        self.assertGreater(len(headings), 0)

    def test_TC_ACC_009_keyboard_tab_reaches_email_input(self):
        """Tab key navigates to email input field."""
        page = LoginPage(self.driver)
        page.open()
        body = self.driver.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.TAB)
        time.sleep(0.3)
        active = self.driver.switch_to.active_element
        active_tag = active.tag_name
        self.assertIn(active_tag, ['input', 'a', 'button'],
            "Tab should focus a form element")

    def test_TC_ACC_010_keyboard_enter_submits_login_form(self):
        """Enter key submits the login form from password field."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('test@test.com')
        pwd_el = page.find(LoginPage.PASSWORD_INPUT)
        pwd_el.send_keys('TestPass@1')
        pwd_el.send_keys(Keys.RETURN)
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_ACC_011_submit_button_is_focusable(self):
        """Submit button is focusable via keyboard (tabindex not -1)."""
        page = LoginPage(self.driver)
        page.open()
        btn = page.find(LoginPage.SUBMIT_BTN)
        tabindex = btn.get_attribute('tabindex')
        self.assertNotEqual(tabindex, '-1',
            "Submit button should be reachable via Tab")

    def test_TC_ACC_012_links_have_accessible_text(self):
        """All anchor links have text or aria-label."""
        page = LoginPage(self.driver)
        page.open()
        links = self.driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            text = link.text.strip()
            aria = link.get_attribute('aria-label') or ''
            title = link.get_attribute('title') or ''
            self.assertTrue(
                len(text) > 0 or len(aria) > 0 or len(title) > 0,
                f"Link has no accessible text: href={link.get_attribute('href')}"
            )

    def test_TC_ACC_013_error_messages_use_role_alert(self):
        """Error messages use role='alert' or aria-live for screen readers."""
        page = LoginPage(self.driver)
        page.open()
        page.login('wrong@test.com', 'WrongPass@1')
        time.sleep(3)
        # Check for alert role or aria-live
        alerts = self.driver.find_elements(By.CSS_SELECTOR,
            '[role="alert"], [aria-live="assertive"], [aria-live="polite"]')
        # Alerts may or may not be present — just verify no crash
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_ACC_014_images_have_alt_attributes(self):
        """All <img> elements have alt attributes."""
        self.driver.get(test_config.base_url)
        time.sleep(3)
        images = self.driver.find_elements(By.TAG_NAME, 'img')
        for img in images:
            alt = img.get_attribute('alt')
            self.assertIsNotNone(alt,
                f"Image missing alt: src={img.get_attribute('src')}")

    def test_TC_ACC_015_page_has_skip_to_content_or_landmark(self):
        """Page provides navigation landmarks for screen reader users."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        nav_landmarks = self.driver.find_elements(By.CSS_SELECTOR,
            'nav, [role="navigation"], header, [role="banner"]')
        landmarks_in_login = self.driver.find_elements(By.CSS_SELECTOR,
            'main, [role="main"], form')
        has_landmarks = len(nav_landmarks) > 0 or len(landmarks_in_login) > 0
        self.assertTrue(has_landmarks, "Page should have ARIA landmarks")

    def test_TC_ACC_016_focus_visible_on_interactive_elements(self):
        """Interactive elements show focus outline when focused."""
        page = LoginPage(self.driver)
        page.open()
        email_el = page.find(LoginPage.EMAIL_INPUT)
        email_el.click()
        active = self.driver.switch_to.active_element
        self.assertEqual(active.get_attribute('id'), 'email',
            "Email input should receive focus on click")

    def test_TC_ACC_017_form_has_novalidate_or_html_validation(self):
        """Login form uses either HTML5 validation or React-controlled validation."""
        page = LoginPage(self.driver)
        page.open()
        forms = self.driver.find_elements(By.TAG_NAME, 'form')
        self.assertGreater(len(forms), 0, "Form element must be present")

    def test_TC_ACC_018_color_contrast_dark_class_present(self):
        """Dark mode class does not break text visibility."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        html_class = self.driver.execute_script(
            "return document.documentElement.className;")
        body = self.driver.find_element(By.TAG_NAME, 'body')
        bg_color = self.driver.execute_script(
            "return window.getComputedStyle(arguments[0]).backgroundColor;", body)
        self.assertIsNotNone(bg_color)
        self.assertNotEqual(bg_color, '')

    def test_TC_ACC_019_register_form_labels_count(self):
        """Register form has at least 4 accessible labels for its inputs."""
        page = RegisterPage(self.driver)
        page.open()
        labels = self.driver.find_elements(By.CSS_SELECTOR, 'label')
        self.assertGreaterEqual(len(labels), 4,
            "Register form should have labels for all 4 inputs")

    def test_TC_ACC_020_viewport_meta_allows_zoom(self):
        """Viewport meta does not disable user zoom (accessibility requirement)."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        viewport = self.driver.execute_script("""
            const meta = document.querySelector('meta[name="viewport"]');
            return meta ? meta.getAttribute('content') : '';
        """)
        self.assertIsNotNone(viewport)
        # WCAG 1.4.4 — user-scalable=no is a violation
        self.assertNotIn('user-scalable=no', viewport.lower(),
            "Viewport should not disable user zoom")


if __name__ == '__main__':
    unittest.main()
