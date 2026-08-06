# 🖥️ FlowTime — Local Execution Guide

This guide explains how to run the Selenium automation framework locally.

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | ≥ 3.11 | https://python.org |
| Google Chrome | Latest stable | https://google.com/chrome |
| Node.js | ≥ 22.x | https://nodejs.org |
| Git | Any | https://git-scm.com |

---

## 1. Clone the Repository

```bash
git clone https://github.com/ramya072006/Website-Flowtime.git
cd Website-Flowtime
```

## 2. Install Python Dependencies

```bash
cd automation
pip install -r requirements.txt
cd ..
```

## 3. Set BASE_URL Environment Variable

```bash
# Windows PowerShell
$env:BASE_URL = "https://ramya072006.github.io/Website-Flowtime/"

# Linux / macOS
export BASE_URL="https://ramya072006.github.io/Website-Flowtime/"
```

> ⚠️ **IMPORTANT**: Selenium MUST run against the live GitHub Pages deployment.
> Never set BASE_URL to localhost.

## 4. Run All Test Suites

```bash
# Run all 470 tests
python automation/runner.py --suite all --base-url "$env:BASE_URL" --output automation/reports

# Run a specific suite
python automation/runner.py --suite auth_authorization --base-url "$env:BASE_URL" --output automation/reports
```

## 5. Available Suites

| Suite | Modules | Test Count |
|-------|---------|------------|
| `auth_authorization` | Authentication, Authorization | 80 |
| `navigation_ui` | Navigation, UI Validation | 80 |
| `forms_crud` | Forms, CRUD Operations | 100 |
| `validation_errors` | Input Validation, Error Handling | 60 |
| `session_file` | Session Management, File Upload | 40 |
| `accessibility_responsive` | Accessibility, Responsive Design | 40 |
| `performance_regression` | Performance Smoke, Regression | 70 |
| `all` | All modules | 470 |

## 6. Generate Reports

```bash
# HTML Report
python automation/utils/report_generator.py --output automation/reports --base-url "$env:BASE_URL"

# Excel Report
python automation/utils/excel_reporter.py --output automation/reports/Excel

# Summary
python automation/utils/summary_generator.py --input automation/reports --output automation/reports/Summary --base-url "$env:BASE_URL"
```

## 7. View Reports

```bash
# Open HTML report
start automation/reports/HTML/execution-report-all.html

# Open Excel report
start automation/reports/Excel/Automation_Test_Report_all.xlsx
```

## 8. Report Locations

```
automation/reports/
├── HTML/
│   ├── execution-report-*.html
│   └── dashboard.html
├── Excel/
│   ├── Automation_Test_Report_all.xlsx
│   ├── Passed_Test_Cases.xlsx
│   └── Summary_Report.xlsx
├── JSON/
│   └── execution-results.json
├── Summary/
│   └── summary.md
└── history/
    ├── runs.json
    └── trend.md
```

---

*FlowTime Selenium Automation Framework — Local Execution Guide*
