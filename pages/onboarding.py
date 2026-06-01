import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import datetime
from database import get_connection
from auth import require_admin
from audit import log_action
from utils.email_sim import send_email
from utils.drive_sim import create_employee_folder, create_department_subfolder
try:
    from utils.calendar_sim import create_onboarding_meeting # type: ignore
except Exception:
    def create_onboarding_meeting(employee_name, employee_email, joining_date):
        """Fallback when utils.calendar_sim cannot be imported."""
        safe_name = employee_name.replace(" ", "_")
        return {
            "event_id":  f"CAL_FALLBACK_{safe_name}_{joining_date}",
            "title":     f"Onboarding Session — {employee_name}",
            "start":     f"{joining_date} 10:00",
            "end":       f"{joining_date} 11:00",
            "meet_link": "https://meet.google.com/sim-onboard",
            "status":    "created"
        }

# ── Constants ─────────────────────────────────────────────────
DEPARTMENTS = ["HR", "Engineering", "Finance", "Marketing",
               "Sales", "Operations", "Legal", "IT Support"]

ROLES = ["Junior Employee", "Senior Employee", "Team Lead",
         "Manager", "Director", "Intern", "Contractor"]

ACCESS_OPTIONS = ["HR Drive", "Engineering Repo", "Finance Sheets",
                  "Marketing Assets", "Project Management Tool",
                  "Company Wiki", "Slack Workspace", "Email Groups"]

# ── Main page ─────────────────────────────────────────────────
def show():
    require_admin()
    st.title("🚀 Employee Onboarding")
    st.markdown("Complete the form below to onboard a new employee.")
    st.markdown("---")

    tab1, tab2 = st.tabs(["➕ New Onboarding", "📋 Onboarding Status"])

    with tab1:
        _onboarding_form()

    with tab2:
        _onboarding_status()


# ── Onboarding form ───────────────────────────────────────────
def _onboarding_form():
    st.subheader("New Employee Details")

    with st.form("onboarding_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name         = st.text_input("Full Name *")
            email        = st.text_input("Company Email *")
            department   = st.selectbox("Department *", DEPARTMENTS)

        with col2:
            role         = st.selectbox("Role/Position *", ROLES)
            joining_date = st.date_input(
                "Joining Date *",
                value=datetime.date.today() + datetime.timedelta(days=7)
            )
            phone        = st.text_input("Phone (optional)")

        st.markdown("**Required Access** (select all that apply)")
        access_selected = st.multiselect(
            "Systems & Resources", ACCESS_OPTIONS,
            default=["Company Wiki", "Slack Workspace"]
        )

        notes = st.text_area("Additional Notes (optional)", height=80)

        submitted = st.form_submit_button(
            "🚀 Start Onboarding Process", use_container_width=True
        )

    if submitted:
        # ── Validation ────────────────────────────────────────
        if not name or not email or "@" not in email:
            st.error("❌ Please provide a valid name and email.")
            return

        # ── Run the full onboarding pipeline ─────────────────
        _run_onboarding_pipeline(
            name=name,
            email=email,
            department=department,
            role=role,
            joining_date=str(joining_date),
            access=access_selected,
            notes=notes
        )


# ── Onboarding pipeline ───────────────────────────────────────
def _run_onboarding_pipeline(name, email, department, role,
                              joining_date, access, notes):
    st.markdown("---")
    st.subheader(f"⚙️ Onboarding: {name}")
    progress = st.progress(0)
    log = []

    # ── Step 1: Create Employee Record ────────────────────────
    with st.status("Step 1: Creating employee record...", expanded=True) as s:
        try:
            conn = get_connection()

            # Check for duplicate email
            existing = conn.execute(
                "SELECT employee_id FROM employees WHERE email = ?", (email,)
            ).fetchone()

            if existing:
                st.error(f"❌ Employee with email {email} already exists.")
                conn.close()
                return

            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO employees
                    (name, email, department, role, joining_date, status)
                VALUES (?, ?, ?, ?, ?, 'active')
            """, (name, email, department, role, joining_date))
            employee_id = cursor.lastrowid
            conn.commit()
            conn.close()

            s.update(label="✅ Step 1: Employee record created", state="complete")
            log.append(("✅", "Employee record", f"ID: {employee_id}"))
            log_action("onboarding_step1", f"Employee record created for {name} (ID: {employee_id})")
        except Exception as e:
            s.update(label=f"❌ Step 1 failed: {e}", state="error")
            return

    progress.progress(20)

    # ── Step 2: Create Drive Folder ───────────────────────────
    with st.status("Step 2: Creating Google Drive folder...", expanded=True) as s:
        folder = create_employee_folder(name, department)

        # Create sub-folders
        sub_docs     = create_department_subfolder(name, "Documents")
        sub_projects = create_department_subfolder(name, "Projects")

        s.update(label="✅ Step 2: Drive folder created (simulated)", state="complete")
        log.append(("✅", "Drive folder", folder["folder_url"]))
        log_action("onboarding_step2", f"Drive folder created for {name}: {folder['folder_id']}")

    progress.progress(40)

    # ── Step 3: Send Welcome Email ────────────────────────────
    with st.status("Step 3: Sending welcome email...", expanded=True) as s:
        welcome_body = f"""
Dear {name},

Welcome to the team! 🎉

We're thrilled to have you join us as {role} in the {department} department.

Your onboarding details:
- Start Date: {joining_date}
- Department: {department}
- Role: {role}
- Your Drive Folder: {folder['folder_url']}

Access provisioned:
{chr(10).join(f"  • {a}" for a in access)}

Your onboarding meeting has been scheduled for {joining_date} at 10:00 AM.
Meeting Link: https://meet.google.com/sim-onboard

Please reach out to HR if you have any questions.

Best regards,
HR & IT Administration Team
        """.strip()

        result = send_email(
            to_address=email,
            subject=f"Welcome to the Team, {name}! 🎉",
            body=welcome_body,
            email_type="welcome"
        )

        s.update(label="✅ Step 3: Welcome email sent (simulated)", state="complete")
        log.append(("✅", "Welcome email", f"Sent to {email}"))
        log_action("onboarding_step3", f"Welcome email sent to {email}")

    progress.progress(60)

    # ── Step 4: Create Calendar Meeting ──────────────────────
    with st.status("Step 4: Scheduling onboarding meeting...", expanded=True) as s:
        event = create_onboarding_meeting(
            employee_name=name,
            employee_email=email,
            joining_date=joining_date
        )

        s.update(label="✅ Step 4: Calendar event created (simulated)", state="complete")
        log.append(("✅", "Calendar meeting", f"{event['start']} — {event['meet_link']}"))
        log_action("onboarding_step4", f"Calendar event created for {name} on {joining_date}")

    progress.progress(80)

    # ── Step 5: Save Onboarding Record & Set Status ───────────
    with st.status("Step 5: Finalizing onboarding record...", expanded=True) as s:
        import json, datetime as dt
        conn = get_connection()
        conn.execute("""
            INSERT INTO onboarding_records
                (employee_id, employee_name, department, role, joining_date,
                 required_access, drive_folder, calendar_event,
                 welcome_email, status, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'sent', 'onboarded', ?)
        """, (
            employee_id, name, department, role, joining_date,
            json.dumps(access),
            folder["folder_url"],
            event["event_id"],
            dt.datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()

        s.update(label="✅ Step 5: Onboarding complete!", state="complete")
        log.append(("✅", "Status", "Onboarded ✅"))
        log_action("onboarding_complete", f"Onboarding completed for {name} ({email})")

    progress.progress(100)

    # ── Summary Card ──────────────────────────────────────────
    st.success(f"🎉 {name} has been successfully onboarded!")
    st.markdown("---")
    st.subheader("📋 Onboarding Summary")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Name:** {name}")
        st.markdown(f"**Email:** {email}")
        st.markdown(f"**Department:** {department}")
        st.markdown(f"**Role:** {role}")
        st.markdown(f"**Start Date:** {joining_date}")
    with col2:
        st.markdown(f"**Employee ID:** {employee_id}")
        st.markdown(f"**Drive Folder:** [Open Folder]({folder['folder_url']})")
        st.markdown(f"**Meeting:** {event['start']}")
        st.markdown(f"**Meet Link:** [Join]({event['meet_link']})")
        st.markdown(f"**Status:** 🟢 Onboarded")

    st.markdown("**Access Provisioned:**")
    for a in access:
        st.markdown(f"  - ✅ {a}")

    st.markdown("---")
    st.markdown("**Pipeline Steps:**")
    for icon, step, detail in log:
        st.markdown(f"{icon} **{step}** — {detail}")


# ── Onboarding status tab ─────────────────────────────────────
def _onboarding_status():
    import pandas as pd
    st.subheader("All Onboarding Records")

    conn = get_connection()
    rows = conn.execute("""
        SELECT onboarding_id, employee_name, department, role,
               joining_date, status, welcome_email, completed_at
        FROM onboarding_records
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()

    if rows:
        df = pd.DataFrame([dict(r) for r in rows])
        # Color-code status
        st.dataframe(df, use_container_width=True)
        st.caption(f"Total onboarding records: {len(rows)}")
    else:
        st.info("No onboarding records yet. Use the form above to onboard your first employee.")