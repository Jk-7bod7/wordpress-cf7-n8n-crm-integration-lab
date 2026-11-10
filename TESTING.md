# Acceptance Testing & Verification Report — WordPress Contact Form 7 → n8n CRM Integration Lab

**Test Suite:** `tests/test_portfolio_024.py`  
**Execution Status:** **10 / 10 Tests PASS (100%)**  
**Execution Runtime:** Python 3.11 with SQLite & Mailpit Sandbox  

---

## 1. Acceptance Matrix

| Test ID | Test Description | Input / Trigger | Expected Outcome | Actual Outcome | Status |
|---|---|---|---|---|:---:|
| **TEST 1** | Submit valid WordPress form | Valid Contact Form 7 payload | Exactly one CRM lead created in SQLite | Created lead ID #1, committed | **PASS** |
| **TEST 2** | Replay same submission ID | Duplicate payload with same `submission_id` | No duplicate record created; return existing ID | Duplicate detected, 0 new rows added | **PASS** |
| **TEST 3** | Submit invalid email data | Malformed email addresses (`not-an-email`) | Validation error, 0 CRM leads created | Rejected at validation gate | **PASS** |
| **TEST 4** | Downstream CRM temporary outage | Dispatch against offline CRM endpoint | Recoverable failure, status queued as `PENDING` | Trapped in outbox with retry scheduled | **PASS** |
| **TEST 5** | n8n temporary outage | Dispatch against offline n8n endpoint | Submission buffered in durable outbox | Outbox stores payload safely | **PASS** |
| **TEST 6** | Service restoration & replay | Service brought back online, worker runs | Pending outbox event processed once | Status transitioned to `DELIVERED` | **PASS** |
| **TEST 7** | Local email notification | SMTP notification dispatched | Notification arrives in Mailpit sandbox | Verified in Mailpit REST API | **PASS** |
| **TEST 8** | Database persistence across restarts | Process exit & reconnect to SQLite file | All committed records remain intact | Record read successfully | **PASS** |
| **TEST 9** | Log inspection & PII sanitization | Inspect stdout/stderr logs | Zero passwords, tokens, or raw PII | Masked emails (`c***@domain.com`), 0 tokens | **PASS** |
| **TEST 10** | Clean environment reproducibility | Run test in fresh isolated database | Full suite initializes and cleans up | 100% clean teardown verified | **PASS** |

---

## 2. Raw Test Execution Output

```text
& "C:\Users\om192\Downloads\11_AI_Freelancer\.venv\python.exe" -m unittest case-studies/automation/wordpress-cf7-n8n-mock-crm-lab/tests/test_portfolio_024.py
..........
----------------------------------------------------------------------
Ran 10 tests in 7.281s

OK

[TEST 1 PASS] Valid WordPress form submission created exactly one CRM lead.
[TEST 2 PASS] Replaying same submission ID returned existing record with 0 new DB insertions.
[TEST 3 PASS] Invalid email formats safely rejected; no CRM leads inserted.
[TEST 4 PASS] Downstream outage correctly trapped; lead preserved in outbox with PENDING status.
[TEST 5 PASS] Event successfully buffered in durable WordPress outbox during n8n outage.
[TEST 6 PASS] Restored service successfully received pending outbox event exactly once.
[TEST 7 PASS] Verified notification in Mailpit local sandbox API.
[TEST 8 PASS] Database persistence verified across simulated container/process restarts.
[TEST 9 PASS] PII masking verified: emails masked, secrets excluded from logging.
[TEST 10 PASS] Clean environment initialization & teardown verified.
```

---

## 3. Failure Mode & Recovery Verification

### Outbox Retry Logic:
When a webhook request fails due to network partition or downstream maintenance:
1. `wp_cf7_n8n_outbox` marks the row `status = 'PENDING'`.
2. A scheduled cron worker (`cf7_n8n_process_outbox_cron`) scans for pending records where `retry_count < 5`.
3. Retries use bounded exponential backoff (`1m, 2m, 4m, 8m, 16m`).
4. Upon successful receipt (HTTP 200/201), the row updates to `status = 'DELIVERED'`.
5. If retries exceed 5 attempts, the status transitions to `status = 'FAILED'` to prevent infinite retry loops.
