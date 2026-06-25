# api/main.py

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uvicorn
from core.pipeline import process_meeting
from email_service.sender import send_meeting_summary

app = FastAPI(
    title="Meeting Intelligence System",
    description="AI-powered meeting transcription and summarization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

UPLOAD_DIR = "temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
async def root():
    return {
        "message": "Meeting Intelligence System running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "transcription": "Whisper",
        "diarization": "Pyannote",
        "extraction": "Groq LLaMA3"
    }


@app.post("/process")
async def process_meeting_endpoint(
    audio_file: UploadFile = File(...),
    meeting_title: str = Form(default="Meeting"),
    min_speakers: int = Form(default=1),
    max_speakers: int = Form(default=8),
    send_email: bool = Form(default=False),
    recipient_email: str = Form(default="")
):
    """
    Process a meeting audio file and return insights.
    """

    # Validate file type
    allowed_types = [
        "audio/mpeg", "audio/mp4", "audio/wav",
        "audio/m4a", "audio/flac", "video/mp4"
    ]

    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, audio_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)

    print(f"Uploaded: {audio_file.filename} ({audio_file.size} bytes)")

    # Process
    result = process_meeting(
        audio_file_path=file_path,
        meeting_title=meeting_title,
        min_speakers=min_speakers,
        max_speakers=max_speakers,
        whisper_model="base"
    )

    # Clean up uploaded file
    if os.path.exists(file_path):
        os.remove(file_path)

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Processing failed")
        )

    # Send email if requested
    if send_email and recipient_email:
        email_result = send_meeting_summary(
            recipient_email=recipient_email,
            meeting_title=meeting_title,
            insights=result["insights"]
        )
        result["email_sent"] = email_result

    return result


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )