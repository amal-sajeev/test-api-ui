import streamlit as st
import wizard

testwizard = wizard.LearningPlatformSDK("http://localhost:8100")

@st.dialog("Create Assessment")
def create_assessment(client, user, banks):
    asession = wizard.Session("","","")
    asession.user = user
    asession.bank = st.selectbox("Select question bank", list(i["name"] for i in banks), index = None)

    if asession.bank:
        asessionbank = testwizard.get_bank(client, asession.bank)
        asession.client = client
        asession.dynamic = st.toggle("Make Session Dynamic?")
        asession.max_score = st.number_input("Maximum Score", 10)
        subjects = st.multiselect("Select subjects for the questions", asessionbank["subjects"])
        difficulty = st.multiselect("Select allowed difficulties", ["1",'2','3','4','5'])
        courses = st.multiselect("Select courses for the questions", asessionbank["courses"])
        modules = st.multiselect("Select modules for the questions", asessionbank["modules"])
        
        if courses:
            query_results = testwizard.search_questions(client, asession.bank, subjects, difficulty, courses, modules)
            print(query_results)
            asession.question_list = query_results
            selections = None
            if st.toggle("Customize Question list"):
                asession.question_list = selections
                with st.container(height=200):
                    for i in query_results:
                        if st.checkbox(i["question_content"], key = query_results.index(i) ):
                            selections.append(i)
                asession.question_list = selections
            if st.button("Create"):
                if selections:
                    if len(selections)==0:
                        st.error("Either select questions for the assessment or turn off customization!",icon = "🛑")
                    else:
                        session_id = testwizard.create_assessment(client, user, asession)
                        st.toast("Assessment created succesfully! ID: "+session_id)
                else:
                    session_id = testwizard.create_assessment(client, user, asession)
                    st.toast("Assessment created succesfully! ID: "+session_id)
                st.rerun()


@st.dialog("New Practice Session")
def create_practice(client, user, banks):
    asession = wizard.Session("","","")
    asession.user = user
    asession.bank = st.selectbox("Select question bank", list(i["name"] for i in banks), index = None)

    if asession.bank:
        asessionbank = testwizard.get_bank(client, asession.bank)
        asession.client = client
        subjects = st.multiselect("Select subjects for the questions", asessionbank["subjects"])
        difficulty = st.multiselect("Select allowed difficulties", ["1",'2','3','4','5'])
        courses = st.multiselect("Select courses for the questions", asessionbank["courses"])
        modules = st.multiselect("Select modules for the questions", asessionbank["modules"])
        
        if courses:
            query_results = testwizard.search_questions(client, asession.bank, subjects, difficulty, courses, modules)
            print(query_results)
            asession.question_list = query_results
            selections = None
            if st.toggle("Customize Question list"):
                asession.question_list = selections
                with st.container(height=200):
                    for i in query_results:
                        if st.checkbox(i["question_content"], key = query_results.index(i) ):
                            selections.append(i)
                asession.question_list = selections
            if st.button("Create"):
                if selections:
                    if len(selections)==0:
                        st.error("Either select questions for the practice session or turn off customization!",icon = "🛑")
                    else:
                        session_id = testwizard.create_assessment(client, user, asession)
                        st.toast("Practice session created succesfully! ID: "+session_id)
                else:
                    session_id = testwizard.create_practice(client, user, asession)
                    st.toast("Practice session created succesfully! ID: "+session_id)
                st.rerun()