"""
FlowTime Selenium conftest.py
Injects BASE_URL into environment before any test module is imported.
Does NOT import Selenium — safe to run without a browser installed.
"""

import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set default BASE_URL if not already configured
if not os.getenv('BASE_URL'):
    owner = os.getenv('GITHUB_REPOSITORY_OWNER', '')
    repo_full = os.getenv('GITHUB_REPOSITORY', '')
    repo = repo_full.split('/')[-1] if '/' in repo_full else repo_full
    if owner and repo:
        os.environ['BASE_URL'] = f'https://{owner}.github.io/{repo}/'
    else:
        os.environ.setdefault('BASE_URL', 'https://ramya072006.github.io/Website-Flowtime/')

print(f"[conftest] BASE_URL = {os.environ.get('BASE_URL', 'NOT SET')}")
