import streamlit as st
from database import initialize_database
from auth import create_default_admin, require_login, logout
from audit import log_action

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Workspace Admin",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Initialize DB on first run ────────────────────────────────
initialize_database()
create_default_admin()

# ── Require login ─────────────────────────────────────────────
require_login()

# ── Sidebar navigation ────────────────────────────────────────
role = st.session_state.get("role", "user")
username = st.session_state.get("username", "")

with st.sidebar:
    st.markdown("### 🏢 Workspace Admin")
    st.markdown(f"👤 **{username}** `{role}`")
    st.markdown("---")

    if role == "admin":
        page = st.radio("Navigation", [
            "📊 Dashboard",
            "👥 Employees",
            "🚀 Onboarding",
            "🔑 Access Requests",
            "🚪 Offboarding",
            "🎫 IT Tickets",
            "📋 Audit Log",
        ])
    else:
        page = st.radio("Navigation", [
            "🔑 Access Requests",
            "🎫 IT Tickets",
        ])

    st.markdown("---")
    if st.button("🔓 Logout"):
        log_action("logout", f"{username} logged out")
        logout()

# ── Route to pages ────────────────────────────────────────────
if page == "📊 Dashboard":
    from pages.admin_dashboard import show
    show()
elif page == "👥 Employees":
    from pages.employees import show
    show()
# (other pages imported in later weeks)
else:
    st.info(f"🔧 {page} — Coming in future weeks!")