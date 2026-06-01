from database import get_connection

def send_email(to_address: str, subject: str, body: str, email_type: str = "general"):
    """
    Simulates sending an email.
    Stores it in email_log table instead of using real Gmail API.
    In Week 3+, this can be replaced with real Gmail API calls.
    """
    conn = get_connection()
    conn.execute("""
        INSERT INTO email_log (to_address, subject, body, email_type, status)
        VALUES (?, ?, ?, ?, 'sent')
    """, (to_address, subject, body, email_type))
    conn.commit()
    conn.close()
    return {"status": "sent", "to": to_address, "subject": subject}

def get_email_log(limit: int = 50):
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM email_log ORDER BY sent_at DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]