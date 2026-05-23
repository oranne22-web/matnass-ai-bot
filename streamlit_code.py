import streamlit as st
from agent import app

st.set_page_config(page_title = "Matnas AI")
st.title("הבוט  של המתנס")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("לדוגמא: איזה פעילויות יש לנערים?")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })
    with st.chat_message("user"):
        st.write(question)

    result = app.invoke({
        "user_input": question
    })

    response = result["result"]

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
