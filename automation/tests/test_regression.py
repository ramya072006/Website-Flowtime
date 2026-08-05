"""
Regression Test Suite — 50 Test Cases
Module: Regression
Tests: Cross-cutting regression checks ensuring prior fixes remain stable.
Covers: UI consistency, auth flows, navigation, form behaviour,
        SPA routing, security, and deployment health.
"""

import time
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from automation.tests.base_test import BaseTest
from automation.pages import (
    LoginPage, RegisterPage, ForgotPasswordPage, LandingPage
)
from automation.config import routes, test_config
from automation.data import (
    VALID_USER, STRONG_PASSWORD, BOUNDARY_VALUES,
    random_email, random_name
)


class TestRegression(BaseTest):
    MODULE = 'Regression'
    PRIORITY = 'Critical'

    # ─── TC_REG_001–010: Authentication Regression ────────────────────────────

    def test_TC_REG_001_login_page_still_at_correct_route(self):
        """Regression: /login route still renders the login form."""
        page = LoginPage(self.driver)
        page.open()
        self.assert_url_contains('login')
        self.assert_element_visible(LoginPage.EMAIL_INPUT)

    def test_TC_REG_002_register_page_still_at_correct_route(self):
        """Regression: /register route still renders the register form."""
        page = RegisterPage(self.driver)
        page.open()
        self.assert_url_contains('register')
        self.assert_element_visible(RegisterPage.NAME_INPUT)

    def test_TC_REG_003_forgot_password_still_at_correct_route(self):
        """Regression: /forgot-password still renders the form."""
        page = ForgotPasswordPage(self.driver)
        page.open()
        self.assert_url_contains('forgot-password')
        self.assert_element_visible(ForgotPasswordPage.EMAIL_INPUT)

    def test_TC_REG_004_landing_page_still_renders(self):
        """Regression: Root URL still renders landing page."""
        page = LandingPage(self.driver)
        page.open()
        time.sleep(2)
        source = self.driver.page_source
        self.assertGreater(len(source), 1000)

    def test_TC_REG_005_password_field_still_masked_by_default(self):
        """Regression: Password field type='password' not accidentally changed."""
        page = LoginPage(self.driver)
        page.open()
        self.assertEqual(page.get_password_input_type(), 'password')

    def test_TC_REG_006_password_toggle_still_works(self):
        """Regression: Eye icon still toggles password visibility."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_password('SomePass@123')
        page.toggle_password_visibility()
        time.sleep(0.3)
        self.assertEqual(page.get_password_input_type(), 'text')

    def test_TC_REG_007_forgot_password_back_link_still_works(self):
        """Regression: Back to login link still navigates to /login."""
        page = ForgotPasswordPage(self.driver)
        page.open()
        page.click_back_to_login()
        time.sleep(2)
        self.assert_url_contains('login')

    def test_TC_REG_008_register_login_link_still_works(self):
        """Regression: 'Already have an account?' link still works."""
        page = RegisterPage(self.driver)
        page.open()
        page.click_login_link()
        time.sleep(2)
        self.assert_url_contains('login')

    def test_TC_REG_009_login_register_link_still_works(self):
        """Regression: Sign up link on login still works."""
        page = LoginPage(self.driver)
        page.open()
        page.click_register()
        time.sleep(2)
        self.assert_url_contains('register')

    def test_TC_REG_010_login_forgot_password_link_still_works(self):
        """Regression: Forgot password link on login still navigates correctly."""
        page = LoginPage(self.driver)
        page.open()
        page.click_forgot_password()
        time.sleep(2)
        self.assert_url_contains('forgot-password')

    # ─── TC_REG_011–020: Protected Route Regression ───────────────────────────

    def test_TC_REG_011_dashboard_still_protected(self):
        """Regression: /dashboard still requires authentication."""
        self.driver.get(routes.url('dashboard'))
        time.sleep(2)
        self.assertNotIn('/dashboard', self.driver.current_url.split('?')[0])

    def test_TC_REG_012_tasks_still_protected(self):
        """Regression: /tasks still requires authentication."""
        self.driver.get(routes.url('tasks'))
        time.sleep(2)
        self.assertNotIn('/tasks', self.driver.current_url.split('?')[0])

    def test_TC_REG_013_settings_still_protected(self):
        """Regression: /settings still requires authentication."""
        self.driver.get(routes.url('settings'))
        time.sleep(2)
        self.assertNotIn('/settings', self.driver.current_url.split('?')[0])

    def test_TC_REG_014_ai_page_still_protected(self):
        """Regression: /ai still requires authentication."""
        self.driver.get(routes.url('ai'))
        time.sleep(2)
        self.assertNotIn('/ai', self.driver.current_url.split('?')[0])

    def test_TC_REG_015_team_page_still_protected(self):
        """Regression: /team still requires authentication."""
        self.driver.get(routes.url('team'))
        time.sleep(2)
        self.assertNotIn('/team', self.driver.current_url.split('?')[0])

    def test_TC_REG_016_analytics_still_protected(self):
        """Regression: /analytics still requires authentication."""
        self.driver.get(routes.url('analytics'))
        time.sleep(2)
        self.assertNotIn('/analytics', self.driver.current_url.split('?')[0])

    def test_TC_REG_017_habits_still_protected(self):
        """Regression: /habits still requires authentication."""
        self.driver.get(routes.url('habits'))
        time.sleep(2)
        self.assertNotIn('/habits', self.driver.current_url.split('?')[0])

    def test_TC_REG_018_calendar_still_protected(self):
        """Regression: /calendar still requires authentication."""
        self.driver.get(routes.url('calendar'))
        time.sleep(2)
        self.assertNotIn('/calendar', self.driver.current_url.split('?')[0])

    def test_TC_REG_019_notifications_still_protected(self):
        """Regression: /notifications still requires authentication."""
        self.driver.get(routes.url('notifications'))
        time.sleep(2)
        self.assertNotIn('/notifications', self.driver.current_url.split('?')[0])

    def test_TC_REG_020_focus_page_still_protected(self):
        """Regression: /focus still requires authentication."""
        self.driver.get(routes.url('focus'))
        time.sleep(2)
        self.assertNotIn('/focus', self.driver.current_url.split('?')[0])

    # ─── TC_REG_021–030: UI & Styling Regression ──────────────────────────────

    def test_TC_REG_021_login_has_four_interactive_elements(self):
        """Regression: Login form still has email, password, submit, forgot-pass."""
        page = LoginPage(self.driver)
        page.open()
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self.assert_element_visible(LoginPage.PASSWORD_INPUT)
        self.assert_element_visible(LoginPage.SUBMIT_BTN)
        self.assert_element_visible(LoginPage.FORGOT_LINK)

    def test_TC_REG_022_register_has_five_interactive_elements(self):
        """Regression: Register still has name, email, password, confirm, submit."""
        page = RegisterPage(self.driver)
        page.open()
        self.assert_element_visible(RegisterPage.NAME_INPUT)
        self.assert_element_visible(RegisterPage.EMAIL_INPUT)
        self.assert_element_visible(RegisterPage.PASS_INPUT)
        self.assert_element_visible(RegisterPage.CONFIRM_INPUT)
        self.assert_element_visible(RegisterPage.SUBMIT_BTN)

    def test_TC_REG_023_flowtime_brand_still_on_login(self):
        """Regression: FlowTime brand name still on login page."""
        page = LoginPage(self.driver)
        page.open()
        brand = self.driver.find_elements(By.XPATH,
            '//*[contains(text(),"FlowTime") or contains(text(),"flowtime")]')
        self.assertGreater(len(brand), 0, "Brand name FlowTime must appear on login")

    def test_TC_REG_024_tailwind_classes_still_applied(self):
        """Regression: Tailwind CSS still applied (flex/grid classes work)."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        source = self.driver.page_source
        self.assertTrue(
            any(c in source for c in ['flex', 'grid', 'rounded', 'text-sm']),
            "Tailwind classes must be present"
        )

    def test_TC_REG_025_dark_mode_class_not_breaking_layout(self):
        """Regression: Adding dark class to html does not break layout."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        self.driver.execute_script(
            "document.documentElement.classList.add('dark');")
        time.sleep(0.5)
        self.assert_element_visible(LoginPage.EMAIL_INPUT)

    def test_TC_REG_026_login_submit_button_still_full_width(self):
        """Regression: Login submit button still has w-full class."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        source = self.driver.page_source
        self.assertIn('w-full', source)

    def test_TC_REG_027_register_strength_bar_still_present(self):
        """Regression: Password strength bar still renders on register."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_password('WeakTest')
        time.sleep(0.5)
        has_bar = page.is_strength_bar_visible()
        self.assertTrue(has_bar, "Strength bar should still render")

    def test_TC_REG_028_register_mismatch_still_shows_error(self):
        """Regression: Password mismatch error still shown."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_password(STRONG_PASSWORD)
        page.enter_confirm_password('TotallyDifferent@99')
        time.sleep(0.5)
        self.assertTrue(page.is_password_mismatch_shown())

    def test_TC_REG_029_login_email_type_still_email(self):
        """Regression: Email input type='email' not changed."""
        page = LoginPage(self.driver)
        page.open()
        self.assertEqual(page.get_email_input_type(), 'email')

    def test_TC_REG_030_framer_motion_not_blocking_elements(self):
        """Regression: Framer Motion animations don't block form interactions."""
        page = LoginPage(self.driver)
        page.open()
        time.sleep(1)  # Wait for entry animations
        self.assert_element_visible(LoginPage.EMAIL_INPUT)
        self.assert_element_visible(LoginPage.SUBMIT_BTN)

    # ─── TC_REG_031–040: SPA Behaviour Regression ─────────────────────────────

    def test_TC_REG_031_react_root_present_on_all_public_routes(self):
        """Regression: React root rendered on all public routes."""
        for r in ['', 'login', 'register', 'forgot-password']:
            self.driver.get(routes.url(r))
            time.sleep(1.5)
            kids = self.driver.execute_script(
                "const root = document.getElementById('root');"
                "return root ? root.children.length : 0;")
            self.assertGreater(kids, 0,
                f"React root empty on route /{r}")

    def test_TC_REG_032_404_route_still_handled(self):
        """Regression: Unknown route still handled by React Router."""
        self.driver.get(routes.url('page-does-not-exist-at-all'))
        time.sleep(2)
        source = self.driver.page_source
        self.assertNotIn('ENOENT', source)

    def test_TC_REG_033_browser_back_still_works(self):
        """Regression: Browser back navigation still functions."""
        self.driver.get(routes.url('login'))
        time.sleep(1)
        self.driver.get(routes.url('register'))
        time.sleep(1)
        self.driver.back()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_REG_034_page_refresh_still_works(self):
        """Regression: Page refresh on /login still renders the login page."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        self.driver.refresh()
        time.sleep(2)
        self.assert_element_visible(LoginPage.EMAIL_INPUT)

    def test_TC_REG_035_react_query_client_still_works(self):
        """Regression: React Query client doesn't error on page load."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        errors = self.driver.get_log('browser')
        query_errors = [e for e in errors
                        if 'QueryClient' in str(e)
                        and 'SEVERE' in str(e.get('level', ''))]
        self.assertEqual(len(query_errors), 0)

    def test_TC_REG_036_zustand_store_still_initializes(self):
        """Regression: Zustand auth store initializes without error."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        errors = self.driver.get_log('browser')
        zustand_errors = [e for e in errors
                          if 'zustand' in str(e).lower()
                          and 'SEVERE' in str(e.get('level', ''))]
        self.assertEqual(len(zustand_errors), 0)

    def test_TC_REG_037_auth_initializer_runs_without_crash(self):
        """Regression: AuthInitializer component still runs without crash."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        root_kids = self.driver.execute_script(
            "const r = document.getElementById('root');"
            "return r ? r.children.length : 0;")
        self.assertGreater(root_kids, 0,
            "AuthInitializer should have completed and page should render")

    def test_TC_REG_038_localstorage_still_accessible(self):
        """Regression: localStorage is still accessible in the browser."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        self.driver.execute_script("localStorage.setItem('reg_test', '1');")
        val = self.driver.execute_script("return localStorage.getItem('reg_test');")
        self.assertEqual(val, '1')
        self.driver.execute_script("localStorage.removeItem('reg_test');")

    def test_TC_REG_039_spa_no_crashes_under_rapid_navigation(self):
        """Regression: Rapid navigation between pages doesn't crash the SPA."""
        routes_to_visit = ['login', 'register', 'forgot-password', 'login', '']
        for r in routes_to_visit:
            self.driver.get(routes.url(r))
            time.sleep(0.8)
        source = self.driver.page_source
        self.assertGreater(len(source), 100)

    def test_TC_REG_040_deployment_url_returns_200_equivalent(self):
        """Regression: Deployed GitHub Pages URL is still accessible."""
        self.driver.get(test_config.base_url)
        time.sleep(3)
        source = self.driver.page_source
        self.assertGreater(len(source), 200,
            "Deployment URL should return content")

    # ─── TC_REG_041–050: Security & Configuration Regression ──────────────────

    def test_TC_REG_041_https_still_enforced(self):
        """Regression: GitHub Pages still serves over HTTPS."""
        if 'github.io' in test_config.base_url:
            self.assertTrue(
                test_config.base_url.startswith('https://'),
                "GitHub Pages should use HTTPS"
            )

    def test_TC_REG_042_no_sensitive_keys_in_page_source(self):
        """Regression: No API keys or secrets in page source."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        source = self.driver.page_source
        self.assertNotIn('JWT_SECRET', source)
        self.assertNotIn('MONGODB_URI', source)
        self.assertNotIn('STRIPE_SECRET', source)

    def test_TC_REG_043_xss_protection_still_active(self):
        """Regression: XSS payloads in form fields still don't execute."""
        page = LoginPage(self.driver)
        page.open()
        page.enter_email('<script>window.xss_reg=true;</script>')
        time.sleep(0.5)
        executed = self.driver.execute_script(
            "return window.xss_reg === true;")
        self.assertFalse(executed)

    def test_TC_REG_044_invalid_token_still_redirects(self):
        """Regression: Injecting invalid JWT still results in redirect."""
        self.driver.get(routes.url('login'))
        time.sleep(1)
        self.driver.execute_script(
            "localStorage.setItem('accessToken', 'bad.token.here');")
        self.driver.get(routes.url('tasks'))
        time.sleep(3)
        url = self.driver.current_url
        self.assertNotIn('/tasks', url.split('?')[0])

    def test_TC_REG_045_empty_localstorage_still_shows_login(self):
        """Regression: Empty localStorage still results in login redirect."""
        self.driver.get(routes.url('login'))
        time.sleep(1)
        self.driver.execute_script("localStorage.clear();")
        self.driver.get(routes.url('dashboard'))
        time.sleep(2)
        url = self.driver.current_url
        self.assertNotIn('/dashboard', url.split('?')[0])

    def test_TC_REG_046_login_form_still_requires_email(self):
        """Regression: Email field still has required attribute."""
        page = LoginPage(self.driver)
        page.open()
        req = page.get_attribute(LoginPage.EMAIL_INPUT, 'required')
        self.assertIsNotNone(req)

    def test_TC_REG_047_register_submit_still_disabled_weak_password(self):
        """Regression: Weak password still disables submit on register."""
        page = RegisterPage(self.driver)
        page.open()
        page.enter_name('Test')
        page.enter_email(random_email())
        page.enter_password('weak')
        page.enter_confirm_password('weak')
        time.sleep(0.5)
        self.assertTrue(page.is_submit_disabled())

    def test_TC_REG_048_router_base_path_still_correct(self):
        """Regression: React Router base path still handles GitHub Pages prefix."""
        self.driver.get(test_config.base_url)
        time.sleep(3)
        source = self.driver.page_source
        self.assertGreater(len(source), 500,
            "Base URL must render the app")

    def test_TC_REG_049_vite_build_assets_still_load(self):
        """Regression: Vite production assets still load without errors."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        errors = self.driver.get_log('browser')
        asset_errors = [e for e in errors
                        if 'assets/' in str(e)
                        and ('404' in str(e) or '403' in str(e))
                        and 'SEVERE' in str(e.get('level', ''))]
        self.assertEqual(len(asset_errors), 0)

    def test_TC_REG_050_app_renders_correctly_after_full_pipeline(self):
        """Regression: Full build-deploy-render cycle produces a working SPA."""
        self.driver.get(test_config.base_url)
        time.sleep(3)
        root_kids = self.driver.execute_script(
            "const r = document.getElementById('root');"
            "return r ? r.children.length : 0;")
        self.assertGreater(root_kids, 0,
            "Full CI/CD pipeline should produce a working React SPA")


if __name__ == '__main__':
    unittest.main()
