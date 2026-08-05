"""
Test Data Management — all test data for the FlowTime automation suite.
Credentials are loaded from environment variables.
Never hardcode real passwords in this file.
"""

import os
import random
import string
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List


# ─────────────────────────────────────────────────────────────────────────────
# User Data
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class UserData:
    name: str
    email: str
    password: str
    confirm_password: str = ''

    def __post_init__(self):
        if not self.confirm_password:
            self.confirm_password = self.password


def _env(key: str, default: str) -> str:
    return os.getenv(key, default)


VALID_USER = UserData(
    name=_env('TEST_NAME', 'Selenium Tester'),
    email=_env('TEST_EMAIL', 'selenium.test@flowtime-demo.com'),
    password=_env('TEST_PASSWORD', 'SeleniumTest@123'),
)

ADMIN_USER = UserData(
    name='Admin User',
    email=_env('ADMIN_EMAIL', 'admin@flowtime-demo.com'),
    password=_env('ADMIN_PASSWORD', 'AdminTest@123'),
)


def random_string(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def random_email() -> str:
    return f"test.{random_string(6)}@flowtime-test.invalid"


def random_name() -> str:
    names = ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Drew']
    surnames = ['Smith', 'Johnson', 'Lee', 'Brown', 'Davis', 'Wilson']
    return f"{random.choice(names)} {random.choice(surnames)}"


# ─────────────────────────────────────────────────────────────────────────────
# Authentication Test Data
# ─────────────────────────────────────────────────────────────────────────────

INVALID_CREDENTIALS = [
    ('wrong@example.com', 'WrongPass123!', 'Non-existent account'),
    (VALID_USER.email, 'WrongPassword!', 'Wrong password'),
    ('', 'Password123!', 'Missing email'),
    (VALID_USER.email, '', 'Missing password'),
    ('notanemail', 'Password123!', 'Invalid email format'),
    ('a' * 256 + '@test.com', 'Pass123!', 'Email exceeds max length'),
]

INVALID_PASSWORDS = [
    ('short', 'Too short'),
    ('nouppercase123!', 'No uppercase'),
    ('NOLOWER123!', 'No lowercase'),
    ('NoNumbers!', 'No numbers'),
    ('NoSpecial123', 'No special char'),
    ('        ', 'Whitespace only'),
]

VALID_PASSWORDS = [
    'ValidPass@123',
    'SecureP@ssw0rd',
    'T3stP@ssword!',
    'FlowTime#2024',
]

STRONG_PASSWORD = 'StrongSel@ium123!'

# ─────────────────────────────────────────────────────────────────────────────
# Task Test Data
# ─────────────────────────────────────────────────────────────────────────────

TASK_PRIORITIES = ['Low', 'Medium', 'High', 'Urgent']
TASK_STATUSES = ['Todo', 'In Progress', 'Done', 'Cancelled']

SAMPLE_TASKS = [
    {'title': 'Complete project proposal', 'priority': 'High', 'description': 'Write the Q1 proposal'},
    {'title': 'Review pull request #42', 'priority': 'Medium', 'description': 'Code review for auth module'},
    {'title': 'Update documentation', 'priority': 'Low', 'description': 'Update README'},
    {'title': 'Fix login bug', 'priority': 'Urgent', 'description': 'Critical auth issue'},
    {'title': 'Deploy to staging', 'priority': 'High', 'description': 'Staging deployment'},
]

INVALID_TASK_TITLES = [
    ('', 'Empty title'),
    ('a' * 501, 'Exceeds max length'),
    ('<script>alert("xss")</script>', 'XSS attempt'),
]

# ─────────────────────────────────────────────────────────────────────────────
# UI & Navigation Test Data
# ─────────────────────────────────────────────────────────────────────────────

APP_ROUTES = [
    ('/', 'FlowTime', 'Landing'),
    ('/login', 'FlowTime', 'Login'),
    ('/register', 'FlowTime', 'Register'),
    ('/forgot-password', 'FlowTime', 'ForgotPassword'),
]

PROTECTED_ROUTES = [
    '/dashboard',
    '/tasks',
    '/habits',
    '/calendar',
    '/analytics',
    '/focus',
    '/notifications',
    '/settings',
    '/ai',
    '/team',
]

NAV_ITEMS = [
    ('dashboard', 'Dashboard'),
    ('tasks', 'Tasks'),
    ('habits', 'Habits'),
    ('calendar', 'Calendar'),
    ('analytics', 'Analytics'),
    ('focus', 'Focus'),
    ('settings', 'Settings'),
    ('ai', 'AI'),
    ('team', 'Team'),
]

# ─────────────────────────────────────────────────────────────────────────────
# Form Validation Test Data
# ─────────────────────────────────────────────────────────────────────────────

XSS_PAYLOADS = [
    '<script>alert("xss")</script>',
    '"><img src=x onerror=alert(1)>',
    "'; DROP TABLE users; --",
    '{{7*7}}',
    '${7*7}',
]

BOUNDARY_VALUES = {
    'email_max': 'a' * 243 + '@test.com',   # 254 chars total (RFC limit)
    'name_max': 'A' * 100,
    'password_min': 'Aa1!aaaa',              # 8 chars
    'password_min_minus_1': 'Aa1!aaa',      # 7 chars
    'empty': '',
    'whitespace': '   ',
    'unicode': 'Ünïcödé Näme',
    'emoji': '🚀🎯✅',
}

ACCESSIBILITY_ROLES = [
    'button', 'link', 'textbox', 'checkbox',
    'heading', 'navigation', 'main', 'form',
]

VIEWPORT_SIZES = [
    (1920, 1080, 'Full HD Desktop'),
    (1366, 768, 'HD Laptop'),
    (1280, 800, 'MacBook'),
    (768, 1024, 'iPad Portrait'),
    (414, 896, 'iPhone XR'),
    (375, 667, 'iPhone SE'),
    (360, 640, 'Android'),
    (320, 568, 'iPhone 5'),
]

PERFORMANCE_THRESHOLDS = {
    'page_load_ms': 5000,       # 5 seconds
    'dom_interactive_ms': 3000, # 3 seconds
    'first_render_ms': 2000,    # 2 seconds
    'api_response_ms': 3000,    # 3 seconds
}
