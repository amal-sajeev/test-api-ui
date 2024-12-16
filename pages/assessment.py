import streamlit as st
import wizard
from streamlit_cookies_controller import CookieController
import time
from datetime import datetime
import functions

if st.session_state.current_session['dynamic'] == True:
    st.title(f"Executing Dynamic Assessment:")
else:
    st.title("Executing Static Assessment:")
if 'last_payload' not in st.session_state:
    st.session_state.last_payload = {}
if 'last_response' not in st.session_state:
    st.session_state.last_response = {}

testwizard = wizard.LearningPlatformSDK( st.session_state.api if "api" in st.session_state else "https://stu.globalknowledgetech.com:8100")
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

def dynamic_assessment():
    if 'current_question' not in st.session_state:
        st.session_state.current_question = testwizard.start_assessment(client, st.session_state.current_session['_id'], True)
    if "message" not in st.session_state.current_question:
        st.write(st.session_state.current_question)
        st.write(st.session_state.current_question['question_content'])
        
        selection = st.radio(
            "Select your answer", 
            options=st.session_state.current_question['question_options'].values(), 
            index=None, 
            key="question_selection"  
        )
        
        if st.button("Next", key="next_question_btn"):
            if selection is not None:
                
                selected_index = list(st.session_state.current_question['question_options'].keys())[list(st.session_state.current_question['question_options'].values()).index(selection)]

                # Proceed to the next question
                st.session_state.current_question = testwizard.dynamic_assessment_next(
                    client, 
                    st.session_state.current_session['_id'], 
                    st.session_state.current_question['_id'], 
                    selected_index
                )
                st.rerun()
            else:
                st.warning("Please select an answer before proceeding.")
    else:
        st.balloons()
        functions.results(st.session_state.current_question)

def static_assessment():
    st.session_state.current_question = testwizard.start_assessment(client,st.session_state.current_session['_id'])
    with st.container(height=300):
        st.write(st.session_state.current_question)
    answers=[]
    results= {}
    with st.form("statassess"):
        for i in st.session_state.current_question:
            st.write(i['question_content'])
            
            option = st.radio(
                "Select your answer", 
                options=i['question_options'].values(), 
                index=None, 
                key="question_selection"+i['_id']  
                )
            for z in i['question_options'].keys():
                if option ==  i['question_options'][z]:
                    option = z
            answers.append({
                "questionid" : i['_id'],
                "option" : option if option else ""  
            })
            

        if st.form_submit_button("Submit Assessment"):
            results = testwizard.submit_assessment(client, st.session_state.current_session['_id'], answers)    
    return(results)

with st.container(border=True):
    if st.session_state.current_session['dynamic'] == True:
        dynamic_assessment()
    else:
        st.write(static_assessment())
        
