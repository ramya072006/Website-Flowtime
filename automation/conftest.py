"""
pytest conftest.py — FlowTime Selenium Automation Framework
Provides CLI options and shared fixtures for pytest runs.
"""

import os
import pytest


def pytest_addoption(parser):
    """Add custom CLI options to pytest."""
    parser.addoption(
        '--base-url',
        action='store',
        default='',
        help='Base URL for Selenium tests (must be live GitHub Pages URL)',
    )
    parser.addoption(
        '--headless',
        action='store_true',
        default=True,
        help='Run Chrome in headless mode',
    )
    parser.addoption(
        '--suite',
        action='store',
        default='all',
        help='Test suite name to run',
    )


def pytest_configure(config):
    """Apply CLI options to environment before test collection."""
    base_url = config.getoption('--base-url', default='', skip=True)
    if base_url:
        os.environ['BASE_URL'] = base_url.rstrip('/') + '/'

    headless = config.getoption('--headless', default=True, skip=True)
    if headless:
        os.environ['HEADLESS'] = 'true'


def pytest_collection_modifyitems(config, items):
    """Add markers and deselect based on suite option."""
    # Add default markers to all items
    for item in items:
        module_name = item.module.__name__ if hasattr(item, 'module') else ''
        if 'authentication' in module_name or 'authorization' in module_name:
            item.add_marker(pytest.mark.auth)
        elif 'navigation' in module_name or 'ui_validation' in module_name:
            item.add_marker(pytest.mark.navigation)
        elif 'forms' in module_name or 'crud' in module_name:
            item.add_marker(pytest.mark.forms)
        elif 'regression' in module_name:
            item.add_marker(pytest.mark.regression)
        elif 'performance' in module_name:
            item.add_marker(pytest.mark.performance)


# Register custom markers
def pytest_configure(config):
    config.addinivalue_line('markers', 'auth: Authentication and Authorization tests')
    config.addinivalue_line('markers', 'navigation: Navigation and UI tests')
    config.addinivalue_line('markers', 'forms: Form interaction tests')
    config.addinivalue_line('markers', 'regression: Regression test suite')
    config.addinivalue_line('markers', 'performance: Performance smoke tests')
    config.addinivalue_line('markers', 'critical: Critical priority tests')

    base_url = config.getoption('--base-url', default='', skip=True)
    if base_url:
        os.environ['BASE_URL'] = base_url.rstrip('/') + '/'
