import streamlit as st
import requests
import os
from PIL import Image
import threading
import tempfile
import numpy as np
from scipy.io.wavfile import write
import google.generativeai as genai

st.markdown("""
<style>/* =============================================== */
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

/* =============================================== */
/* TEXT INPUT STYLING */
/* =============================================== */
.stTextInput > div > div > input {
    background: var(--bg-primary);
    border: 2px solid var(--border-light);
    border: none;
    padding: 1rem 1.5rem;
    font-size: 1rem;
    color: var(--text-primary);
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px var(--shadow-light);
}

.stTextInput > div > div > input:focus {
    outline: none;
    border-color: var(--primary-green);
    box-shadow: 0 0 0 3px rgba(79, 128, 45, 0.2);
    background: #fff8e1;
}

.stTextInput > div > div > input::placeholder {
    color: black;
    font-style: italic;
}

/* =============================================== */
/* FINAL TOUCHES - FIXING VISIBILITY */
/* =============================================== */

</style>
""", unsafe_allow_html=True)

# --- Configuration ---
try:
    # Get the API key from Streamlit's secrets
    api_key = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    # Fallback to environment variable for local development
    api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("Please set the Google API Key in st.secrets or as an environment variable.")
    st.stop()

# Configure the Gemini API
genai.configure(api_key=api_key)

# Using a stable, multimodal Gemini model
model = genai.GenerativeModel('gemini-2.5-flash')

# --- Multilingual Text (Your original structure remains) ---
LANGUAGES = {
    # ... (Your LANGUAGES dictionary remains the same) ...
    "English": {
        "title": "Root Coder AI - Farmer's Assistant for India",
        "welcome_message": "Hello! I am Root Coder AI, your expert agricultural assistant for India Farmers. How can I help you with your farming today? You can ask a question or upload an image.",
        "uploader_label": "Upload an image of your crop, pest, or soil",
        "input_placeholder": "Ask your question here...",
        "language_select": "Choose Language",
        "error_text": "Sorry, an error occurred with the AI model. Please try again.",
        "spinner_text": "Thinking..."
    },
    "മലയാളം (Malayalam)": {
        "title": "റൂട്ട് കോഡർ AI - ഇന്ത്യയിലെ കർഷക സഹായി 🇮🇳",
        "welcome_message": "നമസ്കാരം! ഞാൻ റൂട്ട് കോഡർ AI ആണ്, ഇന്ത്യയിലെ നിങ്ങളുടെ കാർഷിക വിദഗ്ധ സഹായി. SIH 2025-ന് വേണ്ടി റൂട്ട് കോഡർ ടീം (ഭഗവാൻ ഝാ, മായൻ നഗർ, അനികേത് പട്ടേൽ, അമൻ നഗർ, ലക്ഷ്യ, ഗിരിജ) വികസിപ്പിച്ചെടുത്ത ഒരു പ്രോജക്റ്റാണിത്. ഇന്ന് നിങ്ങളുടെ കൃഷിയിൽ ഞാൻ എങ്ങനെ സഹായിക്കണം? നിങ്ങൾക്ക് ഒരു ചോദ്യം ചോദിക്കാം അല്ലെങ്കിൽ ഒരു ചിത്രം അപ്‌ലോഡ് ചെയ്യാം.",
        "uploader_label": "നിങ്ങളുടെ വിള, കീടം, അല്ലെങ്കിൽ മണ്ണിന്റെ ഒരു ചിത്രം അപ്‌ലോഡ് ചെയ്യുക",
        "input_placeholder": "നിങ്ങളുടെ ചോദ്യം ഇവിടെ ചോദിക്കൂ...",
        "language_select": "ഭാഷ തിരഞ്ഞെടുക്കുക",
        "error_text": "ക്ഷമിക്കണം, ഒരു പിശക് സംഭവിച്ചു. ദയവായി വീണ്ടും ശ്രമിക്കുക.",
        "spinner_text": "ചിന്തിക്കുന്നു..."
    },
    "हिन्दी (Hindi)": {
        "title": "रूट कोडर AI - भारत किसान सहायक 🇮🇳",
        "welcome_message": "नमस्ते! मैं रूट कोडर AI हूँ, पूरे भारत में आपके कृषि विशेषज्ञ सहायक। यह SIH 2025 के लिए रूट कोडर टीम (भगवन झा, मयंक नागर, अनिकेत पटेल, अमन नागर, लक्ष्या, और गिरिजा) द्वारा विकसित एक प्रोजेक्ट है। आज मैं आपकी खेती में कैसे मदद कर सकता हूँ? आप मुझसे कोई सवाल पूछ सकते हैं या किसी पौधे की तस्वीर अपलोड कर सकते हैं।",
        "uploader_label": "अपनी फसल, कीट, या मिट्टी की एक तस्वीर अपलोड करें",
        "input_placeholder": "अपना सवाल यहाँ पूछें...",
        "language_select": "भाषा चुनें",
        "error_text": "क्षमा करें, एक त्रुटि हुई। कृपया पुन: प्रयास करें।",
        "spinner_text": "सोच रहा हूँ..."
    },
    "ಕನ್ನಡ (Kannada)": {
        "title": "ರೂಟ್ ಕೋಡರ್ AI - ಭಾರತ ರೈತ ಸಹಾಯಕ 🇮🇳",
        "welcome_message": "ನಮಸ್ಕಾರ! ನಾನು ರೂಟ್ ಕೋಡರ್ AI, ಭಾರತದಾದ್ಯಂತ ನಿಮ್ಮ ಕೃಷಿ ತಜ್ಞ ಸಹಾಯಕ. ಇದು SIH 2025 ಗಾಗಿ ರೂಟ್ ಕೋಡರ್ ತಂಡದಿಂದ (ಭಗವಾನ್ ಝಾ, ಮಾಯನ್ ನಗರ್, ಅನಿಕೇತ್ ಪಟೇಲ್, ಅಮನ್ ನಗರ್, ಲಕ್ಷ್ಯ, ಮತ್ತು ಗಿರಿಜ) ಅಭಿವೃದ್ಧಿಪಡಿಸಿದ ಯೋಜನೆ. ಇಂದು ನಿಮ್ಮ ಕೃಷಿಯಲ್ಲಿ ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ? ನೀವು ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಬಹುದು ಅಥವಾ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಬಹುದು.",
        "uploader_label": "ನಿಮ್ಮ ಬೆಳೆ, ಕೀಟ, ಅಥವಾ ಮಣ್ಣಿನ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "input_placeholder": "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಇಲ್ಲಿ ಕೇಳಿ...",
        "language_select": "ಭಾಷೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ",
        "error_text": "ಕ್ಷಮಿಸಿ, ದೋಷ ಸಂಭವಿಸಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
        "spinner_text": "ಆಲೋಚಿಸಲಾಗುತ್ತಿದೆ..."
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

    prompt_parts = [system_prompt, "\n\n", input_text]

    if image:
        prompt_parts.append(image)

    try:
        response = model.generate_content(prompt_parts)

        # Ensures clean name usage
        response_text = response.text.strip().replace("Krishi Mitra AI", "Root Coder AI")

        return response_text

    except Exception as e:
        # Simplified error handling for robustness
        # Fallback language error text is used
        error_lang = "English" if selected_language not in LANGUAGES else selected_language
        st.error(f"An API error occurred: {e}")
        return LANGUAGES[error_lang]["error_text"]


# --- Streamlit App ---

# --- Language Selection in Sidebar ---
# st.sidebar commands are now guaranteed to work after CSS fix
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


# Initial Message Setup
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": ui_texts["welcome_message"]}
    ]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "image" in message:
            st.image(message["image"], width=250)

# --- Voice Input and Image Upload Logic ---
if "recording" not in st.session_state:
    st.session_state.recording = False
if "audio_file" not in st.session_state:
    st.session_state.audio_file = None
if "recording_data" not in st.session_state:
    st.session_state.recording_data = []
if "show_image_uploader" not in st.session_state:
    st.session_state.show_image_uploader = False


def record_audio_thread():
    fs = 44100
    st.session_state.recording_data = []
    try:
        while st.session_state.recording:
            # NOTE: Requires numpy and sounddevice
            data = sd.rec(4410, samplerate=fs, channels=1)
            sd.wait()
            st.session_state.recording_data.append(data)
    except Exception as e:
        st.error(f"Audio recording error: {e}")
        st.session_state.recording = False


def toggle_recording():
    st.session_state.recording = not st.session_state.recording
    if st.session_state.recording:
        threading.Thread(target=record_audio_thread, daemon=True).start()
    else:
        if st.session_state.recording_data:
            fs = 44100
            # NOTE: np.concatenate requires numpy
            audio = np.concatenate(st.session_state.recording_data, axis=0)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            # NOTE: write requires scipy.io.wavfile
            write(temp_file.name, fs, audio)
            st.session_state.audio_file = temp_file.name
            st.rerun()


def toggle_image_uploader():
    st.session_state.show_image_uploader = not st.session_state.show_image_uploader
    # Hide audio message if we toggle image
    if st.session_state.show_image_uploader:
        st.session_state.recording = False
        st.session_state.audio_file = None
    st.rerun()


# --- Input Area: Icons and Chat Input ---

with st.form(key='chat_form', clear_on_submit=True):
    cols = st.columns([1, 1, 10])  # Small columns for icons, larger for chat input

    with cols[0]:
        # Image Upload Icon Button
        image_btn = st.form_submit_button("📤", help=ui_texts["uploader_label"])
        if image_btn:
            # Use toggle function to control visibility
            toggle_image_uploader()

    with cols[1]:
        # Voice Input Icon Button
        voice_btn = st.form_submit_button(
            "🎙️" if not st.session_state.recording else "⏹️",
            help="Start/Stop Voice Recording"
        )
        if voice_btn:
            toggle_recording()

    with cols[2]:
        # Chat input box (using a hidden text input inside the form)
        prompt_input = st.text_input(
            "",
            placeholder=ui_texts["input_placeholder"],
            label_visibility="collapsed",
            key="prompt_text_input"  # Key to grab the value
        )
        # The actual form submission button (hidden, triggered by Enter)
        submitted = st.form_submit_button("Submit", type="primary", use_container_width=True)
        # NOTE: A visual Send Icon button would be better here for the new UI style.

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
    st.info("Recording in progress... Click the stop button (⏹️) above to save.")
elif st.session_state.audio_file:
    # Display audio and then clear the file path so it doesn't replay on every rerun
    st.audio(st.session_state.audio_file)
    # NOTE: You would typically process this audio file to text here using a Speech-to-Text API.
    st.success("Audio recorded and saved successfully! If you asked a question, please type it below.")

# --- Process Chat Input ---
if submitted and prompt_input:
    # Get the image if the uploader is visible and a file was uploaded
    image_to_process = uploaded_image if uploaded_image else None
    prompt = prompt_input

    # Add user message
    user_message = {"role": "user", "content": prompt}
    if image_to_process:
        user_message["image"] = image_to_process
    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.write(prompt)
        if image_to_process:
            st.image(image_to_process, width=250)

    # Assistant reply
    with st.chat_message("assistant"):
        with st.spinner(ui_texts["spinner_text"]):
            lang_code = (
                "English" if selected_language == "English"
                else "Malayalam" if selected_language == "മലയാളം (Malayalam)"
                else "Hindi" if selected_language == "हिन्दी (Hindi)"
                else "Kannada"  # New language code
            )
            response_text = get_gemini_response(prompt, image_to_process, lang_code)
            st.write(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})

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
footer_content = """
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