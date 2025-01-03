import streamlit as st
import wizard
from streamlit_cookies_controller import CookieController
import time
from datetime import datetime
from wizard import *
import streamlit_sortables


st.set_page_config(
        page_title="Dynamic Testing API demo",
        layout = "wide"
)


testwizard = wizard.LearningPlatformSDK( st.session_state.api if "api" in st.session_state else "https://stu.globalknowledgetech.com:8100")
controller = CookieController() 
 
cookies = controller.getAll() 
client = "testertest" 
 
if 'user_id' not in st.session_state: 
    st.session_state.user_id = "" 
if 'current_session' not in st.session_state:
    st.session_state.current_session = {}
if 'last_payload' not in st.session_state:
    st.session_state.last_payload = {}
if 'last_response' not in st.session_state:
    st.session_state.last_response = {}
if 'api' not in st.session_state:
    st.session_state.api = "https://stu.globalknowledgetech.com:8100"



@st.dialog(title= "User Login", width="small")
def user_login():
    user_uuid = st.text_input("Enter your id!")
    setup_api = st.toggle("Use hosted api?", value= True)
    if setup_api == True:
        st.session_state.api = "https://stu.globalknowledgetech.com:8100"
    else:
        st.session_state.api = "http://localhost:8100"
    st.code(st.session_state.api)
    if st.button("Submit"):
        controller.set("user", user_uuid)
        controller.set("testerurl", st.session_state.api)
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
import functions

if st.session_state.user_id:
    userlist  = testwizard.get_user_list(client)
    with st.sidebar:
        st.title("Current User")
        st.code(st.session_state.user_id)
        if st.button("Logout"):
            logout()
        st.code(st.session_state.api)
        if st.button("Switch between local and hosted API"):
            if st.session_state.api == "https://stu.globalknowledgetech.com:8100":
                st.session_state.api = "http://localhost:8100"            
            else:
                st.session_state.api = "https://stu.globalknowledgetech.com:8100"
            st.rerun()
        
        controller.set("testerurl", st.session_state.api)
        if "_id" in st.session_state.current_session:
            st.write("Current session:")
            st.code(st.session_state.current_session['_id'])
        upcoming = testwizard.get_user_upcoming(client,st.session_state.user_id)
        st.write(f" {len(list(i for i in upcoming if i['due']<0))} cards due, {len(list(i for i in upcoming if i['due']>0))} upcoming today.")
        
        
        with st.container(height=300):
            st.subheader("Question banks")
            if st.button("Create Question Bank"):
                functions.create_bank(client)     
            titles, count, update_butt, delete_butt = st.columns([3.5,1.5,4,1], vertical_alignment= "bottom")
            banks = testwizard.get_all_banks(client)
            for i in banks:
                with titles:
                    st.markdown(f"## {i['name']}")
                with count:
                    st.write(f"## {i['question_count']}")
                with update_butt:
                    if st.button("View/Update", key=i):
                        functions.bank_view(client, i['name'])
                with delete_butt:
                    if st.button("X", key = f"up{i}"):
                        testwizard.delete_bank(client, i['name'])
        
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

    

    # ASSESSMENT SCREEN ===========================================================================================

    def assessor():
        import streamlit as st
        import wizard
        from streamlit_cookies_controller import CookieController
        
        st.title("ANSWER THE QUESTION")

    # DASHBOARD (MAIN SEGMENT) ====================================================================================
    st.title("Dashboard")
    assessments, practice, drafts = st.columns(3)

    with assessments:
        if st.button("Create Assessment"):
            functions.create_assessment(client,st.session_state.user_id, banks)
        with st.container(key="Assessment Sessions", border=True):
            st.subheader("Assessments",anchor="assessments")
            colour = lambda x : "red" if x<0.5 and x>0.01 else "blue" if x>0.5 else "green" if x>0.8 else "rainbow" if x>0.9 else "grey"
            for i in testwizard.get_user_assessments(client,st.session_state.user_id):
                with st.container(key=i['_id']):
                    st.subheader(datetime.fromisoformat(i['created']).date(), divider= colour(i['score_average']) )
                    st.write(datetime.fromisoformat(i['created']).time())
                    st.write(f"Assigned: {i['created']}")
                    st.write(f"Score: {i['total_score']}/{i['max_score']}")
                    st.write(":rainbow-background[Dynamic]" if i['dynamic'] == True else ":grey-background[Static]")
                    if i['status'] == "Started":
                        if st.button("Continue Assessment", key=i['_id']+"1"):
                            controller.set("current_session", i)
                            st.session_state.current_session = controller.get("current_session") 
                            if "current_question" in st.session_state:
                                st.session_state.pop("current_question")
                            st.switch_page("pages/assessment.py")
                    elif i['status'] == "Finished":
                        if  i["dynamic"] != True:
                            st.write(f"Average: {i['score_average']}")
                        else:
                            st.write(f"Relative Score: {i['relative_score']}")
                            st.write(f"Efficiency Score: {i['efficiency_score']}")
                            st.write(f"Performance Score: {i['performance_score']}")
                            
                    else:    
                        if st.button("Start Assessment", key=i['_id']+"1"):
                            controller.set("current_session", i)
                            st.session_state.current_session = controller.get("current_session") 
                            if "current_question" in st.session_state:
                                st.session_state.pop("current_question")
                            st.switch_page("pages/assessment.py")
                    if st.button("Delete assignment", key=f"delete {i['_id']}"):
                        st.toast(testwizard.delete_assessment(client,i['_id']))
                        st.rerun()
                    st.pills("Subjects", i["primary_subjects"], disabled= True, key= i['_id']+'9')
                    with st.expander(label = "Secondary Subjects"):
                        st.pills("Secondary", i["secondary_subjects"], disabled= True, key= i['_id']+'11')


    with practice:
        if st.button("Create Practice Session"):
            functions.create_practice(client, st.session_state.user_id, banks)
        with st.container(key = "Practice Sessions", border=True):
            st.subheader("Practice Sessions", anchor="practice")
            colour = lambda x : "rainbow" if x>50 else "green" if x>10 else "blue" if x>5 else "grey"
            for i in testwizard.get_user_practice_sessions(client,st.session_state.user_id):
                with st.container(key=i['_id']):
                    st.subheader(datetime.fromisoformat(i['created']).date(), divider= colour(i['answered']) )
                    st.write(datetime.fromisoformat(i['created']).time())
                    st.write(f"Time taken: {i['time_taken']}")
                    st.write(f"Number of questions: {len(i['question_list'])}")
                    if i['status'] == "Started":
                        if st.button("Continue Assessment", key=i['_id']+"1"):
                            controller.set("current_session", i)
                            st.session_state.current_session = controller.get("current_session") 
                            if "current_question" in st.session_state:
                                st.session_state.pop("current_question")
                            st.switch_page("pages/practice.py")
                    elif i['status'] == "Finished":
                        if  i["dynamic"] != True:
                            st.write(f"Average: {i['score_average']}")
                        else:
                            st.write(f"Relative Score: {i['relative_score']}")
                            st.write(f"Efficiency Score: {i['efficiency_score']}")
                            st.write(f"Performance Score: {i['performance_score']}")
                            
                    else:    
                        if st.button("Start Assessment", key=i['_id']+"1"):
                            controller.set("current_session", i)
                            st.session_state.current_session = controller.get("current_session") 
                            if "current_question" in st.session_state:
                                st.session_state.pop("current_question")
                            st.switch_page("pages/practice.py")
                    if st.button("Delete assignment", key=f"delete {i['_id']}"):
                        st.toast(testwizard.delete_assessment(client,i['_id']))
                        st.rerun()
                    st.pills("Subjects", i["primary_subjects"], disabled= True, key= i['_id']+'9')
                    with st.expander(label = "Secondary Subjects"):
                        st.pills("Secondary", i["secondary_subjects"], disabled= True, key= i['_id']+'11')

    with drafts:
        if st.button("Create Assessment Draft"):
            functions.create_draft(client, banks)
        with st.container(key = "Draft Sessions", border = True):
            st.subheader("Drafts", anchor = "drafts")
            drafts = testwizard.get_all_drafts(client)
            for i in drafts:
                with st.container(key = i["_id"]):
                    st.code(i["_id"])
                    st.pills("Users to Assign to:", [j["user_name"] for j in userlist if j["_id"] in i["users"]])
                    st.write(f"Number of questions: {len(i['question_list'])}")
                    st.write(f"Courses Covered: {i['courses']}")
                    st.write(f"Modules Covered: {i['modules']}")
                    st.write(":rainbow-background[Dynamic]" if i['dynamic'] == True else ":grey-background[Static]")
                    if st.button("Assign to users."):
                        functions.assign_drafts(i,client)
