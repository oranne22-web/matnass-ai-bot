import streamlit as st
from agent import app

st.set_page_config(page_title="מתנ\"ס AI", page_icon="🏫", layout="centered")
st.title("🏫 הבוט של המתנ\"ס")
st.caption("שאל אותי על חוגים, פעילויות, מחירים וזמנים")

# היסטוריית שיחה
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# קלט
prefill = st.session_state.pop("prefill", "")
question = st.chat_input("לדוגמה: אילו פעילויות יש לנערים?") or prefill

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("מחפש..."):
            result = app.invoke({"user_input": question})
        response = result.get("result", "לא נמצאה תשובה.")
        blocks = response.split("\n\n---\n\n")
        for block in blocks:
            st.markdown(block)
            if block != blocks[-1]:
                st.divider()

    st.session_state.messages.append({"role": "assistant", "content": response})