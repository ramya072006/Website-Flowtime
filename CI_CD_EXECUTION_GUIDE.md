# 🚀 FlowTime — CI/CD Execution Guide

Complete guide for the GitHub Actions CI/CD pipeline: Deploy → Verify → Test → Report.

---

## Overview

Every push to `main` or `master` automatically:

```
Push Code
    ↓
Stage 1-4:  Build & Lint
    ↓
Stage 5:    Deploy to GitHub Pages
    ↓
Stage 6-7:  Verify Deployment (HTTP probe)
    ↓
Stage 8-11: Run 470 Selenium E2E Tests (7 parallel suites)
    ↓
Stage 9-10: Generate HTML + Excel Reports
    ↓
Stage 11:   Upload Artifacts (30-day retention)
    ↓
Stage 12:   Publish GitHub Actions Summary
    ↓
Stage 13:   Store Historical Results
```

---

## Repository Setup (One-Time)

### 1. Enable GitHub Pages

Go to your repository → **Settings** → **Pages**:

| Setting | Value |
|---------|-------|
| Source | GitHub Actions |
| Branch | (managed by workflow) |

### 2. Required Permissions

The workflow file already sets these — verify in your repo settings:

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
  actions: read
```

### 3. Optional Secrets

Add these in **Settings → Secrets and variables → Actions**:

| Secret | Description | Default |
|--------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://api.placeholder.com/api` |
| `VITE_SOCKET_URL` | WebSocket URL | `https://api.placeholder.com` |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID | (empty) |
| `VITE_GEMINI_API_KEY` | Gemini AI API key | (empty) |
| `TEST_EMAIL` | Test user email | `test@flowtime-demo.com` |
| `TEST_PASSWORD` | Test user password | `TestPass123!` |

### 4. Workflow File Location

```
.github/workflows/deploy-and-test.yml
```

---

## Trigger the Pipeline

### Automatic (on every push)
```bash
git add .
git commit -m "feat: your change"
git push origin main
```

### Manual (workflow_dispatch)
1. Go to **Actions** tab in GitHub
2. Select **🚀 Deploy & E2E Test — FlowTime**
3. Click **Run workflow**
4. Optionally set `base_url` override
5. Click **Run workflow** (green button)

### Pull Request
Pipeline runs automatically on any PR to `main` or `master`.

---

## Pipeline Stages Detail

| Stage | Job | Description |
|-------|-----|-------------|
| 1 | `build` | Checkout repository |
| 2 | `build` | Install Node.js + npm dependencies |
| 3 | `build` | Build Vite client app |
| 4 | `build` | ESLint static analysis |
| 5 | `deploy` | Deploy to GitHub Pages |
| 6 | `verify-deployment` | Wait 45s for CDN propagation |
| 7 | `verify-deployment` | HTTP probe with 6 retries |
| 8 | `selenium-tests` | Run 7 parallel test suites |
| 9 | `selenium-tests` | Generate HTML report per suite |
| 10 | `selenium-tests` | Generate Excel report per suite |
| 11 | `selenium-tests` | Upload suite artifacts |
| 11b | `finalize` | Download + merge all suite artifacts |
| 12 | `finalize` | Generate master reports + summary |
| 13 | `finalize` | Store historical results |

---

## Parallel Test Suites

| Suite Name | Modules | Tests |
|------------|---------|-------|
| `auth_authorization` | Authentication, Authorization | 80 |
| `navigation_ui` | Navigation, UI Validation | 80 |
| `forms_crud` | Forms, CRUD Operations | 100 |
| `validation_errors` | Input Validation, Error Handling | 60 |
| `session_file` | Session Management, File Upload | 40 |
| `accessibility_responsive` | Accessibility, Responsive Design | 40 |
| `performance_regression` | Performance Smoke, Regression | 70 |
| **Total** | **14 modules** | **470** |

---

## Artifacts

After every run, download from **Actions → Your Run → Artifacts**:

| Artifact | Contents | Retention |
|----------|----------|-----------|
| `test-artifacts-{suite}` | Per-suite HTML, Excel, JSON, logs | 30 days |
| `final-test-reports-{N}` | Merged HTML, Excel, JSON, Summary | 30 days |
| `historical-results-run-{N}` | runs.json, trend.md | 30 days |

### Artifact Contents

```
final-test-reports-{N}/
├── HTML/
│   ├── execution-report-all.html    ← Interactive test report
│   └── dashboard.html               ← Executive dashboard
├── Excel/
│   ├── Automation_Test_Report_all.xlsx  ← 6-sheet master workbook
│   ├── Passed_Test_Cases.xlsx
│   └── Summary_Report.xlsx
├── JSON/
│   └── execution-results.json       ← Raw 470-test results
├── Summary/
│   └── summary.md                   ← GitHub summary markdown
└── history/
    ├── runs.json                    ← Rolling 100-run history
    └── trend.md                     ← Trend table
```

---

## Pass / Fail Gate

The workflow **passes** when:
- ✅ Deployment available (HTTP 200/301/302)
- ✅ Pass rate ≥ 95% (currently 100%)

The workflow **fails** when:
- ❌ Deployment returns error after 6 retries **AND** can't be verified
- ❌ Critical test failure rate > 5%

---

## Deployment URL

```
https://ramya072006.github.io/Website-Flowtime/
```

Override with `BASE_URL` input in workflow_dispatch.

---

## GitHub Actions Summary

After each run, visit the **Summary** tab to see:
- Deployment URL and status
- Total / Passed / Failed / Skipped counts
- Pass rate with ASCII progress bar
- Top passing modules
- Artifact checklist

---

*FlowTime Selenium Automation Framework — CI/CD Execution Guide*
