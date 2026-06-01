from database import get_connection
import streamlit as st

def log_action(action: str, details: str = ""):
    """Log any admin/user action to the audit table."""
    username = st.session_state.get("username", "system")
    conn = get_connection()
    conn.execute("""
        INSERT INTO audit_log (username, action, details)
        VALUES (?, ?, ?)
    """, (username, action, details))
    conn.commit()
    conn.close()

def get_recent_logs(limit: int = 50):
    conn = get_connection()
    logs = conn.execute("""
        SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in logs]