import os
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from streamlit_mic_recorder import speech_to_text, mic_recorder
import google.generativeai as genAI

# Load environment variables
load_dotenv()
genAI.configure(api_key=os.getenv("GEMINI_API"))

# Define functions
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
        model = genAI.GenerativeModel("gemini-2.0-flash-exp")
        res = model.generate_content([prompt, user_input])
        return res.text
    except Exception as e:
        return f"Error: {e}"

def speak(text):
    """
    Convert text to speech and play it.
    """
    tts = gTTS(text=text, lang="en")
    tts.save("response.mp3")
    audio = AudioSegment.from_file("response.mp3")
    play(audio)

# Streamlit App Configuration
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
if bot_name:
    st.session_state.bot_name = bot_name

# Choose interaction method
input_method = st.radio("How would you like to interact?", ["Type", "Voice"])
if input_method == "Type":
    user_input = st.text_input("What's on your mind today?", key="user_input", placeholder="Type your thoughts or concerns here...")
    if st.button("Send"):
        if user_input:
            bot_response = getGeminiRes(user_input)
            st.session_state.chat_history.append({"user": user_input, "bot": bot_response})
elif input_method == "Voice":
    st.write("Click the button to record your voice.")
    with st.spinner("Listening..."):
        text = speech_to_text(language="en", use_container_width=True, just_once=True, key="STT")
        if text:
            st.success(f"You said: {text}")
            bot_response = getGeminiRes(text)
            st.session_state.chat_history.append({"user": text, "bot": bot_response})
            st.markdown(f"**{st.session_state.bot_name}**: {bot_response}")
            speak(bot_response)
        else:
            st.info("No speech detected yet.")

# Display Chat History
st.subheader("Chat History")
if st.session_state.chat_history:
    for chat in st.session_state.chat_history:
        st.markdown(f"**You**: {chat['user']}")
        st.markdown(f"**{st.session_state.bot_name}**: {chat['bot']}")
        st.divider()
else:
    st.write("Start a conversation to see the chat history here!")
