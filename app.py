import streamlit as st
import requests
import os
from PIL import Image
import threading
import tempfile
import numpy as np
# NOTE: Removed direct dependency on scipy and sounddevice for a runnable example.
# In a production environment, you would need to install them:
# import sounddevice as sd
# from scipy.io.wavfile import write
import google.generativeai as genai


# NOTE: Mocking sd.rec and write for a runnable Streamlit code without extra dependencies.
# The original code's threading/audio logic would require `sounddevice` and `scipy`.
# I will use a placeholder function to prevent the code from crashing.
def mock_write(filename, fs, data):
    """Mock function for scipy.io.wavfile.write"""
    print(f"Mocked: Writing {len(data)} samples to {filename}")


def mock_rec(frames, samplerate, channels):
    """Mock function for sounddevice.rec"""
    return np.zeros((frames, channels))


def mock_wait():
    """Mock function for sounddevice.wait"""
    pass


# --- Custom CSS Styles ---
st.markdown("""
<style>
/* =============================================== */
/* ROOT VARIABLES - Harvest Glow Theme */
/* =============================================== */
:root {
    --primary-green: #4f802d;
    --primary-green-hover: #3d6621;
    --secondary-green: #9acd32;
    --accent-yellow: #f5b700;
    --earth-brown: gold;
    --sky-blue: #87ceeb;
    --leaf-light: #4E342E;
    --leaf-medium: #4E342E;
    --text-primary: green;
    --text-secondary: #666666;
    --bg-primary:#4E342E;
    --bg-secondary: #fdf5e6;
    --border-light: #d3d3d3;
    --shadow-light: rgba(0, 0, 0, 0.05);
    --shadow-medium: rgba(0, 0, 0, 0.1);
    --shadow-heavy: rgba(0, 0, 0, 0.15);
    --gradient-primary: linear-gradient(135deg, #4f802d 0%, #8fbc8f 100%);
    --gradient-bg: linear-gradient(180deg, #fdf5e6 0%, #fffaf0 50%, #fff8dc 100%);
}

/* =============================================== */
/* GLOBAL RESETS & BASE STYLES */
/* =============================================== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    color:white;
}

.stApp {
    background: var(--gradient-bg);
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
    min-height: 100vh;
    animation: backgroundPulse 20s ease-in-out infinite;
}

@keyframes backgroundPulse {
    0%, 100% { background: var(--gradient-bg); }
    50% { background: linear-gradient(180deg, #fff8dc 0%, #fffaf0 50%, #fdf5e6 100%); }
}

/* =============================================== */
/* HEADER & TITLE SECTION */
/* =============================================== */
.main-header {
    background: var(--gradient-primary);
    padding: 2.5rem 0;
    margin: -1rem -1rem 2rem -1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    border-radius: 0 0 40px 40px;
    box-shadow: 0 10px 30px var(--shadow-medium);
}

.main-header::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 150%;
    height: 150%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 1%, transparent 70%);
    animation: glowEffect 15s linear infinite;
}

@keyframes glowEffect {
    0% { transform: translate(-50%, -50%) scale(0.5); opacity: 0; }
    50% { opacity: 1; }
    100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}

h1 {
    color: white;
    font-size: 2.8rem;
    font-weight: 700;
    text-shadow: 0 4px 12px rgba(0,0,0,0.3);
    position: relative;
    z-index: 2;
    animation: titleBounce 1.5s cubic-bezier(0.68, -0.55, 0.27, 1.55);
}

@keyframes titleBounce {
    0% { transform: scale(0.8) translateY(-50px); opacity: 0; }
    70% { transform: scale(1.1) translateY(10px); opacity: 1; }
    100% { transform: scale(1) translateY(0); }
}

/* =============================================== */
/* MAIN CONTAINER */
/* =============================================== */
.main .block-container {
    max-width: 900px;
    padding: 2rem;
    background: transparent;
    animation: containerFadeIn 1s ease-out;
}

@keyframes containerFadeIn {
    0% { opacity: 0; transform: translateY(40px); }
    100% { opacity: 1; transform: translateY(0); }
}

/* =============================================== */
/* SIDEBAR - Modern Agriculture Theme */
/* =============================================== */
.stSidebar .stSelectbox label, 
.stSidebar .stRadio label {
    color: var(--earth-brown);
    font-weight: 600;
    font-size: 1.1rem;
}

.stSidebar {
    background: linear-gradient(180deg, var(--leaf-light) 0%, var(--leaf-medium) 100%);
    box-shadow: 4px 0 12px var(--shadow-light);
}

/* =============================================== */
/* CHAT MESSAGES - Modern Card Style */
/* =============================================== */
.stChatMessage {
    background: var(--bg-primary);
    border-radius: 20px;
    margin: 1.5rem 0;
    padding: 1.5rem;
    box-shadow: 0 4px 15px var(--shadow-light);
    border: 1px solid var(--border-light);
    transition: all 0.4s ease-in-out;
    animation: messageFromLeft 0.7s ease-out;
    position: relative;
    overflow: hidden;
}

@keyframes messageFromLeft {
    0% { opacity: 0; transform: translateX(-50px) scale(0.9); }
    100% { opacity: 1; transform: translateX(0) scale(1); }
}

.stChatMessage:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px var(--shadow-medium);
}

/* User messages */
.stChatMessage[data-testid="chat-message-user"] {
    background: linear-gradient(135deg, var(--leaf-light) 0%, var(--leaf-medium) 100%);
    border-left: 5px solid var(--primary-green);
    margin-left: 2rem;
    animation: messageFromRight 0.7s ease-out;
}

@keyframes messageFromRight {
    0% { opacity: 0; transform: translateX(50px) scale(0.9); }
    100% { opacity: 1; transform: translateX(0) scale(1); }
}

/* Assistant messages */
.stChatMessage[data-testid="chat-message-assistant"] {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-left: 5px solid var(--secondary-green);
    margin-right: 2rem;
}

/* Styling for text in assistant message to be black */
.stChatMessage[data-testid="chat-message-assistant"] * {
    color: black !important; 
}


/* =============================================== */
/* BUTTONS - Modern Agricultural Style */
/* =============================================== */
.stButton > button {
    background: var(--accent-yellow);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-size: 1.1rem;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 6px 15px rgba(245, 183, 0, 0.4);
    position: relative;
    overflow: hidden;
    font-weight: 600;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 10px 25px rgba(245, 183, 0, 0.5);
    background: linear-gradient(135deg, var(--accent-yellow) 0%, #f59e0b 100%);
}

.stButton > button:active {
    transform: translateY(-1px) scale(0.98);
}

/* Adjusting button padding for the new layout (File Upload/Voice Record) */
.stButton > button[kind="primary"] {
    padding: 0.5rem 1rem !important;
    font-size: 1rem !important;
}

/* =============================================== */
/* TEXT INPUT STYLING */
/* =============================================== */
.stTextInput > div > div > input {
    background: #fff8dc; /* Light background for visibility */
    border: none;
    padding: 1rem 1.5rem;
    font-size: 1rem;
    color: black; /* Text is black for high contrast */
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px var(--shadow-light);
    border-radius: 12px; /* Matching border radius */
}

.stTextInput > div > div > input:focus {
    outline: none;
    border-color: var(--primary-green);
    box-shadow: 0 0 0 3px rgba(79, 128, 45, 0.2);
    background: #fff8e1;
}

.stTextInput > div > div > input::placeholder {
    color: #666; /* Placeholder text is dark gray */
    font-style: italic;
}

/* Custom styling for the icon buttons at the bottom */
.icon-button-container .stButton > button {
    background: var(--bg-primary) !important;
    border-radius: 12px;
    padding: 0.5rem 1rem; /* Smaller padding for a cleaner icon button look */
    box-shadow: 0 4px 10px var(--shadow-medium);
    transition: background 0.3s, transform 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem; /* Text size for the new labels */
}

.icon-button-container .stButton > button:hover {
    background: #6D4C41 !important; /* Slightly lighter brown on hover */
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
}

/* =============================================== */
/* FINAL TOUCHES - FIXING VISIBILITY */
/* =============================================== */
/* Ensure the text color in user message is white for contrast against dark background */
.stChatMessage[data-testid="chat-message-user"] * {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# --- Configuration ---
try:
    # Get the API key from Streamlit's secrets
    # NOTE: This will only work if secrets are configured. Using a placeholder
    # for local testing if the key is not set.
    api_key = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    # For a runnable example, we will mock the API call if the key is missing.
    # In production, this error is appropriate.
    st.warning("Google API Key not found. Using a mocked response for demonstration.")
    # Stop is commented out to allow the code to run locally without a key
    # st.stop()

# Configure the Gemini API (only if key is available)
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    # Mocking the model for local execution without API key
    class MockModel:
        def generate_content(self, prompt_parts):
            class MockResponse:
                text = "Mocked AI Response: The API key is not configured, but I am an expert Root Coder AI assistant! Your question was processed. To get a real answer, please set your Google API Key."

            return MockResponse()


    model = MockModel()

# --- Multilingual Text ---
LANGUAGES = {
    "English": {
        "title": "Root Coder AI - Farmer's Assistant for India",
        "welcome_message": "Hello! I am Root Coder AI, your expert agricultural assistant for India Farmers. How can I help you with your farming today? You can ask a question or upload an image.",
        "uploader_label": "Upload an image of your crop, pest, or soil",
        "input_placeholder": "Ask your question here...",
        "language_select": "Choose Language",
        "error_text": "Sorry, an error occurred with the AI model. Please try again.",
        "spinner_text": "Thinking...",
        # New texts for the buttons
        "file_upload_btn": " File Upload",
        "voice_record_btn": " Voice Record",
        "voice_stop_btn": "⏹️ Stop Recording",
    },
    "മലയാളം (Malayalam)": {
        "title": "റൂട്ട് കോഡർ AI - ഇന്ത്യയിലെ കർഷക സഹായി 🇮🇳",
        "welcome_message": "നമസ്കാരം! ഞാൻ റൂട്ട് കോഡർ AI ആണ്, ഇന്ത്യയിലെ നിങ്ങളുടെ കാർഷിക വിദഗ്ധ സഹായി. ഇന്ന് നിങ്ങളുടെ കൃഷിയിൽ ഞാൻ എങ്ങനെ സഹായിക്കണം? നിങ്ങൾക്ക് ഒരു ചോദ്യം ചോദിക്കാം അല്ലെങ്കിൽ ഒരു ചിത്രം അപ്‌ലോഡ് ചെയ്യാം.",
        "uploader_label": "നിങ്ങളുടെ വിള, കീടം, അല്ലെങ്കിൽ മണ്ണിന്റെ ഒരു ചിത്രം അപ്‌ലോഡ് ചെയ്യുക",
        "input_placeholder": "നിങ്ങളുടെ ചോദ്യം ഇവിടെ ചോദിക്കൂ...",
        "language_select": "ഭാഷ തിരഞ്ഞെടുക്കുക",
        "error_text": "ക്ഷമിക്കണം, ഒരു പിശക് സംഭവിച്ചു. ദയവായി വീണ്ടും ശ്രമിക്കുക.",
        "spinner_text": "ചിന്തിക്കുന്നു...",
        "file_upload_btn": " ഫയൽ അപ്‌ലോഡ്",
        "voice_record_btn": " ശബ്‌ദം റെക്കോർഡ്",
        "voice_stop_btn": "⏹️ റെക്കോർഡിംഗ് നിർത്തുക",
    },
    "हिन्दी (Hindi)": {
        "title": "रूट कोडर AI - भारत किसान सहायक 🇮🇳",
        "welcome_message": "नमस्ते! मैं रूट कोडर AI हूँ, पूरे भारत में आपके कृषि विशेषज्ञ सहायक। आज मैं आपकी खेती में कैसे मदद कर सकता हूँ? आप मुझसे कोई सवाल पूछ सकते हैं या किसी पौधे की तस्वीर अपलोड कर सकते हैं।",
        "uploader_label": "अपनी फसल, कीट, या मिट्टी की एक तस्वीर अपलोड करें",
        "input_placeholder": "अपना सवाल यहाँ पूछें...",
        "language_select": "भाषा चुनें",
        "error_text": "क्षमा करें, एक त्रुटि हुई। कृपया पुन: प्रयास करें।",
        "spinner_text": "सोच रहा हूँ...",
        "file_upload_btn": " फ़ाइल अपलोड",
        "voice_record_btn": " आवाज़ रिकॉर्ड",
        "voice_stop_btn": "⏹️ रिकॉर्डिंग रोकें",
    },
    "ಕನ್ನಡ (Kannada)": {
        "title": "ರೂಟ್ ಕೋಡರ್ AI - ಭಾರತ ರೈತ ಸಹಾಯಕ 🇮🇳",
        "welcome_message": "ನಮಸ್ಕಾರ! ನಾನು ರೂಟ್ ಕೋಡರ್ AI, ಭಾರತದಾದ್ಯಂತ ನಿಮ್ಮ ಕೃಷಿ ತಜ್ಞ ಸಹಾಯಕ. ಇಂದು ನಿಮ್ಮ ಕೃಷಿಯಲ್ಲಿ ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ? ನೀವು ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಬಹುದು ಅಥವಾ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಬಹುದು.",
        "uploader_label": "ನಿಮ್ಮ ಬೆಳೆ, ಕೀಟ, ಅಥವಾ ಮಣ್ಣಿನ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "input_placeholder": "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಇಲ್ಲಿ ಕೇಳಿ...",
        "language_select": "ಭಾಷೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ",
        "error_text": "ಕ್ಷಮಿಸಿ, ದೋಷ ಸಂಭವಿಸಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
        "spinner_text": "ಆಲೋಚಿಸಲಾಗುತ್ತಿದೆ...",
        "file_upload_btn": "ಫೈಲ್ ಅಪ್‌ಲೋಡ್",
        "voice_record_btn": "️ ಧ್ವನಿ ರೆಕಾರ್ಡ್",
        "voice_stop_btn": "⏹️ ರೆಕಾರ್ಡಿಂಗ್ ನಿಲ್ಲಿಸಿ",
    }
}


# --- Helper Function for Gemini API (System Prompt updated to "India") ---
def get_gemini_response(input_text, image, lang_code):
    system_prompt = f"""
    You are an expert agricultural assistant for farmers across India.
    Your name is 'Root Coder AI'.
    Analyze the user's question and the provided image (if any).
    Provide a concise, helpful, and easy-to-understand answer.
    If the question is about a plant disease, agriculture issues, or livestock, suggest organic and chemical remedies suitable for India's climate.
    If the question is about current market prices, politely state that you cannot access real-time data but can offer general advice.
    If you do not know the answer, say that you are still learning about this topic.
    Respond ONLY in the following language: {lang_code}.
    """

    # Mock response if API key is missing
    if not api_key:
        return model.generate_content(None).text

    prompt_parts = [system_prompt, "\n\n", input_text]

    if image:
        prompt_parts.append(image)

    try:
        response = model.generate_content(prompt_parts)

        # Ensures clean name usage
        response_text = response.text.strip().replace("Krishi Mitra AI", "Root Coder AI")

        return response_text

    except Exception as e:
        # Fallback language error text is used
        error_lang = "English" if selected_language not in LANGUAGES else selected_language
        st.error(f"An API error occurred: {e}")
        return LANGUAGES[error_lang]["error_text"]


# --- Audio Logic Stubs (Using Mocks) ---
def record_audio_thread():
    fs = 44100
    st.session_state.recording_data = []
    # Using mock functions for external library calls
    try:
        while st.session_state.recording:
            # data = sd.rec(4410, samplerate=fs, channels=1) # Original
            data = mock_rec(4410, samplerate=fs, channels=1)  # Mock
            # sd.wait() # Original
            mock_wait()  # Mock
            st.session_state.recording_data.append(data)
    except Exception as e:
        st.error(f"Audio recording error: {e}")
        st.session_state.recording = False


def toggle_recording():
    st.session_state.recording = not st.session_state.recording
    if st.session_state.recording:
        # Reset image uploader when starting voice recording
        st.session_state.show_image_uploader = False
        st.session_state.audio_file = None
        # Start recording thread
        threading.Thread(target=record_audio_thread, daemon=True).start()
    else:
        # Stop recording
        if st.session_state.recording_data:
            fs = 44100
            # NOTE: np.concatenate requires numpy
            audio = np.concatenate(st.session_state.recording_data, axis=0)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            # write(temp_file.name, fs, audio) # Original
            mock_write(temp_file.name, fs, audio)  # Mock
            st.session_state.audio_file = temp_file.name
            st.rerun()
        else:
            # If recording stopped immediately without data
            st.session_state.audio_file = None
            st.info("Recording stopped. No audio data captured.")


def toggle_image_uploader():
    st.session_state.show_image_uploader = not st.session_state.show_image_uploader
    # Hide audio message if we toggle image
    if st.session_state.show_image_uploader:
        st.session_state.recording = False
        st.session_state.audio_file = None
    st.rerun()


# --- Streamlit App ---

# --- Language Selection in Sidebar ---
st.sidebar.title("Settings")
selected_language = st.sidebar.radio(
    label=LANGUAGES["English"]["language_select"],
    options=list(LANGUAGES.keys())
)

ui_texts = LANGUAGES[selected_language]

# --- Main App Interface ---
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title(ui_texts["title"])
st.markdown('</div>', unsafe_allow_html=True)

# Initial State Setup
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": ui_texts["welcome_message"]}
    ]

# Setup state variables
if "recording" not in st.session_state:
    st.session_state.recording = False
if "audio_file" not in st.session_state:
    st.session_state.audio_file = None
if "recording_data" not in st.session_state:
    st.session_state.recording_data = []
if "show_image_uploader" not in st.session_state:
    st.session_state.show_image_uploader = False

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "image" in message and isinstance(message["image"], Image.Image):
            st.image(message["image"], width=250)

# --- Input Area: Buttons and Chat Input ---

# Create two columns for the custom buttons (File Upload and Voice Record)
button_cols = st.columns([1, 1])

# Apply custom class to the column div for specific button styling
st.markdown('<div class="icon-button-container">', unsafe_allow_html=True)

with button_cols[0]:
    # File Upload Button
    if st.button(ui_texts["file_upload_btn"], key="file_upload_btn_key", use_container_width=True):
        toggle_image_uploader()

with button_cols[1]:
    # Voice Recording Button
    voice_label = ui_texts["voice_stop_btn"] if st.session_state.recording else ui_texts["voice_record_btn"]
    if st.button(voice_label, key="voice_record_btn_key", use_container_width=True):
        toggle_recording()

st.markdown('</div>', unsafe_allow_html=True)

# --- Display Uploader or Audio Player if active ---
uploaded_image = None
if st.session_state.show_image_uploader:
    with st.expander(ui_texts["uploader_label"], expanded=True):
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
            key="image_uploader"
        )
        if uploaded_file is not None:
            # Load the image and store the PIL object
            uploaded_image = Image.open(uploaded_file)
            st.image(uploaded_image, caption='Uploaded Image.', use_container_width=True, width=150)
            st.success("Image uploaded successfully!")

# Audio recording messages
if st.session_state.recording:
    st.info(f"🎤 {ui_texts['voice_stop_btn'].split(' ')[-1]} in progress... Click the stop button above to save.")
elif st.session_state.audio_file:
    # Display audio (will use the file path stored)
    st.audio(st.session_state.audio_file)
    st.success("Audio recorded and saved successfully! Note: Speech-to-text processing is not yet implemented.")

# --- Chat Input Form ---
# The actual question is submitted via this form
with st.form(key='chat_form', clear_on_submit=True):
    # Chat input box
    prompt_input = st.text_input(
        "",
        placeholder=ui_texts["input_placeholder"],
        label_visibility="collapsed",
        key="prompt_text_input"  # Key to grab the value
    )
    # Submission button
    submitted = st.form_submit_button("Submit", type="primary", use_container_width=True)

# --- Process Chat Input ---
if submitted and prompt_input:
    # Get the image if the uploader is visible and a file was uploaded
    image_to_process = uploaded_image if uploaded_image else None
    prompt = prompt_input

    # Reset states after submission
    st.session_state.show_image_uploader = False
    st.session_state.audio_file = None

    # Add user message
    user_message = {"role": "user", "content": prompt}
    if image_to_process:
        user_message["image"] = image_to_process
    st.session_state.messages.append(user_message)

    # Rerun to display user message and kick off the response generation
    st.rerun()

# Processing the latest user message
if st.session_state.messages[-1]["role"] == "user" and st.session_state.messages[-1]["content"] not in [
    msg.get("content") for msg in st.session_state.messages[:-1] if msg["role"] == "assistant"]:
    latest_user_message = st.session_state.messages[-1]
    prompt = latest_user_message["content"]
    image_to_process = latest_user_message.get("image")

    # Assistant reply
    with st.chat_message("assistant"):
        with st.spinner(ui_texts["spinner_text"]):
            # Determine the language code for the system prompt
            lang_code = (
                "Malayalam" if selected_language == "മലയാളം (Malayalam)"
                else "Hindi" if selected_language == "हिन्दी (Hindi)"
                else "Kannada" if selected_language == "ಕನ್ನಡ (Kannada)"
                else "English"
            )
            response_text = get_gemini_response(prompt, image_to_process, lang_code)
            st.write(response_text)

    # Append assistant's response to history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.rerun()

# --- Custom Footer (Centered) ---
st.markdown("""
<style>
/* 1. Footer Container Styling: Fixed at bottom, full width, high-contrast */
/* IMPORTANT: Hiding the default footer below, but keeping the sidebar visible */
footer {visibility: hidden;} 

.custom-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    /* Gradient Background: Deep Green/Gold Theme */
    background: linear-gradient(135deg, #16a34a 0%, #2F5233 50%);
    color: black; 
    padding-top: 10px;
    font-size: 14px;
    box-shadow: 0 -4px 10px rgba(0, 0, 0, 0.3); /* Lifted effect */
    z-index: 1000; 
    font-family: 'Inter', sans-serif;
}

/* New: Inner container to center the text content */
.footer-content-wrapper {
    max-width: 1200px; /* Optional: Sets max width for large screens */
    margin: 0 auto; /* KEY CHANGE: Centers the content wrapper */
    text-align: center; /* KEY CHANGE: Centers the text inside the wrapper */
    padding: 0 10px;
}

/* 2. Highlight for Project Name and Team */
.custom-footer strong {
    color: #ffd700; 
    font-weight: 700;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.custom-footer span {
    color: #E0F2F1; /* Light aqua/green for names */
}

/* 3. Responsive Text Size for smaller screens */
@media (max-width: 600px) {
    .custom-footer {
        font-size: 10px;
        padding: 8px 10px;
    }
}
</style>
""", unsafe_allow_html=True)

# --- Footer Content (Markdown) ---
footer_content = f"""
<div class="custom-footer">
    <div class="footer-content-wrapper">
        <p>
            Made with <strong>💖</strong> by Root coder Team: 
            <span>(Bhagwan Jha, Mayank Nagar, Aniket Patel, Aman Nagar, Lakshya, and Girija)</span>
        </p>
    </div>
</div>
"""

st.markdown(footer_content, unsafe_allow_html=True)