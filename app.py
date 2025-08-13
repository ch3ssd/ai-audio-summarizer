# Import all the necessary libraries
import streamlit as st
import os
import json
import whisper
from openai import OpenAI
from dotenv import load_dotenv
import time

# --- Section 1: Configuration and Model Initialization ---
# Load the environment variables from your .env file
load_dotenv()

# Get the configuration for Ollama from the .env file
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

# Best Practice: Use Streamlit's session state to avoid reloading models on every interaction.
# This makes the app much faster.
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False  # Set a flag

try:
    if not st.session_state.models_loaded:
        # Initialize the client to connect to your local Ollama server
        st.session_state.ollama_client = OpenAI(base_url=OLLAMA_BASE_URL, api_key='ollama')

        # Load the Whisper model for speech-to-text.
        # "base" is a good balance of speed and accuracy. It will be downloaded on the first run.
        st.session_state.whisper_model = whisper.load_model("base")

        # Set the flag to True once models are loaded
        st.session_state.models_loaded = True

except Exception as e:
    # If model loading fails, show an error and stop the app
    st.error(f"Failed to load models. Ensure Ollama is running and all prerequisites are installed. Error: {e}")
    st.stop()


# --- Section 2: Core AI Functions ---

def transcribe_audio(audio_file_path: str) -> str:
    """This function takes the path to an audio file and returns the transcribed text."""
    try:
        # Use the loaded Whisper model to transcribe the audio
        # fp16=False is recommended for CPU-based transcription for compatibility
        result = st.session_state.whisper_model.transcribe(audio_file_path, fp16=False)
        return result['text']
    except Exception as e:
        st.error(f"Error during audio transcription: {e}")
        return None


def get_summary_and_action_items(transcript: str) -> str:
    """This function sends the transcript to the local LLM to get a summary."""
    system_prompt = """
    You are an expert meeting assistant. Your task is to analyze a meeting transcript
    and provide a concise summary and a list of action items in a valid JSON format.
    Respond with ONLY the JSON object, nothing else.
    """
    try:
        # Call the Ollama server with the transcript
        response = st.session_state.ollama_client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript}
            ],
            temperature=0.0  # A low temperature makes the output more predictable
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred while contacting the Ollama model: {e}")
        return None


# --- Section 3: Streamlit User Interface ---

# Set the title and layout for your web app
st.set_page_config(page_title="Local AI Audio Summarizer", layout="wide")
st.title("🤖 Local AI Audio Meeting Summarizer")
st.markdown(
    "Upload an audio file of your meeting (`.mp3`, `.wav`, `.m4a`). Everything is processed locally on your machine.")

# Create the file uploader widget
uploaded_file = st.file_uploader("Choose an audio file", type=['mp3', 'wav', 'm4a', 'mp4'])

# This block of code runs only after a file has been uploaded
if uploaded_file is not None:

    # Securely save the uploaded file to the 'uploads' directory
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    unique_filename = f"{int(time.time())}_{uploaded_file.name}"
    audio_file_path = os.path.join("uploads", unique_filename)

    with open(audio_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File '{uploaded_file.name}' uploaded. Click the button to start analysis.")

    # Create the button to start the analysis
    if st.button("Analyze Meeting Audio", type="primary"):

        # Step 1: Transcribe the audio
        with st.spinner("Step 1/2: Transcribing audio with Whisper... This may take a moment. 🤫"):
            transcript_text = transcribe_audio(audio_file_path)

        # If transcription is successful, proceed
        if transcript_text:
            st.success("Transcription complete!")
            with st.expander("Show Full Transcript"):
                st.text_area("Transcript:", transcript_text, height=250)

            # Step 2: Summarize the transcript
            with st.spinner(f"Step 2/2: Summarizing with `{OLLAMA_MODEL}`... 🧠"):
                ai_response = get_summary_and_action_items(transcript_text)

            # If summarization is successful, display the results
            if ai_response:
                try:
                    # Clean the AI's response to make sure it's valid JSON
                    json_start = ai_response.find('{')
                    json_end = ai_response.rfind('}') + 1
                    clean_json_str = ai_response[json_start:json_end]
                    results = json.loads(clean_json_str)

                    # Display the summary and action items
                    st.divider()
                    st.subheader("📝 Meeting Summary")
                    for point in results.get("summary", []):
                        st.markdown(f"- {point}")

                    st.divider()
                    st.subheader("✅ Action Items")
                    for item in results.get("action_items", []):
                        st.checkbox(f"**{item.get('owner', 'N/A')}:** {item.get('task', 'No task')}")
                except (json.JSONDecodeError, IndexError):
                    st.error("The AI returned an invalid format. Raw output below:")
                    st.text(ai_response)
        else:
            st.error("Transcription failed. Cannot proceed to summarization.")

        # Best Practice: Clean up the temporary file after processing
        try:
            os.remove(audio_file_path)
        except OSError as e:
            st.warning(f"Could not remove temporary file: {e}")