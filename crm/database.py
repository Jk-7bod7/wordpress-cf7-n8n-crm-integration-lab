import sqlite3
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

def get_db_file() -> str:
    return os.environ.get("CRM_DATABASE_PATH", os.path.join(os.path.dirname(__file__), "crm_leads.sqlite3"))

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_file())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            company TEXT,
            service_required TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_submission_id ON leads(submission_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)")
    conn.commit()
    conn.close()

def insert_lead(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if submission_id already exists (Idempotency gate)
    cursor.execute("SELECT * FROM leads WHERE submission_id = ?", (lead_data['submission_id'],))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        res = dict(existing)
        res['is_duplicate'] = True
        return res
    
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO leads (submission_id, full_name, email, phone, company, service_required, message, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lead_data['submission_id'],
        lead_data['full_name'],
        lead_data['email'].lower().strip(),
        lead_data.get('phone'),
        lead_data.get('company'),
        lead_data['service_required'],
        lead_data['message'],
        now_iso
    ))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM leads WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()
    res = dict(row)
    res['is_duplicate'] = False
    return res

def get_leads(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_lead_by_id(lead_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def count_leads() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM leads")
    count = cursor.fetchone()[0]
    conn.close()
    return count
