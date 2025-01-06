import os
import google.generativeai as genAI
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import streamlit.components.v1 as components

# Load environment variables
load_dotenv()
genAI.configure(api_key=os.getenv("GEMINI_API"))

# Function to get response from Gemini model
def getGeminiRes(user_input):
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

# Function to speak text aloud
def speak(text):
    tts=gTTS(text=text, lang='en')
    tts.save("res.mp3")
    audio=AudioSegment.from_file("res.mp3")
    play(audio)

# Function to listen to microphone input
def listen(selected_device_id):
    recog = sr.Recognizer()
    with sr.Microphone(device_index=selected_device_id) as source:
        st.info("Listening...")
        try:
            audio = recog.listen(source, timeout=5)
            text = recog.recognize_google(audio) 
            return text
        except sr.UnknownValueError:
            return "Sorry, I did not get that."
        except sr.RequestError as e:
            return f"Sorry, an error occurred: {e}"

# JavaScript to request microphone access and display available devices
def request_microphone_access():
    js_code = """
    <script>
        let selectedDeviceId = null;
        
        navigator.mediaDevices.enumerateDevices()
            .then(devices => {
                const audioDevices = devices.filter(device => device.kind === 'audioinput');
                if (audioDevices.length > 0) {
                    const deviceSelect = document.createElement('select');
                    audioDevices.forEach(device => {
                        const option = document.createElement('option');
                        option.value = device.deviceId;
                        option.text = device.label || `Device ${device.deviceId}`;
                        deviceSelect.appendChild(option);
                    });
                    document.body.appendChild(deviceSelect);
                    
                    deviceSelect.addEventListener('change', function(event) {
                        selectedDeviceId = event.target.value;
                        console.log('Selected device ID:', selectedDeviceId);
                        // Send the selected device ID back to Streamlit
                        window.parent.postMessage({deviceId: selectedDeviceId}, "*");
                    });
                } else {
                    alert('No audio input devices found.');
                }
            })
            .catch(err => {
                console.error('Error accessing devices:', err);
            });
    </script>
    """
    components.html(js_code)

# Streamlit app configuration
st.set_page_config(page_title="TherapistAI", page_icon=":robot:")
st.title("TherapistAI")
st.markdown("This is an AI-powered Therapist designed to listen and respond with empathy.")

# Initialize session state for chat history and bot name
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "bot_name" not in st.session_state:
    st.session_state.bot_name = "TherapistAI"

# Initialize a placeholder for selected microphone device ID
if "selected_device_id" not in st.session_state:
    st.session_state.selected_device_id = None

# Request microphone access on load
request_microphone_access()

# Bot naming input
bot_name = st.text_input("Name your AI Therapist:", key="bot_name_input", placeholder="Enter a name for your therapist...")

# Update bot name if provided
if bot_name:
    st.session_state.bot_name = bot_name

# Input method selection
input_method = st.radio("How would you like to interact?", ["Type", "Voice"])

if input_method == "Type":
    user_input = st.text_input("What's on your mind today?", key="user_input", placeholder="Type your thoughts or concerns here...")
    if st.button("Send"):
        if user_input:
            bot_response = getGeminiRes(user_input)
            st.session_state.chat_history.append({"user": user_input, "bot": bot_response})
elif input_method == "Voice":
    if st.button("Speak"):
        # Check if a device has been selected
        if st.session_state.selected_device_id:
            selected_device_id = st.session_state.selected_device_id
            user_input = listen(selected_device_id)
            if user_input:
                bot_response = getGeminiRes(user_input)
                st.session_state.chat_history.append({"user": user_input, "bot": bot_response})
                speak(bot_response)
        else:
            st.warning("Please select a microphone device.")

# Display chat history
st.subheader("Chat History")
if st.session_state.chat_history:
    for chat in st.session_state.chat_history:
        st.markdown(f"**You**: {chat['user']}")
        st.markdown(f"**{st.session_state.bot_name}**: {chat['bot']}")
        st.divider()
else:
    st.write("Start a conversation to see the chat history here!")

# Handle message from JavaScript
components.html("""
<script>
    window.addEventListener("message", function(event) {
        if (event.data.deviceId) {
            const deviceId = event.data.deviceId;
            const streamlitScript = `
                <script>
                    window.parent.postMessage({selectedDeviceId: '${deviceId}'}, "*");
                </script>
            `;
            document.body.appendChild(streamlitScript);
        }
    });
</script>
""")
