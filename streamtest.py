import streamlit as st
import wizard
from streamlit_cookies_controller import CookieController
import time
from datetime import datetime


testwizard = wizard.APIClient() 
controller = CookieController() 
 
cookies = controller.getAll() 
client = "testertest" 
 
if 'user_id' not in st.session_state: 
    st.session_state.user_id = "" 
if 'session_id' not in st.session_state:
    st.session_state.session_id = ""

@st.dialog(title= "User Login", width="small")
def user_login():
    user_uuid = st.text_input("Enter your id!")
    if st.button("Submit"):
        controller.set("user", user_uuid)
        st.session_state.user_id = user_uuid 
        time.sleep(0.1)
        st.rerun()

def logout():
    controller.remove("user")
    st.rerun()
 
if "user" in cookies:
    st.session_state.user_id = controller.get("user")
else:
    user_login()

with st.sidebar:
    st.title("Current User")
    st.code(st.session_state.user_id)
    st.write("Current session:")
    st.code(st.session_state.session_id)
    upcoming = testwizard.get_upcoming(client,st.session_state.user_id)
    st.write(f" {len(list(i for i in upcoming if i["due"]<0))} cards due, {len(list(i for i in upcoming if i["due"]>0))} upcoming today.")
    if st.button("Logout"):
        logout()
    with st.container(height=300):
        st.subheader("Question banks")
        titles, count, update_butt = st.columns([3.5,1.5,5], vertical_alignment= "center")
        banks = testwizard.get_all_banks(client)
        for i in banks:
            with titles:
                st.write(i["name"])
            with count:
                st.write(i["question_count"])
            with update_butt:
                st.button("View/Update", key=i)

st.title("Dashboard")
with st.container(key="Assessment Sessions"):
    st.subheader("Assessments",anchor="assessments")
    colour = lambda x : "red" if x<0.5 and x>0.01 else "blue" if x>0.5 else "green" if x>0.8 else "rainbow" if x>0.9 else "grey"
    for i in testwizard.get_assessments(client,st.session_state.user_id):
        with st.container(key=i["_id"]):
            st.subheader(i["created"], divider= colour(i["average_score"]) )
            st.write(f"Assigned: {i["created"]}")
            st.write(f"Score: {i["total_score"]}/{i["answered"]}")

with st.container(key = "Practice Sessions"):
    st.subheader("Practice Sessions", anchor="practice")
