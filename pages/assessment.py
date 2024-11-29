import streamlit as st
import wizard
from streamlit_cookies_controller import CookieController
import time
from datetime import datetime

st.title(f"Executing Assessment:")

testwizard = wizard.LearningPlatformSDK("http://localhost:8100")
controller = CookieController() 
 
cookies = controller.getAll() 
client = "testertest" 

if st.session_state.user_id:
    with st.sidebar:
        st.title("Current User")
        st.code(st.session_state.user_id)
        if "_id" in st.session_state.current_session:
            st.write("Current session:")
            st.code(st.session_state.current_session["_id"])
        upcoming = testwizard.get_user_upcoming(client,st.session_state.user_id)
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


