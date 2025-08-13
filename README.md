# AI Audio Meeting Summarizer (Powered by Google Gemini)

This project is a desktop application that uses the Google Gemini API to transcribe and summarize audio from meetings. It is designed with privacy and security in mind.

## Features
- Analyzes audio files (`.mp3`, `.wav`, etc.) directly using the Gemini 1.5 Flash model.
- Generates a transcript, a concise summary, and a checklist of action items from a single API call.
- A simple, easy-to-use interface built with Streamlit.
- Securely handles API keys and temporary audio files.

## Setup and Installation

### Prerequisites
- Python 3.8+
- Git
- A Google AI API Key

### Installation Steps
1.  **Get an API Key**: Create a free API key at [Google AI Studio](https://makersuite.google.com/app/apikey).
2.  **Clone the repository**:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/ai-audio-summarizer.git](https://github.com/YOUR_USERNAME/ai-audio-summarizer.git)
    cd ai-audio-summarizer
    ```
3.  **Create and activate a virtual environment**:
    ```bash
    #Create virtual environment:
    python -m venv venv
    
    #Activate virtual environment:
    #For Windows
    .\venv\Scripts\activate
    
    # For macOS and Linux
    source venv/bin/activate
    ```
4.  **Install the required packages**:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Create your local environment file**:
    - Create a new file named `.env` in the project directory.
    - Add one line to it: `GOOGLE_API_KEY="YOUR_API_KEY_HERE"`

## How to Run
1.  Make sure your `(venv)` is active.
2.  Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```