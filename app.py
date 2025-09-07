import streamlit as st
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
import time

#Secure Configuration and Initialization
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


#Core AI Functions

def transcribe_audio_with_gemini(audio_file_path: str) -> str | None:
    """Step 1: Sends the audio file to Gemini and returns only the transcript."""
    try:
        audio_file = genai.upload_file(path=audio_file_path)

        while audio_file.state.name == "PROCESSING":
            time.sleep(2)
            audio_file = genai.get_file(name=audio_file.name)

        if audio_file.state.name != "ACTIVE":
            st.error(f"File could not be processed. Final state: {audio_file.state.name}")
            return None

        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        response = model.generate_content(["Please transcribe this audio file.", audio_file],
                                          request_options={"timeout": 600})
        return response.text

    except Exception as e:
        st.error(f"An error occurred during transcription: {e}")
        return None


def get_summary_from_text(transcript: str) -> str | None:
    """Step 2: Sends the transcript text to Gemini and returns a JSON summary."""
    try:
        prompt = """
        You are an expert meeting assistant. Please analyze this transcript.
        Provide a concise summary in a single cohesive paragraph and extract all action items.

        Provide your response as a single, valid JSON object with two keys:
        "summary" and "action_items". The "summary" should be a string.
        """

        generation_config = {"response_mime_type": "application/json"}
        model = genai.GenerativeModel(
            model_name="models/gemini-1.5-flash",
            generation_config=generation_config
        )
        response = model.generate_content([prompt, transcript])
        return response.text

    except Exception as e:
        st.error(f"An error occurred during summarization: {e}")
        return None


#Streamlit UI
st.set_page_config(page_title="AI Audio Summarizer", layout="wide")
st.title("AI Audio Meeting Summarizer")
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
            with st.spinner("Transcribing audio..."):
                transcript = transcribe_audio_with_gemini(audio_file_path)

            if transcript:
                st.success("Transcription complete!")

                with st.spinner("Generating summary and action items..."):
                    summary_json = get_summary_from_text(transcript)

                if summary_json:
                    try:
                        results = json.loads(summary_json)
                        st.success("Analysis Complete!")
                        st.divider()

                        st.subheader("Meeting Summary")
                        summary_paragraph = results.get("summary", "No summary provided.")
                        st.write(summary_paragraph)

                        st.subheader("Action Items")
                        for item in results.get("action_items", []):
                            st.checkbox(f"**{item.get('owner', 'N/A')}:** {item.get('task', 'No task')}")

                        with st.expander("Show Full Transcript"):
                            st.text_area("Transcript:", transcript, height=250)

                    except json.JSONDecodeError:
                        st.error("The AI returned an invalid JSON format for the summary. Raw output below:")
                        st.text(summary_json)
    finally:
        if audio_file_path and os.path.exists(audio_file_path):
            os.remove(audio_file_path)