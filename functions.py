import streamlit as st
import wizard

testwizard = wizard.LearningPlatformSDK("http://localhost:8100")

@st.dialog("Create Assessment")
def create_assessment(client, user_id, banks):
    asession = wizard.Session("","","")
    asession.user = user_id
    asession.question_bank = st.selectbox("Select question bank", list(i["name"] for i in banks), index = None)

    if asession.question_bank:
        asessionbank = testwizard.get_bank(client, asession.question_bank)
        asession.client = client
        asession.dynamic = st.toggle("Make Session Dynamic?")
        asession.max_score = st.number_input("Maximum Score", 10)
        subjects = st.multiselect("Select subjects for the questions", asessionbank["subjects"])
        difficulty = st.multiselect("Select allowed difficulties", ["1",'2','3','4','5'])
        courses = st.multiselect("Select courses for the questions", asessionbank["courses"])
        modules = st.multiselect("Select modules for the questions", asessionbank["modules"])
        
        if courses:
            query_results = testwizard.search_questions(client, asession.question_bank, subjects, difficulty, courses, modules)
            print(query_results)
            asession.question_bank = query_results
            if st.toggle("Customize Question list"):
                selections=[]
                with st.container(height=200):
                    for i in query_results:
                        if st.checkbox(i["question_content"], key = query_results.index(i) ):
                            selections.append(i)
                asession.question_bank = selections
            if st.button("Create"):
                if selections:
                    if selections==0:
                        st.error("Either select questions for the assessment or turn off customization!",icon = "🛑")
                    else:
                        session_id = testwizard.create_assessment(client, user_id, asession)
                        st.toast("Assessment created succesfully! ID: "+session_id)
                else:
                    session_id = testwizard.create_assessment(client, user_id, asession)
                    st.toast("Assessment created succesfully! ID: "+session_id)
