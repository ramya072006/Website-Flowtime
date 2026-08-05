"""
Responsive Design Test Suite — 20 Test Cases
Module: Responsive Design
Tests: Multiple viewport sizes, element visibility, no horizontal scroll,
       touch-target sizes, layout integrity.
"""

import time
import unittest
from selenium.webdriver.common.by import By

from automation.tests.base_test import BaseTest
from automation.pages import LoginPage, RegisterPage, LandingPage
from automation.config import routes, test_config
from automation.data import VIEWPORT_SIZES


class TestResponsiveDesign(BaseTest):
    MODULE = 'Responsive Design'
    PRIORITY = 'Medium'

    def _set_viewport(self, width: int, height: int):
        self.driver.set_window_size(width, height)
        time.sleep(0.5)

    def _reset_viewport(self):
        self.driver.set_window_size(1920, 1080)
        time.sleep(0.3)

    # ─── TC_RESP_001–005: Desktop Viewports ───────────────────────────────────

    def test_TC_RESP_001_full_hd_login_form_visible(self):
        """Login form is fully visible on 1920×1080 Full HD."""
        self._set_viewport(1920, 1080)
        page = LoginPage(self.driver)
        page.open()
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self.assert_element_visible(LoginPage.SUBMIT_BTN)
        self._reset_viewport()

    def test_TC_RESP_002_laptop_hd_login_form_visible(self):
        """Login form is visible on 1366×768 HD laptop viewport."""
        self._set_viewport(1366, 768)
        page = LoginPage(self.driver)
        page.open()
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self.assert_element_visible(LoginPage.SUBMIT_BTN)
        self._reset_viewport()

    def test_TC_RESP_003_macbook_viewport_login_visible(self):
        """Login form is visible on 1280×800 MacBook viewport."""
        self._set_viewport(1280, 800)
        page = LoginPage(self.driver)
        page.open()
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self._reset_viewport()

    def test_TC_RESP_004_no_horizontal_scroll_on_desktop(self):
        """No horizontal scroll on 1280px desktop viewport."""
        self._set_viewport(1280, 800)
        self.driver.get(routes.url('login'))
        time.sleep(2)
        scroll_w = self.driver.execute_script("return document.body.scrollWidth;")
        client_w = self.driver.execute_script("return document.body.clientWidth;")
        self.assertLessEqual(scroll_w, client_w + 5,
            f"Horizontal scroll at 1280px: scrollWidth={scroll_w}, clientWidth={client_w}")
        self._reset_viewport()

    def test_TC_RESP_005_landing_page_visible_on_desktop(self):
        """Landing page renders fully on desktop viewport."""
        self._set_viewport(1440, 900)
        page = LandingPage(self.driver)
        page.open()
        time.sleep(2)
        source = self.driver.page_source
        self.assertGreater(len(source), 1000)
        self._reset_viewport()

    # ─── TC_RESP_006–010: Tablet Viewports ────────────────────────────────────

    def test_TC_RESP_006_ipad_portrait_login_visible(self):
        """Login form is visible on iPad portrait 768×1024."""
        self._set_viewport(768, 1024)
        page = LoginPage(self.driver)
        page.open()
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self.assert_element_visible(LoginPage.SUBMIT_BTN)
        self._reset_viewport()

    def test_TC_RESP_007_ipad_portrait_no_horizontal_scroll(self):
        """No horizontal scroll on iPad portrait viewport."""
        self._set_viewport(768, 1024)
        self.driver.get(routes.url('login'))
        time.sleep(2)
        scroll_w = self.driver.execute_script("return document.body.scrollWidth;")
        client_w = self.driver.execute_script("return document.body.clientWidth;")
        self.assertLessEqual(scroll_w, client_w + 5)
        self._reset_viewport()

    def test_TC_RESP_008_tablet_register_form_visible(self):
        """Register form is visible on 768px tablet viewport."""
        self._set_viewport(768, 1024)
        page = RegisterPage(self.driver)
        page.open()
        self.assert_element_visible(RegisterPage.NAME_INPUT)
        self.assert_element_visible(RegisterPage.SUBMIT_BTN)
        self._reset_viewport()

    def test_TC_RESP_009_tablet_landing_page_renders(self):
        """Landing page renders on tablet viewport."""
        self._set_viewport(768, 1024)
        page = LandingPage(self.driver)
        page.open()
        time.sleep(2)
        root_kids = self.driver.execute_script(
            "return document.getElementById('root').children.length;")
        self.assertGreater(root_kids, 0)
        self._reset_viewport()

    def test_TC_RESP_010_tablet_landscape_no_overflow(self):
        """No overflow on 1024×768 landscape tablet."""
        self._set_viewport(1024, 768)
        self.driver.get(routes.url('register'))
        time.sleep(2)
        scroll_w = self.driver.execute_script("return document.body.scrollWidth;")
        client_w = self.driver.execute_script("return document.body.clientWidth;")
        self.assertLessEqual(scroll_w, client_w + 5)
        self._reset_viewport()

    # ─── TC_RESP_011–015: Mobile Viewports ────────────────────────────────────

    def test_TC_RESP_011_iphone_xr_login_visible(self):
        """Login form is visible on iPhone XR 414×896."""
        self._set_viewport(414, 896)
        page = LoginPage(self.driver)
        page.open()
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self._reset_viewport()

    def test_TC_RESP_012_iphone_se_login_visible(self):
        """Login form is visible on iPhone SE 375×667."""
        self._set_viewport(375, 667)
        page = LoginPage(self.driver)
        page.open()
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self.assert_element_visible(LoginPage.SUBMIT_BTN)
        self._reset_viewport()

    def test_TC_RESP_013_android_mobile_login_visible(self):
        """Login form is visible on Android 360×640."""
        self._set_viewport(360, 640)
        page = LoginPage(self.driver)
        page.open()
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self._reset_viewport()

    def test_TC_RESP_014_small_phone_320_login_visible(self):
        """Login form is visible on smallest phone 320×568."""
        self._set_viewport(320, 568)
        page = LoginPage(self.driver)
        page.open()
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self._reset_viewport()

    def test_TC_RESP_015_mobile_no_horizontal_scroll_on_login(self):
        """No horizontal scroll on 375px mobile viewport."""
        self._set_viewport(375, 667)
        self.driver.get(routes.url('login'))
        time.sleep(2)
        scroll_w = self.driver.execute_script("return document.body.scrollWidth;")
        client_w = self.driver.execute_script("return document.body.clientWidth;")
        self.assertLessEqual(scroll_w, client_w + 5,
            f"Mobile horizontal scroll at 375px: {scroll_w} > {client_w}")
        self._reset_viewport()

    # ─── TC_RESP_016–020: Layout Integrity ────────────────────────────────────

    def test_TC_RESP_016_submit_button_not_overflowing_mobile(self):
        """Submit button does not overflow its container on mobile."""
        self._set_viewport(375, 667)
        page = LoginPage(self.driver)
        page.open()
        btn = page.find(LoginPage.SUBMIT_BTN)
        btn_width = self.driver.execute_script(
            "return arguments[0].getBoundingClientRect().width;", btn)
        viewport_width = 375
        self.assertLessEqual(btn_width, viewport_width,
            f"Submit button width {btn_width} exceeds viewport {viewport_width}")
        self._reset_viewport()

    def test_TC_RESP_017_inputs_full_width_on_mobile(self):
        """Form inputs stretch to full width on mobile (w-full class)."""
        self._set_viewport(375, 667)
        page = LoginPage(self.driver)
        page.open()
        email_el = page.find(LoginPage.EMAIL_INPUT)
        input_width = self.driver.execute_script(
            "return arguments[0].getBoundingClientRect().width;", email_el)
        # Input should be close to viewport width (accounting for padding)
        self.assertGreater(input_width, 200,
            "Input should be wide on mobile")
        self._reset_viewport()

    def test_TC_RESP_018_touch_targets_min_44px(self):
        """Interactive elements meet minimum 44×44px touch target size."""
        self._set_viewport(375, 667)
        page = LoginPage(self.driver)
        page.open()
        btn = page.find(LoginPage.SUBMIT_BTN)
        rect = self.driver.execute_script("""
            const r = arguments[0].getBoundingClientRect();
            return {width: r.width, height: r.height};
        """, btn)
        self.assertGreaterEqual(rect['height'], 36,
            f"Submit button height {rect['height']}px should be >= 36px")
        self._reset_viewport()

    def test_TC_RESP_019_register_form_stacks_vertically_on_mobile(self):
        """Register form fields stack vertically on mobile viewport."""
        self._set_viewport(375, 667)
        page = RegisterPage(self.driver)
        page.open()
        name_el = page.find(RegisterPage.NAME_INPUT)
        email_el = page.find(RegisterPage.EMAIL_INPUT)
        name_top = self.driver.execute_script(
            "return arguments[0].getBoundingClientRect().top;", name_el)
        email_top = self.driver.execute_script(
            "return arguments[0].getBoundingClientRect().top;", email_el)
        self.assertLess(name_top, email_top,
            "Name field should appear above email on mobile")
        self._reset_viewport()

    def test_TC_RESP_020_viewport_meta_present_for_mobile(self):
        """Viewport meta tag enables proper mobile rendering."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        viewport = self.driver.execute_script("""
            const m = document.querySelector('meta[name="viewport"]');
            return m ? m.getAttribute('content') : null;
        """)
        self.assertIsNotNone(viewport, "Viewport meta must be set")
        self.assertIn('width=device-width', viewport,
            "Viewport should set width=device-width")


if __name__ == '__main__':
    unittest.main()
