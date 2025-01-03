import os
import google.generativeai as genAI
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genAI.configure(api_key=os.getenv("GEMINI_API"))

def getGeminiRes(user_input):
    """
    Generate a response from the Gemini model with a specialized prompt.
    """
    try:
        prompt = (
            "You are a compassionate and understanding therapist. "
            "Your role is to listen attentively and respond with empathy, kindness, and emotional support. "
            "Provide thoughtful, human-like advice while validating the user's feelings. "
            "Make sure your tone is warm and caring in all responses."
        )
        model = genAI.GenerativeModel('gemini-2.0-flash-exp')
        res = model.generate_content([prompt, user_input])
        return res.text 
    except Exception as e:
        return f"Error: {e}"

# Streamlit app configuration
st.set_page_config(page_title="TherapistAI", page_icon=":robot:")
st.title("TherapistAI")
st.markdown("This is an AI-powered Therapist designed to listen and respond with empathy.")

# Initialize session state for chat history and bot name
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "bot_name" not in st.session_state:
    st.session_state.bot_name = "TherapistAI"

# Bot naming input
bot_name = st.text_input("Name your AI Therapist:", key="bot_name_input", placeholder="Enter a name for your therapist...")

# Update bot name if provided
if bot_name:
    st.session_state.bot_name = bot_name

# User input
user_input = st.text_input("What's on your mind today?", key="user_input", placeholder="Type your thoughts or concerns here...")

# Handle message sending
if st.button("Send"):
    if user_input:
        bot_response = getGeminiRes(user_input)
        st.session_state.chat_history.append({"user": user_input, "bot": bot_response})

# Display chat history
st.subheader("Chat History")
if st.session_state.chat_history:
    for chat in st.session_state.chat_history:
        st.markdown(f"**You**: {chat['user']}")
        st.markdown(f"**{st.session_state.bot_name}**: {chat['bot']}")
        st.divider()
else:
    st.write("Start a conversation to see the chat history here!")

st.caption(f"Powered by Google's Gemini LLM - Your therapist is named **{st.session_state.bot_name}**.")
