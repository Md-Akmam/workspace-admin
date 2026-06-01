import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from auth import require_admin
from utils.helpers import get_stats, get_all_employees
from audit import get_recent_logs

def show():
    require_admin()
    st.title("📊 Admin Dashboard")
    st.markdown("---")

    stats = get_stats()

    # ── KPI Metrics ───────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👥 Total Employees",   stats["total_employees"])
    c2.metric("✅ Active",             stats["active_employees"])
    c3.metric("❌ Inactive",           stats["inactive_employees"])
    c4.metric("⏳ Pending Requests",   stats["pending_requests"])
    c5.metric("🎫 Open Tickets",       stats["open_tickets"])

    st.markdown("---")

    # ── Employee Table ────────────────────────────────────────
    st.subheader("👥 Employees")
    employees = get_all_employees()
    if employees:
        st.dataframe(pd.DataFrame(employees), use_container_width=True)
    else:
        st.info("No employees yet. Add them via Onboarding.")

    # ── Audit Log ─────────────────────────────────────────────
    st.subheader("📋 Recent Audit Log")
    logs = get_recent_logs(10)
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True)
    else:
        st.info("No activity logged yet.")