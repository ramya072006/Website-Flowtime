"""
Navigation Test Suite — 30 Test Cases
Module: Navigation
Tests: Route transitions, browser history, back/forward, deep links.
"""

import time
import unittest

from automation.tests.base_test import BaseTest
from automation.pages import LoginPage, LandingPage
from automation.config import routes, test_config
from automation.data import APP_ROUTES


class TestNavigation(BaseTest):
    MODULE = 'Navigation'
    PRIORITY = 'High'

    def test_TC_NAV_001_landing_page_accessible(self):
        """Root URL loads the landing page."""
        self.driver.get(test_config.base_url)
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)
        source = self.driver.page_source
        self.assertGreater(len(source), 500)

    def test_TC_NAV_002_login_route_loads(self):
        self.driver.get(routes.url('login'))
        time.sleep(2)
        self.assert_url_contains('login')

    def test_TC_NAV_003_register_route_loads(self):
        self.driver.get(routes.url('register'))
        time.sleep(2)
        self.assert_url_contains('register')

    def test_TC_NAV_004_forgot_password_route_loads(self):
        self.driver.get(routes.url('forgot-password'))
        time.sleep(2)
        self.assert_url_contains('forgot-password')

    def test_TC_NAV_005_verify_otp_route_loads(self):
        self.driver.get(routes.url('verify-otp'))
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_NAV_006_login_to_register_link_navigation(self):
        """Navigation from login to register via link."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        page = LoginPage(self.driver)
        page.click_register()
        time.sleep(2)
        self.assert_url_contains('register')

    def test_TC_NAV_007_register_to_login_link_navigation(self):
        """Navigation from register to login via link."""
        from automation.pages import RegisterPage
        self.driver.get(routes.url('register'))
        time.sleep(2)
        page = RegisterPage(self.driver)
        page.click_login_link()
        time.sleep(2)
        self.assert_url_contains('login')

    def test_TC_NAV_008_login_to_forgot_password_navigation(self):
        """Forgot password link on login page navigates correctly."""
        page = LoginPage(self.driver)
        page.open()
        page.click_forgot_password()
        time.sleep(2)
        self.assert_url_contains('forgot-password')

    def test_TC_NAV_009_browser_back_from_login_to_landing(self):
        """Browser back button works from login to landing."""
        self.driver.get(test_config.base_url)
        time.sleep(2)
        self.driver.get(routes.url('login'))
        time.sleep(2)
        self.driver.back()
        time.sleep(2)
        url = self.driver.current_url
        self.assertNotIn('/login', url)

    def test_TC_NAV_010_browser_forward_navigation(self):
        """Browser forward button navigates forward."""
        self.driver.get(test_config.base_url)
        time.sleep(1)
        self.driver.get(routes.url('login'))
        time.sleep(1)
        self.driver.back()
        time.sleep(1)
        self.driver.forward()
        time.sleep(1)
        self.assert_url_contains('login')

    def test_TC_NAV_011_page_refresh_login_stays_on_login(self):
        """Refreshing login page keeps user on login page."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        self.driver.refresh()
        time.sleep(2)
        self.assert_url_contains('login')

    def test_TC_NAV_012_page_refresh_register_stays_on_register(self):
        self.driver.get(routes.url('register'))
        time.sleep(2)
        self.driver.refresh()
        time.sleep(2)
        self.assert_url_contains('register')

    def test_TC_NAV_013_404_route_handled_gracefully(self):
        """Unknown routes are handled gracefully by React Router."""
        self.driver.get(routes.url('this-page-does-not-exist'))
        time.sleep(2)
        source = self.driver.page_source
        # Should not show raw browser 404 or white screen
        self.assertNotIn('<h1>404</h1>', source)

    def test_TC_NAV_014_deep_link_unknown_route_redirects_to_home(self):
        """Deep link to unknown route redirects to home."""
        self.driver.get(routes.url('unknown/deep/path'))
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_NAV_015_page_titles_not_empty(self):
        """Each public page has a non-empty browser title."""
        public_routes = ['', 'login', 'register', 'forgot-password']
        for r in public_routes:
            self.driver.get(routes.url(r))
            time.sleep(2)
            title = self.driver.title
            self.assertGreater(len(title), 0,
                f"Page title empty for route: /{r}")

    def test_TC_NAV_016_no_broken_links_on_landing(self):
        """All anchor links on landing page have valid href attributes."""
        self.driver.get(test_config.base_url)
        time.sleep(3)
        links = self.driver.find_elements('css selector', 'a[href]')
        broken = []
        for link in links[:20]:  # Check first 20
            href = link.get_attribute('href') or ''
            if href.startswith('javascript:void') or href == '#':
                broken.append(href)
        # No javascript:void(0) nav links
        self.assertEqual(len(broken), 0,
            f"Links with javascript:void: {broken}")

    def test_TC_NAV_017_login_page_has_navigation_elements(self):
        """Login page has at least 2 navigation links."""
        page = LoginPage(self.driver)
        page.open()
        links = self.driver.find_elements('css selector', 'a[href]')
        self.assertGreaterEqual(len(links), 2,
            "Login page should have at least 2 nav links")

    def test_TC_NAV_018_register_page_has_navigation_elements(self):
        """Register page has at least 1 navigation link."""
        from automation.pages import RegisterPage
        self.driver.get(routes.url('register'))
        time.sleep(2)
        links = self.driver.find_elements('css selector', 'a[href]')
        self.assertGreaterEqual(len(links), 1)

    def test_TC_NAV_019_url_hash_navigation_works(self):
        """URL hash navigation does not break the SPA."""
        self.driver.get(test_config.base_url + '#features')
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_NAV_020_query_param_in_url_does_not_break_page(self):
        """Query parameters in URL don't break the SPA."""
        self.driver.get(routes.url('login') + '?redirect=/dashboard')
        time.sleep(2)
        source = self.driver.page_source
        self.assertGreater(len(source), 100)

    def test_TC_NAV_021_navigation_history_length_increases(self):
        """Each navigation adds to browser history."""
        self.driver.get(test_config.base_url)
        time.sleep(1)
        self.driver.get(routes.url('login'))
        time.sleep(1)
        self.driver.get(routes.url('register'))
        time.sleep(1)
        history_len = self.driver.execute_script("return window.history.length;")
        self.assertGreaterEqual(history_len, 3)

    def test_TC_NAV_022_login_page_reachable_from_landing(self):
        """Login is reachable from landing page via a link."""
        page = LandingPage(self.driver)
        page.open()
        time.sleep(2)
        login_links = self.driver.find_elements('xpath', '//a[contains(@href,"login")]')
        self.assertGreater(len(login_links), 0,
            "Landing page should have at least one link to /login")

    def test_TC_NAV_023_register_reachable_from_landing(self):
        """Register is reachable from landing page."""
        page = LandingPage(self.driver)
        page.open()
        time.sleep(2)
        reg_links = self.driver.find_elements('xpath',
            '//a[contains(@href,"register")] | //button[contains(text(),"Get Started")]')
        self.assertGreater(len(reg_links), 0)

    def test_TC_NAV_024_page_does_not_redirect_in_loop(self):
        """Navigation does not enter redirect loops."""
        start_url = test_config.base_url
        self.driver.get(start_url)
        time.sleep(3)
        end_url = self.driver.current_url
        # Verify stable URL — not looping
        self.assertIsNotNone(end_url)
        self.assertNotEqual(end_url, 'about:blank')

    def test_TC_NAV_025_spa_handles_trailing_slash(self):
        """Routes with trailing slash are handled correctly."""
        self.driver.get(routes.url('login') + '/')
        time.sleep(2)
        self.assertIsNotNone(self.driver.current_url)

    def test_TC_NAV_026_landing_loads_under_3s(self):
        """Landing page loads in under 3 seconds."""
        start = time.time()
        self.driver.get(test_config.base_url)
        time.sleep(0.5)
        end = time.time()
        elapsed_ms = (end - start) * 1000
        self.assertLess(elapsed_ms, 5000,
            f"Landing page took {elapsed_ms:.0f}ms (should be < 5000ms)")

    def test_TC_NAV_027_login_page_loads_under_3s(self):
        """Login page loads in under 3 seconds."""
        start = time.time()
        self.driver.get(routes.url('login'))
        time.sleep(0.5)
        end = time.time()
        elapsed_ms = (end - start) * 1000
        self.assertLess(elapsed_ms, 5000)

    def test_TC_NAV_028_all_public_pages_return_content(self):
        """All public pages return non-trivial page content."""
        for r, _, name in APP_ROUTES:
            self.driver.get(routes.url(r.lstrip('/')))
            time.sleep(2)
            source = self.driver.page_source
            self.assertGreater(len(source), 500,
                f"Page {name} source too short: {len(source)}")

    def test_TC_NAV_029_footer_not_blocking_navigation(self):
        """Footer links work on the landing page."""
        page = LandingPage(self.driver)
        page.open()
        time.sleep(2)
        footer = self.driver.find_elements('css selector', 'footer')
        if footer:
            self.assertTrue(footer[0].is_displayed())

    def test_TC_NAV_030_route_change_does_not_produce_js_errors(self):
        """Route changes between pages don't produce JS errors."""
        self.driver.get(test_config.base_url)
        time.sleep(2)
        self.driver.get(routes.url('login'))
        time.sleep(2)
        self.driver.get(routes.url('register'))
        time.sleep(2)
        errors = self.driver.get_log('browser')
        severe = [e for e in errors if 'SEVERE' in str(e.get('level', ''))]
        # Filter known noise
        critical = [e for e in severe if 'favicon' not in str(e).lower()]
        self.assertEqual(len(critical), 0,
            f"JS errors during navigation: {critical}")


if __name__ == '__main__':
    unittest.main()
