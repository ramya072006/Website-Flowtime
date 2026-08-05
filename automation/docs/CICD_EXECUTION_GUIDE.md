# 🚀 CI/CD Execution Guide — FlowTime GitHub Actions Pipeline

## Pipeline Overview

```
Push to main/develop
        │
        ▼
┌─────────────────────┐
│  Stage 1-4: Build   │  Checkout → Install → ESLint → vite build
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  Stage 5: Deploy    │  GitHub Pages deployment
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Stage 6-7: Verify   │  Poll for HTTP 200 · React root check
└─────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 8-11: Selenium (7 parallel matrix jobs)              │
│                                                             │
│  auth_authorization  │  navigation_ui    │  forms_crud      │
│  validation_errors   │  session_file     │  acc_responsive  │
│  performance_regression                                     │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│  Stage 11-13: Finalize                       │
│  Merge → Excel → HTML → Summary → History   │
│  Pass/Fail Gate → Upload Artifacts           │
└─────────────────────────────────────────────┘
```

---

## Repository Configuration

### 1. Enable GitHub Pages

1. Go to **Settings → Pages**
2. Source: **GitHub Actions** (not a branch)
3. Save — Pages will be deployed by the workflow

### 2. Required Permissions (already in workflow)

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

### 3. Recommended Secrets (Settings → Secrets → Actions)

| Secret | Description | Required |
|--------|-------------|----------|
| `VITE_API_URL` | Backend API URL | Optional |
| `VITE_SOCKET_URL` | WebSocket URL | Optional |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID | Optional |
| `VITE_GEMINI_API_KEY` | Gemini AI key | Optional |
| `TEST_EMAIL` | Selenium test user email | Optional |
| `TEST_PASSWORD` | Selenium test user password | Optional |

If secrets are not set, the workflow uses safe placeholder defaults.

### 4. Required Variables

No repository variables required — all configuration is handled via workflow env + secrets.

---

## Workflow Triggers

| Trigger | When |
|---------|------|
| `push` to main/master/develop | Every code push |
| `pull_request` to main/master | Every PR |
| `workflow_dispatch` | Manual trigger from Actions UI |

### Manual Trigger Options

Navigate to **Actions → Deploy & E2E Test → Run workflow**:
- **Override BASE_URL** — test against a different URL
- **Skip tests** — deploy only without running Selenium

---

## Deployment URL

The BASE_URL is auto-computed as:
```
https://<repository_owner>.github.io/<repository_name>/
```

Example: `https://ramyasri.github.io/taskmanagementAI/`

---

## Pass / Fail Logic

| Condition | Result |
|-----------|--------|
| Deployment returns HTTP 200 AND pass rate ≥ 95% | ✅ Workflow passes |
| Deployment fails | ❌ Workflow fails |
| Critical test failure rate > 5% | ❌ Workflow fails |

---

## Artifacts

All artifacts are uploaded with **30-day retention**:

| Artifact Name | Contents |
|---------------|----------|
| `test-artifacts-<suite>` | Per-suite reports + screenshots + logs |
| `final-test-reports-<run>` | Merged HTML, Excel, JSON, Summary |
| `historical-results-run-<n>` | Run history for trend analysis |

---

## Monitoring

After each run, check:
1. **Actions Summary** — published at the bottom of the workflow run page
2. **Artifacts** — download from the run's artifact section
3. **Pages** — https://\<owner\>.github.io/\<repo\>/ for live deployment
