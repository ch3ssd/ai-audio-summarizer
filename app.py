import streamlit as st
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
import time

# --- Section 1: Secure Configuration and Initialization ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Google AI API key not found. Please create a .env file and add your key.")
    st.stop()

if 'api_configured' not in st.session_state:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        st.session_state.api_configured = True
    except Exception as e:
        st.error(f"Failed to configure Google AI: {e}")
        st.stop()


# --- Section 2: Core AI Function with Error Handling ---
def analyze_audio_with_gemini(audio_file_path: str):
    try:
        audio_file = genai.upload_file(path=audio_file_path)

        prompt = """
        You are an expert meeting assistant. Please analyze this audio file.
        Perform the following tasks:
        1. Transcribe the entire audio accurately.
        2. Provide a concise, bulleted summary of the key decisions and topics.
        3. Extract all specific action items, including who is assigned to them.

        Provide your response as a single, valid JSON object with three keys:
        "transcript", "summary", and "action_items".
        """

        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

        response = model.generate_content([audio_file, prompt])
        return response.text

    except Exception as e:
        st.error(f"An error occurred while contacting the Gemini API: {e}")
        return None


# --- Section 3: Streamlit UI with Secure File Management ---
st.set_page_config(page_title="AI Audio Summarizer", layout="wide")
st.title("AI Audio Meeting Summarizer (Powered by Google Gemini)")
st.markdown("Upload an audio file. Your data is processed securely and deleted after analysis.")

uploaded_file = st.file_uploader("Choose an audio file", type=['mp3', 'wav', 'm4a', 'mp4'])

if uploaded_file is not None:
    audio_file_path = None
    try:
        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        unique_filename = f"{int(time.time())}_{uploaded_file.name}"
        audio_file_path = os.path.join("uploads", unique_filename)

        with open(audio_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"File '{uploaded_file.name}' uploaded. Click the button to start analysis.")

        if st.button("Analyze Meeting Audio", type="primary"):
            with st.spinner("The AI is analyzing the audio... This may take a few moments. 🧠"):
                ai_response = analyze_audio_with_gemini(audio_file_path)

            if ai_response:
                try:
                    json_start = ai_response.find('{')
                    json_end = ai_response.rfind('}') + 1
                    clean_json_str = ai_response[json_start:json_end]
                    results = json.loads(clean_json_str)

                    st.success("Analysis Complete!")
                    st.divider()

                    st.subheader("📝 Meeting Summary")
                    for point in results.get("summary", []):
                        st.markdown(f"- {point}")

                    st.subheader("✅ Action Items")
                    for item in results.get("action_items", []):
                        st.checkbox(f"**{item.get('owner', 'N/A')}:** {item.get('task', 'No task')}")

                    with st.expander("Show Full Transcript"):
                        st.text_area("Transcript:", results.get("transcript", ""), height=250)

                except (json.JSONDecodeError, IndexError, AttributeError):
                    st.error("The AI returned an invalid format. Raw output below:")
                    st.text(ai_response)
    finally:
        # Security Best Practice: Always delete the temporary file after processing.
        if audio_file_path and os.path.exists(audio_file_path):
            os.remove(audio_file_path)