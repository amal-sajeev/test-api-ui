import streamlit as st
import wizard
from streamlit_cookies_controller import CookieController
import time
from datetime import datetime

if "current_question" not in st.session_state:
    st.session_state.current_question = {}

if st.session_state.current_session["dynamic"] == True:
    st.title(f"Executing Dynamic Assessment:")
else:
    st.title("Executing Static Assessment:")

testwizard = wizard.LearningPlatformSDK("http://localhost:8100")
controller = CookieController() 
 
cookies = controller.getAll() 
client = "testertest" 
if st.session_state.current_session:
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

def dynamic_assessment():
    # Ensure the current_question is initialized in session state if not already present
    if 'current_question' not in st.session_state:
        st.session_state.current_question = testwizard.start_assessment(client, st.session_state.current_session["_id"], True)
    
    # Display the current question
    st.write(st.session_state.current_question["question_content"])
    
    # Create a key for the radio to prevent automatic rerun
    selection = st.radio(
        "Select your answer", 
        options=st.session_state.current_question["question_options"].values(), 
        index=None, 
        key="question_selection"  # Add a unique key
    )
    
    # Create a flag to track if the next button is clicked
    if st.button("Next", key="next_question_btn"):
        # Ensure a selection is made before proceeding
        if selection is not None:
            # Find the index of the selected option
            
            selected_index = list(st.session_state.current_question["question_options"].values()).index(selection)
            print(selected_index)
            # Proceed to the next question
            st.session_state.current_question = testwizard.dynamic_assessment_next(
                client, 
                st.session_state.current_session["_id"], 
                st.session_state.current_question["_id"], 
                selected_index
            )
        else:
            st.warning("Please select an answer before proceeding.")

with st.container(border=True):
    dynamic_assessment()
        
