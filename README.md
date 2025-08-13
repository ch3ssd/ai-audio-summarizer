# AI Audio Meeting Summarizer

This project is a desktop application that uses local AI models to transcribe and summarize audio from meetings. It is designed with privacy as a priority, ensuring no data ever leaves the user's machine.

## Current Status
**Work in Progress:** The project scaffold is complete. This includes the directory structure, dependency management (`requirements.txt`), environment configuration (`.env`), and a functional user interface built with Streamlit that uses placeholder logic.

The core AI functionality (live transcription and summarization) is pending the resolution of a local network issue with the Ollama service.

## Planned Features
- Transcribe audio files (`.mp3`, `.wav`, etc.) using a local instance of OpenAI's Whisper.
- Generate a concise summary of the transcript using a local LLM hosted by Ollama.
- Extract a checklist of action items and their assigned owners.
- A simple, easy-to-use interface built with Streamlit.

## Setup and Installation

### Prerequisites
- Python 3.8+
- Git
- [Ollama](https://ollama.com/)
- [FFmpeg](https://ffmpeg.org/download.html)

### Installation Steps
1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/ai-audio-summarizer.git](https://github.com/YOUR_USERNAME/ai-audio-summarizer.git)
    cd ai-audio-summarizer
    ```
2.  Create and activate a virtual environment:
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set up your local environment file by creating a `.env` file and adding the necessary configuration (see `.env.example` if it exists).

## How to Run
1.  Ensure the Ollama service is running.
2.  Run the Streamlit application from your project's virtual environment:
    ```bash
    streamlit run app.py
    ```
    *Note: Currently, this will launch the UI with placeholder functions.*