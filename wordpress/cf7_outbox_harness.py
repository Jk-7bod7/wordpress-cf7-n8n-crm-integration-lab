"""
WordPress CF7 Integration Outbox & Client Test Harness for PORTFOLIO-024.
Mirrors the exact PHP plugin (cf7-n8n-integration.php) logic in Python for
automated integration testing and offline CI execution using only standard library.
"""
import sqlite3
import json
import uuid
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

class WordPressCF7OutboxHarness:
    def __init__(self, db_path: str, webhook_url: str, webhook_secret: str):
        self.db_path = db_path
        self.webhook_url = webhook_url
        self.webhook_secret = webhook_secret
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wp_cf7_n8n_outbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id TEXT UNIQUE NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                retry_count INTEGER NOT NULL DEFAULT 0,
                last_error TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_outbox_status ON wp_cf7_n8n_outbox(status)")
        conn.commit()
        conn.close()

    def submit_cf7_form(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        submission_id = form_data.get("submission_id") or f"cf7_{uuid.uuid4()}"
        payload = {
            "submission_id": submission_id,
            "full_name": form_data.get("full_name", "").strip(),
            "email": form_data.get("email", "").strip(),
            "phone": form_data.get("phone", "").strip() if form_data.get("phone") else None,
            "company": form_data.get("company", "").strip() if form_data.get("company") else None,
            "service_required": form_data.get("service_required", "General Consultation").strip(),
            "message": form_data.get("message", "").strip(),
            "source_form_id": form_data.get("source_form_id", 1),
            "submitted_at": datetime.now(timezone.utc).isoformat()
        }

        now_iso = datetime.now(timezone.utc).isoformat()
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.webhook_url, data=data_bytes, method="POST", headers={
            "Content-Type": "application/json",
            "X-Webhook-Secret": self.webhook_secret,
            "X-Submission-ID": submission_id,
            "User-Agent": "WordPress-CF7-n8n/1.0.0"
        })

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                status_code = resp.status
                body = resp.read().decode("utf-8", errors="ignore")
                cursor.execute("""
                    INSERT OR REPLACE INTO wp_cf7_n8n_outbox (submission_id, payload, status, retry_count, last_error, created_at, updated_at)
                    VALUES (?, ?, 'DELIVERED', 0, NULL, ?, ?)
                """, (submission_id, json.dumps(payload), now_iso, now_iso))
                conn.commit()
                conn.close()
                return {
                    "success": True,
                    "submission_id": submission_id,
                    "status": "DELIVERED",
                    "http_code": status_code,
                    "response": json.loads(body) if body.startswith("{") else body
                }
        except urllib.error.HTTPError as e:
            err_msg = f"HTTP {e.code}: {e.reason}"
            cursor.execute("""
                INSERT OR REPLACE INTO wp_cf7_n8n_outbox (submission_id, payload, status, retry_count, last_error, created_at, updated_at)
                VALUES (?, ?, 'PENDING', 1, ?, ?, ?)
            """, (submission_id, json.dumps(payload), err_msg, now_iso, now_iso))
            conn.commit()
            conn.close()
            return {
                "success": False,
                "submission_id": submission_id,
                "status": "PENDING",
                "http_code": e.code,
                "error": err_msg
            }
        except Exception as e:
            err_msg = f"Network/Connection error: {str(e)}"
            cursor.execute("""
                INSERT OR REPLACE INTO wp_cf7_n8n_outbox (submission_id, payload, status, retry_count, last_error, created_at, updated_at)
                VALUES (?, ?, 'PENDING', 1, ?, ?, ?)
            """, (submission_id, json.dumps(payload), err_msg, now_iso, now_iso))
            conn.commit()
            conn.close()
            return {
                "success": False,
                "submission_id": submission_id,
                "status": "PENDING",
                "error": err_msg
            }

    def process_outbox(self, max_retries: int = 5) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wp_cf7_n8n_outbox WHERE status = 'PENDING' AND retry_count < ? ORDER BY id ASC", (max_retries,))
        items = [dict(r) for r in cursor.fetchall()]

        results = []
        for item in items:
            payload = json.loads(item["payload"])
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self.webhook_url, data=data_bytes, method="POST", headers={
                "Content-Type": "application/json",
                "X-Webhook-Secret": self.webhook_secret,
                "X-Submission-ID": item["submission_id"],
                "User-Agent": "WordPress-CF7-n8n-Outbox/1.0.0"
            })
            now_iso = datetime.now(timezone.utc).isoformat()
            try:
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    cursor.execute("UPDATE wp_cf7_n8n_outbox SET status = 'DELIVERED', updated_at = ? WHERE id = ?", (now_iso, item["id"]))
                    results.append({"id": item["id"], "submission_id": item["submission_id"], "status": "DELIVERED"})
            except urllib.error.HTTPError as e:
                retries = item["retry_count"] + 1
                status = "FAILED" if retries >= max_retries else "PENDING"
                err = f"HTTP {e.code}: {e.reason}"
                cursor.execute("UPDATE wp_cf7_n8n_outbox SET status = ?, retry_count = ?, last_error = ?, updated_at = ? WHERE id = ?",
                               (status, retries, err, now_iso, item["id"]))
                results.append({"id": item["id"], "submission_id": item["submission_id"], "status": status, "error": err})
            except Exception as e:
                retries = item["retry_count"] + 1
                status = "FAILED" if retries >= max_retries else "PENDING"
                err = f"Network error: {str(e)}"
                cursor.execute("UPDATE wp_cf7_n8n_outbox SET status = ?, retry_count = ?, last_error = ?, updated_at = ? WHERE id = ?",
                               (status, retries, err, now_iso, item["id"]))
                results.append({"id": item["id"], "submission_id": item["submission_id"], "status": status, "error": err})

        conn.commit()
        conn.close()
        return results

    def get_outbox_items(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wp_cf7_n8n_outbox ORDER BY id ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
