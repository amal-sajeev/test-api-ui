import streamlit as st
import wizard
import pandas as pd
import json

from streamlit_cookies_controller import CookieController
controller = CookieController() 


@st.dialog("Create Bank")
def create_bank(client):
    testwizard = wizard.LearningPlatformSDK( st.session_state.api if "api" in st.session_state else controller.get("testerurl"))

    positive_weights = [1, 1.5, 2, 2.5, 3]
    negative_weights = [0.75,1.25,1.75,2.25,2.75]
    
   
    with st.form("Bankmaker"):
        bankname = st.text_input("Name of the Question Bank:")
    
        st.write("Enter weights for each difficulty in your question bank.")
    
        p1,p2,p3,p4,p5 = st.columns(5,vertical_alignment="center")
        pcol = [p1,p2,p3,p4,p5]
        n1,n2,n3,n4,n5 = st.columns(5,vertical_alignment="center")
        ncol = [n1,n2,n3,n4,n5]
        
        
        for i in range(5):
            with pcol[i]:
                positive_weights[i] =  st.number_input(str(i+1),value = positive_weights[i], key= f"pkey{i}")

        for i in range(5):
            with pcol[i]:
                negative_weights[i] =  st.number_input(str(i+1),value = negative_weights[i], key= f"nkey{i}")
        submitted = st.form_submit_button("Create Question Bank")
    if submitted:
        testwizard.create_question_bank(bank_name = bankname, positive_weights=positive_weights, negative_weights= negative_weights, client = client)
        st.rerun()


@st.dialog("View and Update Question Bank")
def bank_view(client, bank):
    testwizard = wizard.LearningPlatformSDK( st.session_state.api if "api" in st.session_state else controller.get("testerurl"))

    with st.form("QuestionUpdate"):
        bank = testwizard.get_bank(client, bank)

        edited_df = st.data_editor(pd.json_normalize(bank["question_list"])) 
        nu_dict = edited_df.to_dict(orient="records")
        for i in nu_dict:
            i["question_options"] = {}
            for j in ["a","b",'c','d']:
                i["question_options"][j] = i[f"question_options.{j}"]
                i.pop(f"question_options.{j}")
        st.write(nu_dict)
        if st.form_submit_button("Submit"):
            testwizard.update_questions(client, bank["name"], nu_dict)

@st.dialog("Create Assessment")
def create_assessment(client, user, banks):
    testwizard = wizard.LearningPlatformSDK( st.session_state.api if "api" in st.session_state else controller.get("testerurl"))

    asession = wizard.Session("","","","")
    asession.user = user
    asession.bank = st.selectbox("Select question bank", list(i['name'] for i in banks), index = None)

    if asession.bank:
        asessionbank = testwizard.get_bank(client, asession.bank)
        asession.client = client
        asession.dynamic = st.toggle("Make Session Dynamic?")
        asession.max_score = st.number_input("Maximum Score", 10)
        courses = st.multiselect("Select courses for the questions", asessionbank['courses'])
        modules = st.multiselect("Select modules for the questions", asessionbank['modules'])
        subjects = st.multiselect("Select subjects for the questions", asessionbank['subjects'])
        asession.starter_difficulty = st.select_slider("Select a difficulty to begin the test with.", [1,2,3,4,5])
        difficulty = st.multiselect("Select allowed difficulties", [1,2,3,4,5], default = [1,2,3,4,5])
        
        if courses:
            query_results = testwizard.search_questions(client, asession.bank, subjects, difficulty, courses, modules)
            
            asession.question_list = query_results
            selections = []
            
            if st.toggle("Customize Question list"):
                custom = True
                with st.container(height=200):
                    for i in query_results:
                        if st.checkbox(i['question_content'], key = query_results.index(i) ):
                            if i not in selections:
                                selections.append(i)
                        elif i in selections:
                            selections.pop(selections.index(i))
                asession.question_list = selections
            else:
                custom = False
                asession.question_list = query_results
            st.write(f"Number of Questions: {len(asession.question_list)}")
            if len(asession.question_list) > 0:
                asession.max_questions = st.select_slider("Maximum questions in the test. (0 means infinite until score is maximum.)", range(len(asession.question_list)+1))
            if st.button("Create"):
                print(asession)

                if custom:
                    if len(selections)==0:
                        st.error("Either select questions for the assessment or turn off customization!",icon = "🛑")
                    else:
                        session_id = testwizard.create_assessment(client, user, asession)
                        st.toast("Assessment created succesfully! ID: "+session_id)
                        st.rerun()
                else:
                    session_id = testwizard.create_assessment(client, user, asession)
                    st.toast("Assessment created succesfully! ID: "+session_id)
                    st.rerun()


@st.dialog("New Practice Session")
def create_practice(client, user, banks):
    testwizard = wizard.LearningPlatformSDK( st.session_state.api if "api" in st.session_state else controller.get("testerurl"))

    asession = wizard.Session("","","","")
    asession.user = user
    asession.bank = st.selectbox("Select question bank", list(i['name'] for i in banks), index = None)

    if asession.bank:
        asessionbank = testwizard.get_bank(client, asession.bank)
        asession.client = client
        asession.dynamic = st.toggle("Make Session Dynamic?")
        asession.max_score = st.number_input("Maximum Score", 10)
        courses = st.multiselect("Select courses for the questions", asessionbank['courses'])
        modules = st.multiselect("Select modules for the questions", asessionbank['modules'])
        subjects = st.multiselect("Select subjects for the questions", asessionbank['subjects'])
        asession.starter_difficulty = st.select_slider("Select a difficulty to begin the test with.", [1,2,3,4,5])
        difficulty = st.multiselect("Select allowed difficulties", [1,2,3,4,5], default = [1,2,3,4,5])
        
        if courses:
            query_results = testwizard.search_questions(client, asession.bank, subjects, difficulty, courses, modules)
            
            asession.question_list = query_results
            selections = None
            
            if st.toggle("Customize Question list"):
                    with st.container(height=200):
                        for i in query_results:
                            if st.checkbox(i['question_content'], key = query_results.index(i) ):
                                selections.append(i)
            st.write(f"Number of Questions: {len(asession.question_list)}")
            asession.max_questions = st.select_slider("Maximum questions in the test. (0 means infinite until score is maximum.)", range(len(asession.question_list)+1))
            if st.button("Create"):
                print(asession)

                if selections:
                    if len(selections)==0:
                        st.error("Either select questions for the practice session or turn off customization!",icon = "🛑")
                    else:
                        session_id = testwizard.create_practice(client, user, asession)
                        st.toast("Practice session created succesfully! ID: "+session_id)
                else:
                    session_id = testwizard.create_practice(client, user, asession)
                    st.toast("Practice session created succesfully! ID: "+session_id)
                st.rerun()


@st.dialog("Congratulations")
def results(results:dict):
    testwizard = wizard.LearningPlatformSDK( st.session_state.api if "api" in st.session_state else controller.get("testerurl"))

    st.title("You've finished!")
    st.subheader("Here are your results:", divider=True)
    for i in results.keys():
        if i !="message":
            nui = i.replace("_", " ")
            nui = nui.title()
            st.write(f"{nui} : {results[i]}")
