import streamlit as st
import wizard
from streamlit_cookies_controller import CookieController
import time


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

st.title("Dashboard")

with st.container(height = 300):
    st.subheader("Question banks")
    titles, count, update_butt = st.columns([0.4,0.3,0.3])
    st.write(testwizard.get_all_banks(client))
    for i in testwizard.get_all_banks(client):
        with titles:
            st.write(i)
        with count:
            print(len(testwizard.get_bank(client,i)))
            st.write(len(testwizard.get_bank(client,i)))
        with update_butt:
            st.button("View/Update", key=i)