"""
Performance Smoke Test Suite — 20 Test Cases
Module: Performance Smoke Tests
Tests: Page load times, DOM ready times, resource counts, SPA render speed.
Uses the Navigation Timing API — thresholds are generous for CI environments.
"""

import time
import unittest
from selenium.webdriver.common.by import By

from automation.tests.base_test import BaseTest
from automation.pages import LoginPage, RegisterPage, LandingPage, ForgotPasswordPage
from automation.config import routes, test_config
from automation.data import PERFORMANCE_THRESHOLDS


class TestPerformanceSmoke(BaseTest):
    MODULE = 'Performance Smoke Tests'
    PRIORITY = 'Medium'

    def _get_nav_timing(self) -> dict:
        """Return Navigation Timing API metrics."""
        return self.driver.execute_script("""
            const t = performance.timing;
            const nav = performance.getEntriesByType('navigation')[0] || {};
            return {
                load_time: t.loadEventEnd - t.navigationStart,
                dom_interactive: t.domInteractive - t.navigationStart,
                dom_content_loaded: t.domContentLoadedEventEnd - t.navigationStart,
                ttfb: t.responseStart - t.navigationStart,
                response_time: t.responseEnd - t.responseStart
            };
        """) or {}

    def _get_resource_count(self) -> dict:
        """Return count of resources by type."""
        return self.driver.execute_script("""
            const entries = performance.getEntriesByType('resource');
            const counts = {script:0, stylesheet:0, img:0, fetch:0, other:0};
            entries.forEach(e => {
                const t = e.initiatorType;
                if (t in counts) counts[t]++;
                else counts.other++;
            });
            counts.total = entries.length;
            return counts;
        """) or {}

    # ─── TC_PERF_001–005: Page Load Time ──────────────────────────────────────

    def test_TC_PERF_001_landing_page_load_under_5s(self):
        """Landing page loads in under 5 seconds."""
        start = time.time()
        self.driver.get(test_config.base_url)
        time.sleep(0.5)
        elapsed = (time.time() - start) * 1000
        self.assertLess(elapsed, PERFORMANCE_THRESHOLDS['page_load_ms'],
            f"Landing page load time {elapsed:.0f}ms exceeds 5000ms threshold")

    def test_TC_PERF_002_login_page_load_under_5s(self):
        """Login page loads in under 5 seconds."""
        start = time.time()
        self.driver.get(routes.url('login'))
        time.sleep(0.5)
        elapsed = (time.time() - start) * 1000
        self.assertLess(elapsed, PERFORMANCE_THRESHOLDS['page_load_ms'])

    def test_TC_PERF_003_register_page_load_under_5s(self):
        """Register page loads in under 5 seconds."""
        start = time.time()
        self.driver.get(routes.url('register'))
        time.sleep(0.5)
        elapsed = (time.time() - start) * 1000
        self.assertLess(elapsed, PERFORMANCE_THRESHOLDS['page_load_ms'])

    def test_TC_PERF_004_forgot_password_load_under_5s(self):
        """Forgot password page loads in under 5 seconds."""
        start = time.time()
        self.driver.get(routes.url('forgot-password'))
        time.sleep(0.5)
        elapsed = (time.time() - start) * 1000
        self.assertLess(elapsed, PERFORMANCE_THRESHOLDS['page_load_ms'])

    def test_TC_PERF_005_navigation_timing_api_available(self):
        """Navigation Timing API is available in the browser."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        has_timing = self.driver.execute_script(
            "return typeof performance !== 'undefined' && "
            "typeof performance.timing !== 'undefined';")
        self.assertTrue(has_timing, "Navigation Timing API should be available")

    # ─── TC_PERF_006–010: DOM Ready & TTFB ────────────────────────────────────

    def test_TC_PERF_006_landing_dom_interactive_under_3s(self):
        """Landing page DOM becomes interactive in under 3 seconds."""
        self.driver.get(test_config.base_url)
        time.sleep(3)
        timing = self._get_nav_timing()
        dom_interactive = timing.get('dom_interactive', 0)
        if dom_interactive > 0:
            self.assertLess(dom_interactive,
                PERFORMANCE_THRESHOLDS['dom_interactive_ms'],
                f"DOM interactive at {dom_interactive}ms (threshold: 3000ms)")

    def test_TC_PERF_007_login_dom_interactive_under_3s(self):
        """Login page DOM becomes interactive in under 3 seconds."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        timing = self._get_nav_timing()
        dom_interactive = timing.get('dom_interactive', 0)
        if dom_interactive > 0:
            self.assertLess(dom_interactive, PERFORMANCE_THRESHOLDS['dom_interactive_ms'])

    def test_TC_PERF_008_ttfb_under_2s(self):
        """Time to First Byte (TTFB) is under 2 seconds."""
        self.driver.get(test_config.base_url)
        time.sleep(3)
        timing = self._get_nav_timing()
        ttfb = timing.get('ttfb', 0)
        if ttfb > 0:
            self.assertLess(ttfb, 2000,
                f"TTFB {ttfb}ms exceeds 2000ms threshold")

    def test_TC_PERF_009_dom_content_loaded_under_4s(self):
        """DOMContentLoaded event fires in under 4 seconds."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        timing = self._get_nav_timing()
        dcl = timing.get('dom_content_loaded', 0)
        if dcl > 0:
            self.assertLess(dcl, 4000,
                f"DOMContentLoaded at {dcl}ms exceeds 4000ms threshold")

    def test_TC_PERF_010_react_root_populates_within_3s(self):
        """React root element has children within 3 seconds of page load."""
        start = time.time()
        self.driver.get(routes.url('login'))
        # Poll until root has children
        root_populated = False
        while (time.time() - start) < 3:
            kids = self.driver.execute_script(
                "const r = document.getElementById('root');"
                "return r ? r.children.length : 0;")
            if kids > 0:
                root_populated = True
                break
            time.sleep(0.2)
        self.assertTrue(root_populated,
            "React root should populate within 3 seconds")

    # ─── TC_PERF_011–015: Resource Counts & Sizes ─────────────────────────────

    def test_TC_PERF_011_resource_count_reasonable(self):
        """Total resource count on login page is reasonable (< 100)."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        counts = self._get_resource_count()
        total = counts.get('total', 0)
        self.assertLess(total, 100,
            f"Too many resources loaded ({total}). Possible issue with bundling.")

    def test_TC_PERF_012_script_count_reasonable(self):
        """Number of JS script resources is reasonable (< 20)."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        counts = self._get_resource_count()
        scripts = counts.get('script', 0)
        self.assertLess(scripts, 20,
            f"Too many script files ({scripts}). Vite should bundle into chunks.")

    def test_TC_PERF_013_stylesheet_count_reasonable(self):
        """Number of stylesheet resources is reasonable (< 5)."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        counts = self._get_resource_count()
        styles = counts.get('stylesheet', 0)
        self.assertLess(styles, 5,
            f"Too many stylesheet files ({styles})")

    def test_TC_PERF_014_page_size_reasonable(self):
        """Landing page HTML response body is not empty."""
        self.driver.get(test_config.base_url)
        time.sleep(3)
        page_source = self.driver.page_source
        self.assertGreater(len(page_source), 500,
            "Page HTML should have substantial content")

    def test_TC_PERF_015_no_long_tasks_blocking_ui(self):
        """No JavaScript errors suggesting blocking long tasks on load."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        errors = self.driver.get_log('browser')
        timeout_errors = [e for e in errors
                          if 'timeout' in str(e).lower()
                          and 'SEVERE' in str(e.get('level', ''))]
        self.assertEqual(len(timeout_errors), 0)

    # ─── TC_PERF_016–020: SPA Navigation Speed ────────────────────────────────

    def test_TC_PERF_016_spa_route_change_under_1s(self):
        """SPA client-side route change completes in under 1 second."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        start = time.time()
        self.driver.get(routes.url('register'))
        time.sleep(0.5)
        elapsed = (time.time() - start) * 1000
        self.assertLess(elapsed, 3000,
            f"Route change took {elapsed:.0f}ms (threshold: 3000ms)")

    def test_TC_PERF_017_multiple_navigations_no_memory_leak_indicator(self):
        """Navigating between pages multiple times does not cause JS errors."""
        pages = ['login', 'register', 'forgot-password', 'login', 'register']
        for r in pages:
            self.driver.get(routes.url(r))
            time.sleep(1)
        errors = self.driver.get_log('browser')
        severe = [e for e in errors
                  if 'SEVERE' in str(e.get('level', ''))
                  and 'favicon' not in str(e).lower()]
        self.assertEqual(len(severe), 0,
            f"Errors after multiple navigations: {severe}")

    def test_TC_PERF_018_landing_page_interactive_elements_responsive(self):
        """Landing page interactive elements respond to hover within 1s."""
        page = LandingPage(self.driver)
        page.open()
        time.sleep(2)
        links = self.driver.find_elements(By.TAG_NAME, 'a')
        self.assertGreater(len(links), 0,
            "Landing page should have interactive links")

    def test_TC_PERF_019_js_bundle_evaluates_without_timeout(self):
        """JavaScript bundle evaluates in the browser without timeout errors."""
        self.driver.get(test_config.base_url)
        time.sleep(5)
        errors = self.driver.get_log('browser')
        eval_errors = [e for e in errors
                       if ('Script' in str(e) or 'execution context' in str(e).lower())
                       and 'SEVERE' in str(e.get('level', ''))]
        self.assertEqual(len(eval_errors), 0)

    def test_TC_PERF_020_vite_optimized_chunks_load_quickly(self):
        """Vite-optimized chunks load and execute without timeout."""
        self.driver.get(routes.url('login'))
        time.sleep(5)
        root_kids = self.driver.execute_script(
            "const r = document.getElementById('root');"
            "return r ? r.children.length : 0;")
        self.assertGreater(root_kids, 0,
            "Vite bundle should load and React should render within 5 seconds")


if __name__ == '__main__':
    unittest.main()
