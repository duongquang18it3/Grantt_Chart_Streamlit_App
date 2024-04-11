import streamlit as st
import streamlit_authenticator as stauth
import pickle
from pathlib import Path

def load_css():
    """Optional: Load CSS for styling the login page or the app itself."""
    st.markdown("""
        <style>
        /* Add your CSS here */
        </style>
    """, unsafe_allow_html=True)

def setup_auth():
    st.set_page_config(
        page_title="Epiklah",
        page_icon="favicon.ico",
        layout="wide"
    )

    load_css()

    # Names and usernames
    name = ["Admin", "Manager", "Employee1", "Employee2"]
    username = ["admin", "manager", "employee1", "employee2"]

    # Load hashed passwords from a pickle file
    file_path = Path(__file__).parent / "hashed_pw.pkl"
    with file_path.open("rb") as file:
        hashed_passwords = pickle.load(file)

    # Setup authenticator
    authenticator = stauth.Authenticate(name, username, hashed_passwords,
                                        "login_form_project", "111222", cookie_expiry_days=30)

    return authenticator

# Use this setup in your main app.py file:
# authenticator = setup_auth()
