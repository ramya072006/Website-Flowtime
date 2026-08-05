# 🔧 Troubleshooting Guide — FlowTime Selenium Automation

---

## Issue 1: `BASE_URL points to localhost` Error

**Symptom:**
```
ValueError: ❌ BASE_URL 'http://localhost:5173/' points to localhost
```

**Cause:** Selenium must never run against localhost. The CI guard blocks this.

**Fix:**
```bash
# Set the correct GitHub Pages URL
export BASE_URL=https://<owner>.github.io/<repo>/
# Or pass via CLI
python automation/runner.py --base-url https://owner.github.io/repo/
```

---

## Issue 2: `ChromeDriver not found` / WebDriver Error

**Symptom:**
```
selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH
```

**Fix (local):**
```bash
pip install webdriver-manager --upgrade
# The DriverFactory already uses webdriver-manager — ensure it's installed
```

**Fix (CI):** The workflow uses `browser-actions/setup-chrome@v1` which handles this automatically.

---

## Issue 3: GitHub Pages Deployment Verification Fails (HTTP 404)

**Symptom:**
```
❌ Deployment verification FAILED — HTTP 404 after 15 attempts
```

**Cause:** GitHub Pages not enabled, or base path mismatch.

**Fix:**
1. Go to **Settings → Pages → Source** → set to **GitHub Actions**
2. Verify `VITE_BASE_PATH` is set to `/<repo-name>/` in the build step
3. Check that `vite.config.ts` reads `process.env.VITE_BASE_PATH`

---

## Issue 4: React App Loads but Shows Blank Page on GitHub Pages

**Symptom:** HTTP 200 but page is blank, React root empty.

**Cause:** Assets loaded with wrong base path (e.g., `/assets/` instead of `/<repo>/assets/`).

**Fix:** Verify in `vite.config.ts`:
```typescript
const base = process.env.VITE_BASE_PATH || '/';
export default defineConfig({ base, ... });
```
And in the workflow:
```yaml
VITE_BASE_PATH: /${{ github.event.repository.name }}/
```

---

## Issue 5: `ModuleNotFoundError: No module named 'automation'`

**Symptom:** Import errors when running tests.

**Fix:** Run from the repo root, not from inside the `automation/` folder:
```bash
# ✅ Correct
cd taskmanagementAI
python automation/runner.py --suite all ...

# ❌ Wrong
cd taskmanagementAI/automation
python runner.py ...
```

---

## Issue 6: Tests Fail with `TimeoutException`

**Symptom:** Many tests fail with `selenium.common.exceptions.TimeoutException`.

**Cause:** Slow network, over-loaded CI runner, or deployment not fully propagated.

**Fix:**
1. Increase `EXPLICIT_WAIT` in `automation/config/config.py` (default: 30s)
2. Increase sleep values in affected tests
3. Re-run the workflow — GitHub Pages CDN can be slow on first deploy

---

## Issue 7: `openpyxl` Excel Reports Not Generated

**Symptom:** Excel files missing from artifacts.

**Fix:**
```bash
pip install openpyxl==3.1.5
```
Or in `requirements.txt` (already included):
```
openpyxl==3.1.5
```

---

## Issue 8: Screenshots Not Captured on Failure

**Symptom:** `automation/screenshots/` folder is empty.

**Cause:** Screenshot path not created before tests run.

**Fix:** `path_config.ensure_all()` is called in `BaseTest.setUp()`. Verify it's not raising an exception by checking `automation/logs/`.

---

## Issue 9: Parallel Test Matrix Jobs All Fail

**Symptom:** All 7 matrix jobs fail simultaneously.

**Cause:** Usually the deployment is not ready.

**Fix:**
1. Check the `verify-deployment` job first
2. If HTTP 200 but SPA is slow, increase the `sleep 30` in Stage 6
3. Check if GitHub Actions runner's IP is blocked by any WAF

---

## Issue 10: `actions/deploy-pages` Fails with Permission Error

**Symptom:**
```
Error: The process '/usr/bin/git' failed with exit code 128
```

**Fix:**
1. **Settings → Actions → General → Workflow permissions** → set to **Read and write**
2. Verify the workflow has:
```yaml
permissions:
  pages: write
  id-token: write
```

---

## Issue 11: `actions/upload-pages-artifact` Fails

**Symptom:** Build artifact upload fails.

**Fix:** Ensure `apps/client/dist` exists after the build:
```bash
ls apps/client/dist  # Should have index.html and assets/
```
If empty, the `npm run build` step silently failed. Check build logs for TypeScript errors.

---

## Issue 12: Tests Pass Locally but Fail in CI

**Common causes:**
1. **Timing** — CI is slower; increase `time.sleep()` values
2. **Viewport** — CI uses 1920×1080; local may differ
3. **Fonts** — CI may not have the same system fonts
4. **Network** — CI has latency to GitHub Pages CDN

**Fix:** All tests already use generous timeouts. For flaky tests:
```python
# Add retry in conftest.py or use pytest-rerunfailures
# Already in requirements.txt: pytest-rerunfailures==14.0
```
Run with:
```bash
python -m pytest automation/tests/ --reruns 2 --reruns-delay 3
```

---

## Issue 13: `workflow_dispatch` Base URL Override Not Working

**Fix:** Ensure you pass the URL with a trailing slash:
```
https://owner.github.io/repo/   ✅
https://owner.github.io/repo    ❌ (missing trailing slash)
```

---

## Quick Health Check

Run this to verify your setup:
```bash
python -c "
import os; os.environ['BASE_URL'] = 'https://example.github.io/test/'
from automation.config import test_config, browser_config, path_config
print('BASE_URL:', test_config.base_url)
print('Headless:', browser_config.headless)
print('Reports dir:', path_config.reports)
print('✅ Config OK')
"
```
