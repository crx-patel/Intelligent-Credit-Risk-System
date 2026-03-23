import streamlit as st
from auth.login import verify_login
from database.models import init_db

from dashboards.employee_dashboard import show_employee_dashboard
from dashboards.customer_dashboard import show_customer_dashboard

# Initialize database
init_db()

st.set_page_config(page_title="AI Credit Risk Advisor", layout="wide")

# Session state initialize
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# Login page
def show_login():

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


# Logout
def show_logout():
    with st.sidebar:
        st.write(f"👤 **{st.session_state.user['full_name']}**")
        st.write(f"Role: `{st.session_state.user['role']}`")
        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()


# Main routing
if not st.session_state.logged_in:
    show_login()

else:
    show_logout()

    if st.session_state.user['role'] == 'employee':
        show_employee_dashboard()

    elif st.session_state.user['role'] == 'customer':
        show_customer_dashboard()
