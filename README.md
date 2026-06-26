# 🎙️ Meeting Intelligence System

An AI-powered meeting transcription, speaker diarization (identification), and insight extraction application. Upload any meeting recording (audio or video), and the system will automatically transcribe the discussion, label which speaker spoke when, extract key decisions, action items, and open questions, and optionally email a structured summary directly to your team.

---

## 🚀 Key Features

*   **Audio/Video Transcription**: Powered by **OpenAI Whisper** (via `faster-whisper`), supporting multiple formats (`mp3`, `mp4`, `wav`, `m4a`, `flac`) up to 100MB.
*   **Speaker Diarization**: Integrated with **Pyannote Audio 3.1** to identify who spoke when, and group consecutive speaking turns naturally.
*   **Smart Insight Extraction**: Utilizes **Groq LLaMA 3.3 (70B)** to extract:
    *   A concise meeting summary (3 sentences max).
    *   Key decisions made.
    *   Action items with designated owners and deadlines.
    *   Open, unresolved questions.
*   **Automated Email Summaries**: Sends formatted summaries to designated recipients using secure **Gmail SMTP**.
*   **Modern Interactive UI**: A clean, responsive dashboard built with **Streamlit** including metrics, expanders, and visual indicators.

---

## 🛠️ Tech Stack & Architecture

*   **Frontend**: Streamlit
*   **Audio Processing**: FFmpeg, soundfile, scipy
*   **Transcription**: Faster-Whisper (runs locally on CPU/GPU)
*   **Diarization**: Pyannote Audio (Hugging Face)
*   **LLM Inference**: Groq Cloud API (`llama-3.3-70b-versatile`)
*   **Notifications**: SMTP (Gmail App Passwords)

---

## 📦 File Structure

```text
├── .streamlit/
│   ├── config.toml       # Streamlit server configuration
│   └── secrets.toml      # Local secrets (ignored by git)
├── api/
│   └── main.py           # Optional FastAPI backend wrapper
├── core/
│   ├── audio_processor.py # Audio validation and FFmpeg conversion
│   ├── config.py         # Credentials and environment loader
│   ├── diarizer.py        # Pyannote speaker diarization
│   ├── extractor.py       # Groq LLM insight extraction
│   ├── pipeline.py       # End-to-end processing pipeline
│   ├── transcriber.py     # Whisper transcription & audio chunking
│   └── transcript_builder.py # Merging transcripts & speaker labels
├── email_service/
│   └── sender.py         # SMTP email formatting and delivery
├── tests/
│   └── test_pipeline.py  # Mock test suite for pipeline logic
├── packages.txt          # Linux system-level dependencies for Streamlit Cloud
└── requirements.txt      # Python package dependencies
```

---

## ⚙️ Prerequisites for Speaker Diarization

Because Pyannote Audio models are gated on Hugging Face, you must complete these steps before running the diarization pipeline:

1.  **Hugging Face Account**: Sign up or log in at [Hugging Face](https://huggingface.co/).
2.  **Accept Model License Agreements**:
    *   Visit [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) and accept the conditions.
    *   Visit [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0) and accept the conditions.
3.  **Hugging Face Access Token**: Go to your [Hugging Face Settings -> Access Tokens](https://huggingface.co/settings/tokens) and create a **Read** token.

---

## 💻 Local Setup & Running

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd meeting_intelligent
    ```

2.  **Set up Virtual Environment**:
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install FFmpeg**:
    Ensure `ffmpeg` and `ffprobe` are installed on your system and added to your system's `PATH`.
    *   *Windows*: Install via Chocolatey (`choco install ffmpeg`) or download official builds.
    *   *macOS*: Install via Homebrew (`brew install ffmpeg`).
    *   *Linux*: Install via apt (`sudo apt install ffmpeg`).

5.  **Configure Credentials**:
    Create a `.env` file or modify `.streamlit/secrets.toml`:
    ```toml
    GROQ_API_KEY = "your_groq_api_key"
    HF_TOKEN = "your_huggingface_read_token"
    EMAIL_ADDRESS = "your_gmail_address@gmail.com"
    EMAIL_APP_PASSWORD = "your_16_digit_gmail_app_password"
    ```

6.  **Run the Streamlit Application**:
    ```bash
    streamlit run ui/app.py
    ```

7.  **Run the Tests**:
    ```bash
    python tests/test_pipeline.py
    ```

---

## ☁️ Streamlit Cloud Deployment Guide

This project is fully structured and aligned for seamless deployment on **Streamlit Community Cloud**.

### Step 1: Push to GitHub
Ensure all code is committed and pushed to a public or private GitHub repository. (Note: `.env` and `.streamlit/secrets.toml` are ignored by Git to prevent exposing your private keys).

### Step 2: Deploy on Streamlit Cloud
1.  Go to [Streamlit Share](https://share.streamlit.io/) and log in.
2.  Click **New app**.
3.  Select your Repository, Branch, and set the **Main file path** to:
    `ui/app.py`
4.  Click **Advanced settings...** before deploying.

### Step 3: Configure Secrets in Streamlit
In the **Secrets** text area, paste your environment configuration from `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_..."
HF_TOKEN = "hf_..."
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_APP_PASSWORD = "your_app_password"
```
Click **Save**.

### Step 4: Click Deploy!
Streamlit Cloud will automatically:
1.  Detect `packages.txt` and install `ffmpeg` and `libsndfile1` using apt.
2.  Detect `requirements.txt` and install all Python packages (including PyTorch and Pyannote Audio).
3.  Start the application, utilizing the secret tokens you added in step 3.

---

## 🔒 Security & Best Practices

*   **No Hardcoded Secrets**: All private API keys and passwords are loaded dynamically via `core/config.py` which checks environment variables, Streamlit secrets (`st.secrets`), and `.env` files.
*   **Git Security**: Both `.env` and `.streamlit/secrets.toml` are explicitly listed in `.gitignore` to prevent leaking credentials.
*   **Temp File Cleanup**: The audio processing pipeline automatically cleans up all converted WAV chunks and temporary audio uploads after processing to optimize disk space and protect privacy.
