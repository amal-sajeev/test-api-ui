import streamlit as st
import wizard
from streamlit_cookies_controller import CookieController
import time
from datetime import datetime
import functions

if st.session_state.current_session['dynamic'] == True:
    st.title(f"Executing Practice Session:")
if 'last_payload' not in st.session_state:
    st.session_state.last_payload = {}
if 'last_response' not in st.session_state:
    st.session_state.last_response = {}

testwizard = wizard.LearningPlatformSDK( st.session_state.api if "api" in st.session_state else "http://localhost:8100")
controller = CookieController() 
 
cookies = controller.getAll() 
client = "testertest" 
if st.session_state.current_session:
    with st.sidebar:
        st.title("Current User")
        st.code(st.session_state.user_id)
        if "_id" in st.session_state.current_session:
            st.write("Current session:")
            st.code(st.session_state.current_session['_id'])
            st.header(":black-background[PRACTICE SESSION]")
            setup_api = st.toggle("Use hosted api?", value= False)
            if setup_api == True:
                st.session_state.api = "https://stu.globalknowledgetech.com:8100"
            else:
                st.session_state.api = "http://localhost:8100"
        with st.expander("View last non-GET Request and Response"):
            st.write("Last Request")
            with open("prequest.txt", 'r') as f:
                st.code(f.read())

            st.write("Last Response")
            with open("presponse.txt", 'r') as f:
                st.code(f.read())

        with st.expander("View last GET Request"):
            st.write("Last GET Request:")
            with open('grequest.txt' , 'r') as f:
                st.code( f.read() )

            st.write("Last GET Request:")
            with open('gresponse.txt' , 'r') as f:
                st.code( f.read() )

def dynamic_practice():
    if 'current_question' not in st.session_state:
        st.session_state.current_question = testwizard.start_practice(client, st.session_state.current_session['_id'])
    if "message" not in st.session_state.current_question:
        st.write(st.session_state.current_question)
        st.write(st.session_state.current_question['question_content'])
        
        selection = st.radio(
            "Select your answer", 
            options=st.session_state.current_question['question_options'].values(), 
            index=None, 
            key="question_selection"  
        )
        dif_options = ["Easy", "Medium", "Hard", "Again"]
        dif_selection = st.radio(
            "How difficult was it to remember the answer?",
            options = dif_options, index= None
        )
        
        
        if st.button("Next", key="next_question_btn"):
            if selection is not None:
                
                selected_index = list(st.session_state.current_question['question_options'].keys())[list(st.session_state.current_question['question_options'].values()).index(selection)]

                sel_dif_index = dif_options.index(dif_selection)+1


                # Proceed to the next question
                st.session_state.current_question = testwizard.continue_practice(
                    client,
                    st.session_state.current_session['_id'],
                    selected_index,
                    sel_dif_index
                )
                st.rerun()
            else:
                st.warning("Please select an answer before proceeding.")
    else:
        st.balloons()
        functions.results(st.session_state.current_question)


with st.container(border=True):
    dynamic_practice()
        
