import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"

def load_context(filename="context.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def ask_groq(messages):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error calling Groq API: {e}"

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Streamlit GPT")

context_text = load_context()
if context_text:
    st.info("Context loaded from the 'context.txt' file.")

user_input = st.text_input("Enter your question:", key="input")

if st.button("Send") and user_input.strip():
    messages = []
    if context_text:
        messages.append({"role": "system", "content": context_text})
    
    messages.extend([msg for msg in st.session_state.messages if msg["role"] != "system"])
    
    messages.append({"role": "user", "content": user_input})

    answer = ask_groq(messages)

    if "system" not in [msg["role"] for msg in st.session_state.messages] and context_text:
        st.session_state.messages.append({"role": "system", "content": context_text})
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": answer})

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**Groq:** {msg['content']}")
