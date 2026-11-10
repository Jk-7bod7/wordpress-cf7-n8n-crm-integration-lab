# System Architecture & Technical Specifications — PORTFOLIO-024

**Project:** WordPress Contact Form 7 → n8n → Mock CRM Integration Lab  
**Classification:** Independent Local Technical Reference Implementation  
**Data Policy:** 100% Synthetic Demonstration Data | Zero External Leakage  

---

## 1. System Overview

The integration lab solves the fragility of traditional webhook-based form integrations by introducing two critical reliability layers:
1. **The Client-Side Durable Outbox (WordPress):** Guarantees at-least-once delivery from WordPress even during network timeouts, downstream maintenance, or n8n restarts.
2. **The Server-Side Idempotency Gate (Mock CRM):** Guarantees exactly-once persistence using deterministic submission keys, neutralizing duplicate records caused by client retries or rapid re-submits.

---

## 2. Sequence Diagram: Normal & Resilient Flow

```mermaid
sequenceDiagram
    autonumber
    actor Visitor
    participant WP as WordPress + CF7
    participant Outbox as Plugin Outbox Table
    participant n8n as n8n Workflow Engine
    participant CRM as FastAPI Mock CRM (SQLite)
    participant Mail as Mailpit Sandbox

    Visitor->>WP: Submits Contact Form 7
    WP->>Outbox: Intercept submission & generate submission_id
    Note over Outbox: Enqueue as PENDING (At-Least-Once Delivery)

    WP->>n8n: POST /webhook/cf7-intake (Headers: X-Webhook-Secret, X-Submission-ID)
    alt n8n Unreachable or Timeout
        WP-->>Visitor: Display immediate confirmation (Form accepted)
        Note over Outbox: Outbox worker retries with exponential backoff
    else n8n Responds
        n8n->>n8n: 1. Verify X-Webhook-Secret (Reject 401 if invalid)
        n8n->>n8n: 2. Validate Schema & Email format (Reject 400 if invalid)
        n8n->>n8n: 3. Normalize fields (trim, lowercase email)
        n8n->>CRM: POST /api/leads (Idempotency Key: submission_id)
        
        alt First-Time Submission
            CRM->>CRM: Commit to SQLite (id=1, is_duplicate=False)
            CRM-->>n8n: HTTP 201 Created (Lead ID)
        else Replay / Duplicate Submission
            CRM->>CRM: Query existing submission_id
            CRM-->>n8n: HTTP 200 OK (id=1, is_duplicate=True)
        end

        n8n->>Mail: SMTP Dispatch (Port 1025)
        Mail-->>n8n: Message Accepted (Zero external dispatch)
        n8n-->>WP: HTTP 200 OK (COMMITTED)
        WP->>Outbox: Update status = DELIVERED
        WP-->>Visitor: Green confirmation screen
    end
```

---

## 3. Outbox State Machine

The custom WordPress plugin implements an outbox queue state machine:

```mermaid
stateDiagram-v2
    [*] --> PENDING: Form Submitted (Intercepted)
    PENDING --> DELIVERED: Webhook Returns HTTP 200/201
    PENDING --> PENDING: Network Timeout / HTTP 5xx (Retry < 5)
    PENDING --> FAILED: Exhausted Retries (Retry >= 5)
    FAILED --> [*]: Dead-Letter Audit Required
    DELIVERED --> [*]: Completed
```

### Outbox Database Schema (`wp_cf7_n8n_outbox`):
```sql
CREATE TABLE wp_cf7_n8n_outbox (
    id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    submission_id VARCHAR(128) NOT NULL,
    payload LONGTEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    retry_count INT(11) NOT NULL DEFAULT 0,
    last_error TEXT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_submission_id (submission_id),
    KEY idx_status (status)
);
```

---

## 4. Mock CRM Database Schema (`leads` table in SQLite):

```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    company TEXT,
    service_required TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX idx_leads_submission_id ON leads(submission_id);
CREATE INDEX idx_leads_email ON leads(email);
```

---

## 5. Security & Isolation Architecture

1. **Network Boundary:** All container ports (`8080`, `5678`, `8000`, `8025`, `1025`) are bound exclusively to loopback interface `127.0.0.1`. No public Cloudflare tunnels or external reverse proxies are attached.
2. **Mutual Secret Authentication:** Webhooks require an explicit `X-Webhook-Secret` header matching the pre-shared token.
3. **PII Masking:** Console logs mask email user identifiers (`j***@example.com`) and phone numbers to prevent log aggregation leaks.
4. **Local Email Sandbox:** Mailpit intercepts all outbound email notifications internally; zero SMTP traffic escapes to external MX records.
