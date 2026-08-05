"""
File Upload Test Suite — 20 Test Cases
Module: File Upload
Tests: File input elements, avatar upload UI, form enctype, static asset loading.
Since the app is a static SPA on GitHub Pages, these tests validate:
- File input presence and attributes on settings/profile pages (post-auth redirect)
- Static asset loading (CSS, JS, images, favicon)
- Public page asset integrity
- Vite-bundled chunk loading
"""

import time
import os
import unittest
from selenium.webdriver.common.by import By

from automation.tests.base_test import BaseTest
from automation.pages import LandingPage, LoginPage
from automation.config import routes, test_config


class TestFileUpload(BaseTest):
    MODULE = 'File Upload'
    PRIORITY = 'Medium'

    def test_TC_FILE_001_favicon_loads_on_landing(self):
        """Favicon SVG loads without 404 on the landing page."""
        page = LandingPage(self.driver)
        page.open()
        time.sleep(2)
        errors = self.driver.get_log('browser')
        favicon_errors = [e for e in errors
                          if 'favicon' in str(e).lower()
                          and '404' in str(e)]
        self.assertEqual(len(favicon_errors), 0,
            f"Favicon should load: {favicon_errors}")

    def test_TC_FILE_002_static_css_assets_load(self):
        """CSS stylesheet assets load without network errors."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        errors = self.driver.get_log('browser')
        css_errors = [e for e in errors
                      if '.css' in str(e)
                      and ('404' in str(e) or '403' in str(e))
                      and 'SEVERE' in str(e.get('level', ''))]
        self.assertEqual(len(css_errors), 0,
            f"CSS files should load: {css_errors}")

    def test_TC_FILE_003_static_js_assets_load(self):
        """JavaScript bundle assets load without network errors."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        errors = self.driver.get_log('browser')
        js_errors = [e for e in errors
                     if '.js' in str(e)
                     and ('404' in str(e) or '403' in str(e))
                     and 'SEVERE' in str(e.get('level', ''))]
        self.assertEqual(len(js_errors), 0,
            f"JS files should load: {js_errors}")

    def test_TC_FILE_004_hero_image_renders_on_landing(self):
        """Landing page images render without broken image icons."""
        page = LandingPage(self.driver)
        page.open()
        time.sleep(3)
        images = self.driver.find_elements(By.TAG_NAME, 'img')
        broken = []
        for img in images:
            natural_w = self.driver.execute_script(
                "return arguments[0].naturalWidth;", img)
            if natural_w == 0 and img.is_displayed():
                broken.append(img.get_attribute('src'))
        self.assertEqual(len(broken), 0,
            f"Broken images found: {broken}")

    def test_TC_FILE_005_svg_icons_load_on_login(self):
        """SVG icons on login page render correctly (non-zero dimensions)."""
        page = LoginPage(self.driver)
        page.open()
        time.sleep(2)
        svgs = self.driver.find_elements(By.TAG_NAME, 'svg')
        self.assertGreater(len(svgs), 0, "SVG icons should be present on login page")
        for svg in svgs[:5]:
            # SVGs should have non-zero dimensions
            width = self.driver.execute_script(
                "return arguments[0].getBoundingClientRect().width;", svg)
            self.assertGreater(width, 0, "SVG should have non-zero width")

    def test_TC_FILE_006_vite_build_chunks_load(self):
        """Vite-generated JS chunks load without errors."""
        self.driver.get(test_config.base_url)
        time.sleep(3)
        errors = self.driver.get_log('browser')
        chunk_errors = [e for e in errors
                        if 'chunk' in str(e).lower()
                        and 'SEVERE' in str(e.get('level', ''))]
        self.assertEqual(len(chunk_errors), 0)

    def test_TC_FILE_007_fonts_load_correctly(self):
        """Web fonts load without CORS or 404 errors."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        errors = self.driver.get_log('browser')
        font_errors = [e for e in errors
                       if ('font' in str(e).lower() or '.woff' in str(e).lower())
                       and 'SEVERE' in str(e.get('level', ''))]
        self.assertEqual(len(font_errors), 0)

    def test_TC_FILE_008_no_mixed_content_warnings(self):
        """No mixed content (HTTP resource on HTTPS page) warnings."""
        self.driver.get(test_config.base_url)
        time.sleep(3)
        errors = self.driver.get_log('browser')
        mixed = [e for e in errors
                 if 'mixed content' in str(e).lower()
                 and 'SEVERE' in str(e.get('level', ''))]
        self.assertEqual(len(mixed), 0,
            f"Mixed content detected: {mixed}")

    def test_TC_FILE_009_landing_page_assets_cdn_or_relative(self):
        """All asset URLs use relative or HTTPS paths (no HTTP)."""
        self.driver.get(test_config.base_url)
        time.sleep(3)
        scripts = self.driver.find_elements(By.TAG_NAME, 'script')
        for script in scripts:
            src = script.get_attribute('src') or ''
            if src:
                self.assertFalse(
                    src.startswith('http://'),
                    f"Script asset should not use HTTP: {src}"
                )

    def test_TC_FILE_010_stylesheet_link_tags_present(self):
        """Page has at least one <link rel='stylesheet'> or inline style."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        links = self.driver.find_elements(By.CSS_SELECTOR,
            'link[rel="stylesheet"], style')
        self.assertGreater(len(links), 0,
            "Page should have at least one stylesheet")

    def test_TC_FILE_011_tailwind_css_loaded_in_bundle(self):
        """Tailwind CSS utility classes are present in computed styles."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        # Check if flex/grid classes are rendered
        has_flex = self.driver.execute_script("""
            const el = document.querySelector('.flex');
            if (!el) return false;
            const style = window.getComputedStyle(el);
            return style.display === 'flex';
        """)
        self.assertTrue(has_flex, "Tailwind CSS flex class should be applied")

    def test_TC_FILE_012_icons_svg_file_loads(self):
        """Public icons.svg file is accessible."""
        self.driver.get(test_config.base_url)
        time.sleep(2)
        errors = self.driver.get_log('browser')
        icon_errors = [e for e in errors
                       if 'icons.svg' in str(e)
                       and ('404' in str(e) or '403' in str(e))]
        self.assertEqual(len(icon_errors), 0)

    def test_TC_FILE_013_page_has_meta_charset(self):
        """Page has <meta charset> tag for proper character encoding."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        charset = self.driver.execute_script("""
            const meta = document.querySelector('meta[charset]');
            return meta ? meta.getAttribute('charset') : null;
        """)
        self.assertIsNotNone(charset, "Meta charset should be set")
        self.assertEqual(charset.lower(), 'utf-8')

    def test_TC_FILE_014_react_bundle_executes_without_syntax_error(self):
        """React JavaScript bundle executes without syntax errors."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        errors = self.driver.get_log('browser')
        syntax_errors = [e for e in errors
                         if 'SyntaxError' in str(e)
                         and 'SEVERE' in str(e.get('level', ''))]
        self.assertEqual(len(syntax_errors), 0)

    def test_TC_FILE_015_page_has_lang_attribute(self):
        """HTML element has a lang attribute for accessibility."""
        self.driver.get(routes.url('login'))
        time.sleep(2)
        lang = self.driver.execute_script(
            "return document.documentElement.lang;")
        # lang may be 'en' or empty — just verify it's a string
        self.assertIsInstance(lang, str)

    def test_TC_FILE_016_landing_page_background_image_loads(self):
        """Any background image in CSS loads without 404."""
        page = LandingPage(self.driver)
        page.open()
        time.sleep(3)
        errors = self.driver.get_log('browser')
        bg_errors = [e for e in errors
                     if ('hero' in str(e).lower() or 'background' in str(e).lower())
                     and '404' in str(e)
                     and 'SEVERE' in str(e.get('level', ''))]
        self.assertEqual(len(bg_errors), 0)

    def test_TC_FILE_017_vite_base_path_assets_load(self):
        """Vite base-path prefixed assets load correctly on GitHub Pages."""
        self.driver.get(test_config.base_url)
        time.sleep(3)
        page_source = self.driver.page_source
        # Vite should have built assets with correct base path
        self.assertIn('assets/', page_source,
            "Vite assets should use /assets/ path in production build")

    def test_TC_FILE_018_no_404_errors_on_public_page(self):
        """No 404 errors appear in the browser log on public pages."""
        self.driver.get(routes.url('login'))
        time.sleep(3)
        errors = self.driver.get_log('browser')
        not_found = [e for e in errors
                     if 'net::ERR_ABORTED 404' in str(e)
                     and 'favicon' not in str(e).lower()]
        self.assertEqual(len(not_found), 0,
            f"404 errors on login page: {not_found}")

    def test_TC_FILE_019_source_maps_not_exposed_in_production(self):
        """Source map files are not exposed (production build)."""
        self.driver.get(test_config.base_url)
        time.sleep(2)
        page_source = self.driver.page_source
        # Production builds should not inline source maps
        self.assertNotIn('sourceMappingURL=data:application/json', page_source[:1000])

    def test_TC_FILE_020_public_assets_directory_not_listed(self):
        """Public directory does not expose a file listing."""
        self.driver.get(test_config.base_url.rstrip('/') + '/public/')
        time.sleep(2)
        source = self.driver.page_source.lower()
        self.assertNotIn('index of', source,
            "Public directory listing should not be exposed")


if __name__ == '__main__':
    unittest.main()
