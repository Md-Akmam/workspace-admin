# utils/helpers.py
from database import get_connection

def get_all_employees():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stats():
    conn = get_connection()
    stats = {}
    stats["total_employees"]    = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    stats["active_employees"]   = conn.execute("SELECT COUNT(*) FROM employees WHERE status='active'").fetchone()[0]
    stats["inactive_employees"] = conn.execute("SELECT COUNT(*) FROM employees WHERE status='inactive'").fetchone()[0]
    stats["pending_requests"]   = conn.execute("SELECT COUNT(*) FROM requests WHERE status='pending'").fetchone()[0]
    stats["open_tickets"]       = conn.execute("SELECT COUNT(*) FROM it_tickets WHERE status='open'").fetchone()[0]
    stats["total_onboarded"]    = conn.execute("SELECT COUNT(*) FROM onboarding_records WHERE status='onboarded'").fetchone()[0]
    stats["emails_sent"]        = conn.execute("SELECT COUNT(*) FROM email_log").fetchone()[0]
    conn.close()
    return stats