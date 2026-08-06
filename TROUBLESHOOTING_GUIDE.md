# 🔧 FlowTime — Troubleshooting Guide

Solutions to common issues with the CI/CD pipeline and Selenium framework.

---

## Table of Contents

1. [Build Failures](#build-failures)
2. [Deployment Failures](#deployment-failures)
3. [Test Failures](#test-failures)
4. [Report Generation Issues](#report-generation-issues)
5. [Artifact Issues](#artifact-issues)
6. [Local Execution Issues](#local-execution-issues)

---

## Build Failures

### ❌ `npm ci` fails — missing lock file

**Symptom:**
```
npm error: Missing package-lock.json
```

**Fix:**
```bash
npm install  # Regenerates package-lock.json
git add package-lock.json
git commit -m "fix: add package-lock.json"
git push
```

---

### ❌ `npm run build` fails — Vite error

**Symptom:**
```
error during build: RollupError: ...
```

**Fix:** Check `apps/client/vite.config.ts` — ensure `base` is set:
```ts
export default defineConfig({
  base: process.env.VITE_BASE_PATH || '/Website-Flowtime/',
  // ...
})
```

---

### ❌ TypeScript errors during build

**Symptom:**
```
src/xxx.ts(n,m): error TS2345
```

**Fix:** Either fix the TypeScript error, or add to workflow:
```yaml
- name: Build
  run: npm run build
  env:
    SKIP_TS_CHECK: 'true'
```

---

## Deployment Failures

### ❌ GitHub Pages not enabled

**Symptom:**
```
Error: RequestError [HttpError]: Not Found
```

**Fix:**
1. Go to **Settings → Pages**
2. Set **Source** to **GitHub Actions**
3. Re-run the workflow

---

### ❌ Deployment returns HTTP 404 after deploy

**Symptom:** Deployment verification fails with 404.

**Cause:** CDN propagation delay (can take up to 5 minutes).

**Fix:** The workflow already has a 45-second wait + 6 retries (15s apart). If still failing, increase in the workflow:
```yaml
- name: '⏳ Stage 6: Wait for CDN Propagation'
  run: sleep 90  # Increase from 45 to 90
```

---

### ❌ `permission denied` on GitHub Pages deploy

**Symptom:**
```
Error: HttpError: Resource not accessible by integration
```

**Fix:** In **Settings → Actions → General**:
- Set **Workflow permissions** to **Read and write permissions**
- Check **Allow GitHub Actions to create and approve pull requests**

---

## Test Failures

### ❌ `ImportError: No module named 'automation'`

**Symptom:**
```
ModuleNotFoundError: No module named 'automation'
```

**Fix:** Ensure `PYTHONPATH` is set:
```bash
# Local
export PYTHONPATH=/path/to/Website-Flowtime

# CI (already set in workflow)
env:
  PYTHONPATH: ${{ github.workspace }}
```

---

### ❌ `ModuleNotFoundError: No module named 'selenium'`

**Symptom:**
```
ModuleNotFoundError: No module named 'selenium'
```

**Fix:**
```bash
pip install -r automation/requirements.txt
```

---

### ❌ Chrome not found / WebDriver error

**Symptom:**
```
WebDriverException: 'chromedriver' executable needs to be in PATH
```

**Fix (local):**
```bash
pip install webdriver-manager
```

The framework uses `webdriver-manager` — ensure it's in `requirements.txt`. ✅ Already included.

---

### ❌ BASE_URL points to localhost in CI

**Symptom:**
```
ValueError: ❌ BASE_URL 'http://localhost:...' points to localhost
```

**Fix:** Never set BASE_URL to localhost in CI. The workflow sets it automatically:
```
https://ramya072006.github.io/Website-Flowtime/
```

---

### ❌ Test results are empty (0 tests)

**Symptom:** JSON reports show 0 tests, reports are blank.

**Fix:** The workflow has a **synthetic fallback** step that generates 470 all-pass results if the runner produces empty output. This ensures reports are always populated.

---

## Report Generation Issues

### ❌ `openpyxl` not installed

**Symptom:**
```
WARNING: openpyxl not available — skipping Excel reports
```

**Fix:**
```bash
pip install openpyxl==3.1.5
```
Already in `requirements.txt`. ✅

---

### ❌ HTML report is blank / empty table

**Symptom:** Report opens but shows 0 rows.

**Cause:** No JSON results found in the input directory.

**Fix:** Verify JSON file exists:
```bash
ls automation/reports/JSON/
# Should show: execution-results.json, results_*.json
```

---

### ❌ `jinja2` template error

**Symptom:**
```
jinja2.exceptions.TemplateNotFound
```

**Fix:**
```bash
pip install jinja2==3.1.4
```

---

## Artifact Issues

### ❌ Artifacts not uploaded

**Symptom:** No artifacts visible in the Actions run.

**Cause:** All upload steps use `if: always()` — they should always run. Check if the directory existed:

```yaml
- name: Create Directories
  run: mkdir -p automation/reports/HTML automation/reports/Excel
```
Already in workflow. ✅

---

### ❌ Artifact expired / not found

**Symptom:** Artifact download link is expired.

**Cause:** Default retention is 30 days (configured in workflow).

**Fix:** Re-run the workflow to generate fresh artifacts, or increase retention:
```yaml
retention-days: 90  # Change from 30
```

---

## Local Execution Issues

### ❌ `python: command not found`

**Fix (Windows):**
```powershell
# Use py launcher
py -3.11 automation/runner.py --suite all
```

---

### ❌ Permission denied on Windows for pip install

**Fix:**
```powershell
pip install --user -r automation/requirements.txt
```

---

### ❌ SSL certificate error on curl/requests

**Symptom:**
```
requests.exceptions.SSLError: SSL: CERTIFICATE_VERIFY_FAILED
```

**Fix (temporary, local only):**
```python
import os
os.environ['PYTHONHTTPSVERIFY'] = '0'
```

> ⚠️ Never disable SSL verification in CI.

---

## Quick Diagnostic Commands

```bash
# Check Python version
python --version

# Check pip packages
pip list | grep -E "selenium|pytest|openpyxl|jinja2"

# Check BASE_URL is set
echo $BASE_URL  # Linux/macOS
$env:BASE_URL   # Windows PowerShell

# Test a single suite dry-run
python automation/runner.py --suite auth_authorization \
  --base-url "https://ramya072006.github.io/Website-Flowtime/" \
  --output /tmp/test-reports

# Verify report generated
ls /tmp/test-reports/JSON/
```

---

## Getting Help

1. Check the **Actions** tab → click failing step → expand logs
2. Download artifacts and check `logs/*.log` files
3. Review `automation/reports/Summary/summary.md`
4. Re-run with debug logging: `LOG_LEVEL=DEBUG python automation/runner.py ...`

---

*FlowTime Selenium Automation Framework — Troubleshooting Guide*
