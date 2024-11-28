import streamlit as st
import wizard, functions
from streamlit_cookies_controller import CookieController
import time
from datetime import datetime
from wizard import *
import streamlit_sortables

testwizard = wizard.LearningPlatformSDK("http://localhost:8100")
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

if st.session_state.user_id:
    with st.sidebar:
        st.title("Current User")
        st.code(st.session_state.user_id)
        st.write("Current session:")
        st.code(st.session_state.session_id)
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


    # ASSESSMENT SCREEN ===========================================================================================

    def assessor():
        import streamlit as st
        import wizard
        from streamlit_cookies_controller import CookieController
        
        st.title("ANSWER THE QUESTION")

    # DASHBOARD (MAIN SEGMENT) ====================================================================================
    st.title("Dashboard")


    assessments, practice = st.columns(2)

    with assessments:
        if st.button("Create Assessment"):
            functions.create_assessment(client,st.session_state.user_id, banks)
        with st.container(key="Assessment Sessions", border=True):
            st.subheader("Assessments",anchor="assessments")
            colour = lambda x : "red" if x<0.5 and x>0.01 else "blue" if x>0.5 else "green" if x>0.8 else "rainbow" if x>0.9 else "grey"
            for i in testwizard.get_user_assessments(client,st.session_state.user_id):
                with st.container(key=i["_id"]):
                    st.subheader(datetime.fromisoformat(i["created"]).date(), divider= colour(i["average_score"]) )
                    st.write(datetime.fromisoformat(i["created"]).time())
                    st.write(f"Assigned: {i["created"]}")
                    st.write(f"Score: {i["total_score"]}/{i["answered"]}")
                    if i["answered"] == 0:
                        if st.button("Start Assessment"):
                            asession = wizard.Session()
                            asessionbank = testwizard.get_bank(client,)
                            asession.user = st.session_state.user_id
                            asession.question_bank = st.selectbox("Select question bank", list(i["names"] for i in banks))
                            asession.client = client
                            asession.dynamic = st.toggle("Make Session Dynamic?")
                            asession.max_score = st.number_input("Maximum Score", 10)
                            subjects = st.multiselect("Select subjects for the questions", asessjk   )
                            assessor(client, st.session_state.user_id,i["_id"])


    with practice:
        with st.container(key = "Practice Sessions", border=True):
            st.subheader("Practice Sessions", anchor="practice")
            colour = lambda x : "rainbow" if x>50 else "green" if x>10 else "blue" if x>5 else "grey"
            for i in testwizard.get_user_practice_sessions(client,st.session_state.user_id):
                with st.container(key=i["_id"]):
                    st.subheader(datetime.fromisoformat(i["created"]).date(), divider= colour(i["answered"]) )
                    st.write(datetime.fromisoformat(i["created"]).time())
                    st.write(f"Time taken: {i["time_taken"]}")
                    st.write(f"Number of questions: {len(i["question_list"])}")
