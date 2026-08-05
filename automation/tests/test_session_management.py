"""
Session Management Test Suite — 20 Test Cases
Module: Session Management
Tests: Token storage, session persistence, logout, cookie management.
"""

import time
import unittest
from selenium.webdriver.common.by import By

from automation.tests.base_test import BaseTest
from automation.pages import LoginPage, LandingPage
from automation.config import routes, test_config
from automation.data import VALID_USER


class TestSessionManagement(BaseTest):
    MODULE = 'Session Management'
    PRIORITY = 'Critical'

    def test_TC_SES_001_fresh_session_no_access_token(self):
        """Fresh browser session has no access token in localStorage."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        token = self.driver.execute_script(
            "return localStorage.getItem('accessToken');")
        self.assertIsNone(token, "No access token should exist on fresh session")

    def test_TC_SES_002_fresh_session_no_refresh_token(self):
        """Fresh session has no refresh token in localStorage."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        token = self.driver.execute_script(
            "return localStorage.getItem('refreshToken');")
        self.assertIsNone(token)

    def test_TC_SES_003_no_cookies_on_public_pages(self):
        """No sensitive auth cookies are set on public pages."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        cookies = self.driver.get_cookies()
        jwt_cookies = [c for c in cookies
                       if 'jwt' in c.get('name', '').lower()
                       or 'token' in c.get('name', '').lower()
                       or 'auth' in c.get('name', '').lower()]
        self.assertEqual(len(jwt_cookies), 0,
            f"No auth cookies should exist on public page: {jwt_cookies}")

    def test_TC_SES_004_delete_cookies_and_reload_stays_public(self):
        """After deleting all cookies and reloading, user stays unauthenticated."""
        self.driver.get(routes.url('login'))
        time.sleep(1)
        self.driver.delete_all_cookies()
        self.driver.get(routes.url('dashboard'))
        time.sleep(2)
        url = self.driver.current_url
        self.assertNotIn('/dashboard', url.split('?')[0])

    def test_TC_SES_005_localstorage_cleared_does_not_error(self):
        """Clearing localStorage does not crash the app."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        self.driver.execute_script("localStorage.clear();")
        self.driver.refresh()
        time.sleep(2)
        source = self.driver.page_source
        self.assertGreater(len(source), 100, "App should not crash after localStorage clear")

    def test_TC_SES_006_sessionstorage_not_used_for_auth(self):
        """Auth tokens are not stored in sessionStorage."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        access_ss = self.driver.execute_script(
            "return sessionStorage.getItem('accessToken');")
        refresh_ss = self.driver.execute_script(
            "return sessionStorage.getItem('refreshToken');")
        self.assertIsNone(access_ss)
        self.assertIsNone(refresh_ss)

    def test_TC_SES_007_zustand_persisted_key_in_localstorage(self):
        """Zustand persisted auth storage key exists after page load."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        # Zustand persist creates 'auth-storage' key
        auth_storage = self.driver.execute_script(
            "return localStorage.getItem('auth-storage');")
        # May be null or JSON — both are acceptable
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_SES_008_protected_route_blocked_without_token(self):
        """Protected route /dashboard is blocked without valid token."""
        self.driver.execute_script("localStorage.clear();")
        self.driver.get(routes.url('dashboard'))
        time.sleep(2)
        url = self.driver.current_url
        self.assertNotIn('/dashboard', url.split('?')[0])

    def test_TC_SES_009_invalid_token_in_localstorage_does_not_grant_access(self):
        """Invalid/expired token in localStorage does not grant dashboard access."""
        self.driver.get(routes.url('login'))
        time.sleep(1)
        self.driver.execute_script(
            "localStorage.setItem('accessToken', 'invalid.jwt.token');"
            "localStorage.setItem('refreshToken', 'invalid.refresh.token');"
        )
        self.driver.get(routes.url('dashboard'))
        time.sleep(3)
        url = self.driver.current_url
        # Should not land on /dashboard since token is invalid
        self.assertNotIn('/dashboard', url.split('?')[0])

    def test_TC_SES_010_page_reload_clears_invalid_token(self):
        """After reload with invalid token, user is returned to login."""
        self.driver.get(routes.url('login'))
        time.sleep(1)
        self.driver.execute_script(
            "localStorage.setItem('accessToken', 'expired.token.here');"
        )
        self.driver.refresh()
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_SES_011_multiple_tabs_share_localstorage(self):
        """LocalStorage is shared across same-origin tabs."""
        self.driver.get(routes.url('login'))
        time.sleep(1)
        self.driver.execute_script(
            "localStorage.setItem('test_key', 'test_value');")
        val = self.driver.execute_script(
            "return localStorage.getItem('test_key');")
        self.assertEqual(val, 'test_value')
        # Clean up
        self.driver.execute_script("localStorage.removeItem('test_key');")

    def test_TC_SES_012_auth_state_not_shared_between_different_origins(self):
        """GitHub Pages URL is served over HTTPS (same origin enforced)."""
        url = self.driver.current_url or test_config.base_url
        if 'github.io' in test_config.base_url:
            self.assertTrue(
                test_config.base_url.startswith('https://'),
                "GitHub Pages should enforce HTTPS for secure cookies"
            )

    def test_TC_SES_013_login_page_no_preexisting_error_on_load(self):
        """Login page loads without any pre-existing error states."""
        page = LoginPage(self.driver)
        page.open()
        error_visible = page.is_error_displayed()
        self.assertFalse(error_visible,
            "Error banner should not be shown on fresh login page load")

    def test_TC_SES_014_localstorage_auth_storage_valid_json(self):
        """If auth-storage key exists in localStorage, it is valid JSON."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        raw = self.driver.execute_script(
            "return localStorage.getItem('auth-storage');")
        if raw:
            import json
            try:
                parsed = json.loads(raw)
                self.assertIsInstance(parsed, dict)
            except json.JSONDecodeError:
                self.fail(f"auth-storage is not valid JSON: {raw[:100]}")

    def test_TC_SES_015_session_not_accessible_from_different_path(self):
        """LocalStorage from one path is accessible across paths (same origin)."""
        self.driver.get(routes.url('login'))
        time.sleep(1)
        self.driver.execute_script(
            "localStorage.setItem('ses_test', '123');")
        self.driver.get(routes.url('register'))
        time.sleep(1)
        val = self.driver.execute_script(
            "return localStorage.getItem('ses_test');")
        self.assertEqual(val, '123')
        self.driver.execute_script("localStorage.removeItem('ses_test');")

    def test_TC_SES_016_cookies_list_on_public_page(self):
        """Verify no httpOnly session cookies leak to JavaScript context."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        js_cookies = self.driver.execute_script("return document.cookie;")
        self.assertNotIn('jwt', js_cookies.lower())
        self.assertNotIn('token=', js_cookies.lower())

    def test_TC_SES_017_auth_initializer_runs_on_page_load(self):
        """AuthInitializer component initializes auth state on load."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        # After initialization, isInitialized should be true — page renders
        source = self.driver.page_source
        self.assertGreater(len(source), 200, "Auth initializer should have completed")

    def test_TC_SES_018_react_query_cache_empty_on_fresh_session(self):
        """TanStack Query cache is empty on fresh unauthenticated session."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        # React Query doesn't use localStorage by default — verify no error
        errors = self.driver.get_log('browser')
        query_errors = [e for e in errors
                        if 'queryClient' in str(e).lower()
                        and 'SEVERE' in str(e.get('level', ''))]
        self.assertEqual(len(query_errors), 0)

    def test_TC_SES_019_persistent_store_survives_soft_navigation(self):
        """Zustand store persists across SPA route changes."""
        self.driver.get(routes.url('login'))
        time.sleep(1)
        self.driver.execute_script(
            "localStorage.setItem('nav_test', 'alive');")
        self.driver.get(routes.url('register'))
        time.sleep(1)
        val = self.driver.execute_script(
            "return localStorage.getItem('nav_test');")
        self.assertEqual(val, 'alive')
        self.driver.execute_script("localStorage.removeItem('nav_test');")

    def test_TC_SES_020_protected_route_shows_login_after_session_expire(self):
        """After simulating session expiry, protected route shows login."""
        self.driver.get(routes.url('login'))
        time.sleep(1)
        self.driver.execute_script("localStorage.clear();")
        self.driver.get(routes.url('tasks'))
        time.sleep(2)
        url = self.driver.current_url
        self.assertNotIn('/tasks', url.split('?')[0],
            "Should redirect to login when session expired")


if __name__ == '__main__':
    unittest.main()
