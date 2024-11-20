import streamlit as st
import sqlite3
from hashlib import sha256
from streamlit_cookies_controller import CookieController
import time

# Initialize the cookies controller
cookie_controller = CookieController()

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('users.db')
    return conn

# Function to authenticate user
def authenticate_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    password_hash = sha256(password.encode()).hexdigest()
    c.execute('SELECT id FROM users WHERE username = ? AND password_hash = ?', (username, password_hash))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Function to handle login
def login(username, password):
    user_id = authenticate_user(username, password)
    if user_id:
        # Set a cookie with the user ID
        cookie_controller.set("user_id", user_id)
        st.session_state.user_id = user_id
        st.success("Logged in successfully!")
        time.sleep(0.5)  # Pause briefly before rerun
        st.rerun()  # Rerun to reflect the login state immediately
    else:
        st.error("Login failed")

# Function to handle logout
def logout():
    # Clear cookie by setting it to an empty value with a past expiration
    cookie_controller.set("user_id", "", max_age=0)
    st.session_state.pop("user_id", None)
    st.success("Logged out successfully!")
    time.sleep(0.5)  # Pause briefly before rerun
    st.rerun()  # Rerun to clear the interface

# Check if user is logged in
def check_session():
    # Check if the user_id cookie exists
    user_id = cookie_controller.get("user_id")
    if user_id:
        # Restore session
        st.session_state["user_id"] = user_id
        st.success("Session restored!")

# Streamlit app layout
def main():
    st.title("Simple Streamlit Login App")
    check_session()

    if "user_id" in st.session_state:
        st.write("You are logged in.")
        if st.button("Logout"):
            logout()
    else:
        st.write("Please log in.")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                login(username, password)

if __name__ == "__main__":
    main()