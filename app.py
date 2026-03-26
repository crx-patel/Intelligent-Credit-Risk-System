



# ═════════════════════════════════════════════════════════════════════════════
# AI Credit Risk Advisor - Main Application
# ═════════════════════════════════════════════════════════════════════════════

"""
Main Streamlit application for AI Credit Risk Advisory System.
Handles user authentication and routing to appropriate dashboards.
"""

# Third-Party Imports
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from database.db import create_user, get_user_by_username

# Local Imports
from auth.login import verify_login
from database.db import init_db
from dashboards.employee_dashboard import show_employee_dashboard
from dashboards.customer_dashboard import show_customer_dashboard


# ═════════════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═════════════════════════════════════════════════════════════════════════════

def initialize_app():
    """Initialize database and page configuration."""

    # ✅ Streamlit config FIRST
    st.set_page_config(page_title="AI Credit Risk Advisor", layout="wide")

    # 🔥 MUST RUN (no try-catch)
    init_db()


def initialize_session_state():
    """Initialize session state variables."""

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if "user" not in st.session_state:
        st.session_state.user = None
    if "page" not in st.session_state:
         st.session_state.page = "login"
        
    


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
        st.divider()

        if st.button("Create New Account"):
          st.session_state.page = "signup"
          st.rerun()


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
            
def show_signup():
    st.title("📝 Signup")

    full_name = st.text_input("Full Name")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        if full_name and username and password:

            existing_user = get_user_by_username(username)

            if existing_user:
                st.error("❌ Username already exists!")
            else:
                success = create_user(username, password, full_name)

                if success:
                    st.success("✅ Account created! Please login.")
                else:
                    st.error("❌ Signup failed")

        else:
            st.warning("⚠️ Fill all fields")

    st.divider()

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# MAIN ROUTING
# ═════════════════════════════════════════════════════════════════════════════

def main():
    """Main application entry point."""

    initialize_app()
    initialize_session_state()

    # 🔐 Not logged in
    if not st.session_state.logged_in:

        if st.session_state.page == "login":
            show_login()

        elif st.session_state.page == "signup":
            show_signup()

    # ✅ Logged in
    else:
        show_logout()

        if st.session_state.user['role'] == 'employee':
            show_employee_dashboard()

        elif st.session_state.user['role'] == 'customer':
            show_customer_dashboard()


# ═════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()