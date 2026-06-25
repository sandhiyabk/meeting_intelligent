# ui/app.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Meeting Intelligence",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Meeting Intelligence System")
st.caption(
    "Upload any meeting audio → Get transcript, "
    "decisions, action items, and summary"
)

# API health check
try:
    health = requests.get("http://localhost:8001/health", timeout=2)
    if health.status_code == 200:
        st.success("✅ API Connected", icon="✅")
    else:
        st.error("❌ API Error")
except:
    st.warning("⚠️ API not running — start FastAPI first")
    st.code("uvicorn api.main:app --port 8001 --reload", language="bash")

st.divider()

# Upload section
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 Upload Meeting Audio")

    uploaded_file = st.file_uploader(
        "Choose audio/video file",
        type=["mp3", "mp4", "wav", "m4a", "flac"],
        help="Supports MP3, MP4, WAV, M4A, FLAC up to 100MB"
    )

    meeting_title = st.text_input(
        "Meeting Title",
        value="Team Meeting",
        placeholder="e.g. Q3 Budget Review"
    )

    col_sp1, col_sp2 = st.columns(2)
    with col_sp1:
        min_speakers = st.number_input(
            "Min Speakers", min_value=1, max_value=10, value=1
        )
    with col_sp2:
        max_speakers = st.number_input(
            "Max Speakers", min_value=1, max_value=15, value=8
        )

    st.divider()
    st.subheader("📧 Email Summary (Optional)")

    send_email = st.checkbox("Send email summary after processing")
    recipient_email = ""
    if send_email:
        recipient_email = st.text_input(
            "Recipient Email",
            placeholder="team@company.com"
        )

    process_btn = st.button(
        "🚀 Process Meeting",
        type="primary",
        use_container_width=True,
        disabled=uploaded_file is None
    )

with col2:
    st.subheader("📊 Meeting Insights")

    if process_btn and uploaded_file:
        with st.spinner("Processing... This may take 2-5 minutes"):
            try:
                files = {
                    "audio_file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "audio/mpeg"
                    )
                }
                data = {
                    "meeting_title": meeting_title,
                    "min_speakers": min_speakers,
                    "max_speakers": max_speakers,
                    "send_email": send_email,
                    "recipient_email": recipient_email
                }

                response = requests.post(
                    "http://localhost:8001/process",
                    files=files,
                    data=data,
                    timeout=600
                )

                if response.status_code == 200:
                    result = response.json()
                    st.session_state.result = result
                    st.success("✅ Processing complete!")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown')}")

            except requests.exceptions.Timeout:
                st.error("Request timed out — audio may be too long")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if "result" in st.session_state:
        result = st.session_state.result
        insights = result.get("insights", {})

        # Summary
        st.markdown("### 📝 Summary")
        st.info(insights.get("summary", "No summary"))

        # Stats row
        c1, c2, c3 = st.columns(3)
        c1.metric("Decisions", len(insights.get("decisions", [])))
        c2.metric("Action Items", len(insights.get("action_items", [])))
        c3.metric("Open Questions", len(insights.get("open_questions", [])))

        st.divider()

        # Decisions
        decisions = insights.get("decisions", [])
        if decisions:
            st.markdown("### ✅ Key Decisions")
            for d in decisions:
                st.success(f"→ {d}")

        # Action Items
        action_items = insights.get("action_items", [])
        if action_items:
            st.markdown("### 📋 Action Items")
            for item in action_items:
                task = item.get("task", "")
                owner = item.get("owner", "UNKNOWN")
                deadline = item.get("deadline", "UNKNOWN")
                st.warning(
                    f"**{task}**\n\n"
                    f"Owner: {owner} | Deadline: {deadline}"
                )

        # Open Questions
        questions = insights.get("open_questions", [])
        if questions:
            st.markdown("### ❓ Open Questions")
            for q in questions:
                st.error(f"→ {q}")

        # Full Transcript
        with st.expander("📜 Full Transcript"):
            transcript = result.get("transcript", [])
            for segment in transcript:
                speaker = segment.get("speaker", "")
                timestamp = segment.get("timestamp", "")
                text = segment.get("text", "")
                st.markdown(
                    f"**[{speaker}]** `{timestamp}` — {text}"
                )

        # Email status
        if "email_sent" in result:
            if result["email_sent"]["success"]:
                st.success(
                    f"📧 Email sent to {result['email_sent']['recipient']}"
                )
            else:
                st.error(
                    f"Email failed: {result['email_sent']['error']}"
                )

    else:
        st.info("👈 Upload audio and click Process Meeting")
        st.markdown("""
        **What this system does:**
        - 🎙️ Transcribes any meeting audio (Whisper)
        - 👥 Identifies who said what (Pyannote)
        - 🧠 Extracts decisions and action items (LLaMA 3)
        - 📧 Sends formatted summary email (optional)

        **Powered by:**
        - OpenAI Whisper (transcription)
        - Pyannote (speaker diarization)
        - Groq LLaMA 3.3-70B (intelligence)
        """)

st.divider()
st.caption(
    "Built by Sandhiya BK | Kamaraj College of Engineering | "
    "Part of AI Engineer journey | 2027 Batch"
)