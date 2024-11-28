import streamlit as st
from  streamlit_sortables import sort_items


items = [
    {'header': "Questions matching parameters", 'items' : ["What is the largest desert in the world?", "What is the longest river in South America?", "Which country has the most time zones?", "Paragraph Based questions include questions that ask you to complete, rearrange and present conclusions of a given paragraph. They are part of the reading comprehension section of the banking exams and are very important with respect to the scoring. Normally you will encounter questions that ask you to select an option that sums up or presents the ideas that are in a paragraph. We will see these and many examples in the following sections." ]},
    {"header": "Assessment Questions", "items" : []}
]

selections=[]
sorted_questions = []

with st.container(height=200):
    for i in items[0]["items"]:
        if st.checkbox(i, key = items[0]["items"].index(i) ):
            selections.append(i)

st.write(selections)