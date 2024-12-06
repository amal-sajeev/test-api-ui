import streamlit as st
import wizard
from streamlit_cookies_controller import CookieController
import time
from datetime import datetime
import functions

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
        

def dynamic_assessment():
    # Ensure the current_question is initialized in session state if not already present
    if 'current_question' not in st.session_state:
        st.session_state.current_question = testwizard.start_assessment(client, st.session_state.current_session["_id"], True)
    if "message" not in st.session_state.current_question:
        st.write(st.session_state.current_question)
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
                
                selected_index = list(st.session_state.current_question["question_options"].keys())[list(st.session_state.current_question["question_options"].values()).index(selection)]


                # Proceed to the next question
                st.session_state.current_question = testwizard.dynamic_assessment_next(
                    client, 
                    st.session_state.current_session["_id"], 
                    st.session_state.current_question["_id"], 
                    selected_index
                )
                st.rerun()
            else:
                st.warning("Please select an answer before proceeding.")
    else:
        st.balloons()
        functions.results(st.session_state.current_question)

with st.container(border=True):
    dynamic_assessment()
        
