# Security Policy & Threat Model — WordPress Contact Form 7 → n8n CRM Integration Lab

**Project:** WordPress Contact Form 7 → n8n → Mock CRM Integration Lab  
**Classification:** Independent Local Technical Reference Implementation  

---

## 1. Core Security Principles

### A. Zero Real-World PII (Synthetic Data Only)
This repository contains exclusively synthetic mock data. No real personal identifiable information, live customer records, or proprietary corporate data are stored or processed.

### B. Loopback Network Isolation
All exposed host ports are bound strictly to `127.0.0.1`:
- `127.0.0.1:8080` (WordPress)
- `127.0.0.1:5678` (n8n)
- `127.0.0.1:8000` (Mock CRM)
- `127.0.0.1:8025` (Mailpit UI)
- `127.0.0.1:1025` (Mailpit SMTP)

No services are exposed to the public Internet or bound to `0.0.0.0`. Cloudflare tunnels, ngrok, or reverse proxies are explicitly excluded.

### C. Webhook Secret Authentication
Every webhook dispatched from WordPress to n8n must include an `X-Webhook-Secret` header. Submissions missing this header or providing an invalid token are immediately rejected with `HTTP 401 Unauthorized`.

### D. PII Masking & Safe Logging
Console output and log files produced by the Mock CRM, WordPress harness, and n8n engine mask email usernames (`j***@example.com`) and phone numbers. Passwords, API tokens, and webhook secrets are strictly scrubbed from logs.

---

## 2. Threat Analysis & Mitigations

| Threat | Risk Level | Mitigation Architecture |
|---|:---:|---|
| **Replay Attacks & Duplicate Leads** | Medium | The CRM enforces an **idempotency gate** on `submission_id` in SQLite. Replayed submissions return the original committed record without inserting duplicates. |
| **Spam & Malformed Ingestion** | Medium | Two-stage schema validation: (1) Contact Form 7 frontend validation, (2) n8n JavaScript code node validation rejecting missing fields or bad email formats with HTTP 400. |
| **Downstream Outage Data Loss** | High | The WordPress **durable outbox** stores payloads locally in SQLite/MySQL if the webhook fails, retrying up to 5 times before failing over. |
| **External Email Leakage** | Critical | Notification routing targets **Mailpit** on internal port 1025. Mailpit holds all messages in memory/local database without relaying to external SMTP servers. |
| **Credential & Secret Exposure** | High | `.env` and SQLite database files containing runtime records are strictly excluded via `.gitignore`. `.env.example` contains only non-sensitive placeholders. |
