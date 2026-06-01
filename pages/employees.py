
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from auth import require_admin, hash_password
from database import get_connection
from audit import log_action

def show():
    require_admin()
    st.title("👥 Employee Management")
    st.markdown("---")

    tab1, tab2 = st.tabs(["View Employees", "Add User Account"])

    with tab1:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM employees").fetchall()
        conn.close()
        if rows:
            st.dataframe(pd.DataFrame([dict(r) for r in rows]),
                         use_container_width=True)
        else:
            st.info("No employees found. Use Onboarding to add employees.")

    with tab2:
        st.subheader("Create Login Account for Employee")
        with st.form("add_user_form"):
            username  = st.text_input("Username")
            password  = st.text_input("Password", type="password")
            role      = st.selectbox("Role", ["user", "admin"])
            submitted = st.form_submit_button("Create Account")

        if submitted and username and password:
            try:
                conn = get_connection()
                conn.execute("""
                    INSERT INTO users (username, password_hash, role)
                    VALUES (?, ?, ?)
                """, (username, hash_password(password), role))
                conn.commit()
                conn.close()
                log_action("create_user", f"Created user: {username} ({role})")
                st.success(f"✅ User '{username}' created successfully!")
            except Exception as e:
                st.error(f"Error: {e}")