# ═════════════════════════════════════════════════════════════════════════════
# AI Credit Risk Advisor - Main Application
# ═════════════════════════════════════════════════════════════════════════════

"""
Main Streamlit application for AI Credit Risk Advisory System.
Handles user authentication and routing to appropriate dashboards.
"""

# Standard Library Imports
# ─────────────────────────────────────────────────────────────────────────────

# Third-Party Imports
# ─────────────────────────────────────────────────────────────────────────────
import streamlit as st

# Local Imports
# ─────────────────────────────────────────────────────────────────────────────
from auth.login import verify_login
from database.models import init_db
from dashboards.employee_dashboard import show_employee_dashboard
from dashboards.customer_dashboard import show_customer_dashboard


# ═════════════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═════════════════════════════════════════════════════════════════════════════

def initialize_app():
    """Initialize database and page configuration."""
    init_db()
    st.set_page_config(page_title="AI Credit Risk Advisor", layout="wide")


def initialize_session_state():
    """Initialize session state variables."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if "user" not in st.session_state:
        st.session_state.user = None


# ═════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═════════════════════════════════════════════════════════════════════════════

def show_login():
    """Display login page and handle authentication."""
    st.title("🏦 AI Credit Risk Advisor")
    st.subheader("Please Login to Continue")
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")

        if st.button("Login", use_container_width=True):
            user = verify_login(username, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success(f"Welcome {user['full_name']}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password!")

        st.divider()
        st.caption("Employee login: admin / admin123")
        st.caption("Customer login: customer1 / cust123")


def show_logout():
    """Display logout button and user info in sidebar."""
    with st.sidebar:
        st.write(f"👤 **{st.session_state.user['full_name']}**")
        st.write(f"Role: `{st.session_state.user['role']}`")
        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# MAIN ROUTING
# ═════════════════════════════════════════════════════════════════════════════

def main():
    """Main application entry point."""
    initialize_app()
    initialize_session_state()

    if not st.session_state.logged_in:
        show_login()
    else:
        show_logout()

        if st.session_state.user['role'] == 'employee':
            show_employee_dashboard()
        elif st.session_state.user['role'] == 'customer':
            show_customer_dashboard()


if __name__ == "__main__":
    main()
