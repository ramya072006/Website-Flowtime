# 🖥️ Local Execution Guide — FlowTime Selenium Automation

## Prerequisites

| Requirement | Version | Install |
|-------------|---------|---------|
| Python | 3.11+ | https://python.org |
| Google Chrome | Latest stable | https://chrome.google.com |
| Git | Any | Pre-installed |

---

## 1. Setup

```bash
# From repo root
cd automation
pip install -r requirements.txt
```

---

## 2. Configure Environment

Create `automation/.env.test`:
```env
# MANDATORY — point to the live GitHub Pages deployment
BASE_URL=https://<your-username>.github.io/<repo-name>/

# Optional test credentials
TEST_EMAIL=test@flowtime-demo.com
TEST_PASSWORD=TestPass123!

# Browser settings
HEADLESS=false          # true for headless, false to watch the browser
LOG_LEVEL=INFO
```

> ⚠️ **Never set BASE_URL to localhost.** Selenium MUST run against the live deployment.

---

## 3. Run All Tests

```bash
# From repo root
python automation/runner.py --suite all --base-url https://user.github.io/repo/
```

---

## 4. Run Individual Suites

```bash
# Authentication + Authorization (80 tests)
python automation/runner.py --suite auth_authorization --base-url https://user.github.io/repo/

# Navigation + UI Validation (80 tests)
python automation/runner.py --suite navigation_ui --base-url https://user.github.io/repo/

# Forms + CRUD (100 tests)
python automation/runner.py --suite forms_crud --base-url https://user.github.io/repo/

# Input Validation + Error Handling (60 tests)
python automation/runner.py --suite validation_errors --base-url https://user.github.io/repo/

# Session Management + File Upload (40 tests)
python automation/runner.py --suite session_file --base-url https://user.github.io/repo/

# Accessibility + Responsive Design (40 tests)
python automation/runner.py --suite accessibility_responsive --base-url https://user.github.io/repo/

# Performance + Regression (70 tests)
python automation/runner.py --suite performance_regression --base-url https://user.github.io/repo/
```

---

## 5. Run with Visible Browser (Debug Mode)

```bash
HEADLESS=false python automation/runner.py \
  --suite auth_authorization \
  --base-url https://user.github.io/repo/
```

---

## 6. Generate Reports Manually

```bash
# HTML report
python automation/utils/report_generator.py \
  --input automation/reports \
  --output automation/reports/HTML \
  --base-url https://user.github.io/repo/

# Excel report
python automation/utils/excel_reporter.py \
  --output automation/reports/Excel

# Summary markdown
python automation/utils/summary_generator.py \
  --input automation/reports \
  --output automation/reports/Summary \
  --base-url https://user.github.io/repo/
```

---

## 7. View Reports

| Report | Location |
|--------|----------|
| HTML Report | `automation/reports/HTML/execution-report-all.html` |
| Dashboard | `automation/reports/HTML/dashboard.html` |
| Excel Full | `automation/reports/Excel/Automation_Test_Report_all.xlsx` |
| Failed Tests | `automation/reports/Excel/Failed_Test_Cases.xlsx` |
| Summary MD | `automation/reports/Summary/summary.md` |
| JSON Results | `automation/reports/JSON/results_*.json` |
| Screenshots | `automation/screenshots/` |
| Logs | `automation/logs/` |

---

## 8. Run Specific Test Case

```bash
python -m pytest automation/tests/test_authentication.py::TestAuthentication::test_TC_AUTH_001_login_page_loads \
  -v --base-url https://user.github.io/repo/
```

---

## 9. Parallel Execution

```bash
python -m pytest automation/tests/ \
  -n 4 \
  --dist=loadfile \
  -v
```
