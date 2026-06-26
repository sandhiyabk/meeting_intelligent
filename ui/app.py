# ui/app.py — Streamlit Cloud version

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import tempfile

# Import pipeline directly — no FastAPI needed for cloud
from core.pipeline import process_meeting
from email_service.sender import send_meeting_summary

st.set_page_config(
    page_title="Meeting Intelligence",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Meeting Intelligence System")
st.caption(
    "Upload any meeting audio → Transcript + "
    "Decisions + Action Items + Email Summary"
)

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 Upload Meeting Audio")

    uploaded_file = st.file_uploader(
        "Choose audio/video file",
        type=["mp3", "mp4", "wav", "m4a", "flac"],
        help="Supports MP3 MP4 WAV M4A FLAC up to 100MB"
    )

    meeting_title = st.text_input(
        "Meeting Title",
        value="Team Meeting"
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

    send_email = st.checkbox("Send email summary")
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
        tmp_path = None
        with st.spinner("Processing — this takes 2-5 minutes..."):
            try:
                # Save uploaded file to temp location
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=f".{uploaded_file.name.split('.')[-1]}"
                ) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                # Call pipeline directly
                result = process_meeting(
                    audio_file_path=tmp_path,
                    meeting_title=meeting_title,
                    min_speakers=min_speakers,
                    max_speakers=max_speakers,
                    whisper_model="base"
                )

                if result["success"]:
                    st.session_state.result = result
                    st.success("✅ Processing complete!")
                else:
                    st.error(f"Error: {result.get('error')}")

            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    if "result" in st.session_state:
        result = st.session_state.result
        insights = result.get("insights", {})

        score_col1, score_col2, score_col3 = st.columns(3)
        score_col1.metric(
            "Decisions",
            len(insights.get("decisions", []))
        )
        score_col2.metric(
            "Action Items",
            len(insights.get("action_items", []))
        )
        score_col3.metric(
            "Open Questions",
            len(insights.get("open_questions", []))
        )

        st.markdown("### 📝 Summary")
        st.info(insights.get("summary", "No summary"))

        decisions = insights.get("decisions", [])
        if decisions:
            st.markdown("### ✅ Key Decisions")
            for d in decisions:
                st.success(f"→ {d}")

        action_items = insights.get("action_items", [])
        if action_items:
            st.markdown("### 📋 Action Items")
            for item in action_items:
                st.warning(
                    f"**{item.get('task')}** | "
                    f"Owner: {item.get('owner')} | "
                    f"By: {item.get('deadline')}"
                )

        questions = insights.get("open_questions", [])
        if questions:
            st.markdown("### ❓ Open Questions")
            for q in questions:
                st.error(f"→ {q}")

        with st.expander("📜 Full Transcript"):
            for segment in result.get("transcript", []):
                st.markdown(
                    f"**[{segment.get('speaker')}]** "
                    f"`{segment.get('timestamp')}` — "
                    f"{segment.get('text')}"
                )

        if send_email and recipient_email:
            email_result = send_meeting_summary(
                recipient_email=recipient_email,
                meeting_title=meeting_title,
                insights=insights
            )
            if email_result["success"]:
                st.success(f"📧 Email sent to {recipient_email}")
            else:
                st.error(f"Email failed: {email_result['error']}")

    else:
        st.info("👈 Upload audio and click Process Meeting")
        st.markdown("""
        **Powered by:**
        - 🎙️ OpenAI Whisper — transcription
        - 👥 Pyannote — speaker identification
        - 🧠 Groq LLaMA 3.3 — intelligence
        - 📧 Gmail SMTP — email summary
        """)

st.divider()
st.caption(
    "Built by Sandhiya BK | "
    "Kamaraj College of Engineering | "
    "2027 Batch | AI Engineer Journey"
)