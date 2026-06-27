# core/transcriber.py

import whisper
import os

_model = None


def get_model(model_size: str = "base"):
    """Load Whisper model once and reuse."""
    global _model
    if _model is None:
        print(f"Loading Whisper {model_size} model...")
        _model = whisper.load_model(model_size)
        print("Whisper model loaded")
    return _model


def transcribe_audio(audio_path: str,
                     model_size: str = "base") -> dict:
    """Transcribe audio file to text with timestamps."""
    model = get_model(model_size)
    print(f"Transcribing: {audio_path}")
    result = model.transcribe(
        audio_path,
        language="en",
        task="transcribe",
        verbose=False,
        word_timestamps=True,
        fp16=False
    )
    print(f"Done: {len(result['segments'])} segments")
    return result


def get_segments_with_timestamps(transcription_result: dict) -> list:
    """Extract clean segments with timestamps."""
    segments = []
    for seg in transcription_result["segments"]:
        text = seg["text"].strip()
        if text:
            segments.append({
                "start": round(seg["start"], 2),
                "end": round(seg["end"], 2),
                "text": text
            })
    return segments


def get_full_text(transcription_result: dict) -> str:
    """Get complete transcript as single string."""
    return transcription_result["text"].strip()


def transcribe_long_audio(audio_path: str,
                           model_size: str = "base") -> dict:
    """Handle audio of any length."""
    from core.audio_processor import get_audio_duration

    duration = get_audio_duration(audio_path)
    print(f"Audio duration: {duration:.1f} seconds")

    if duration < 600:
        return transcribe_audio(audio_path, model_size)

    # Long audio — chunk approach
    from core.audio_processor import split_audio_chunks, cleanup_temp_files
    print("Long audio — splitting into chunks")
    chunks = split_audio_chunks(audio_path, chunk_minutes=5)

    all_segments = []
    full_text_parts = []
    time_offset = 0

    model = get_model(model_size)

    for i, chunk_path in enumerate(chunks):
        print(f"Transcribing chunk {i+1}/{len(chunks)}...")
        result = model.transcribe(chunk_path, language="en", fp16=False)

        for seg in result["segments"]:
            text = seg["text"].strip()
            if text:
                all_segments.append({
                    "start": round(seg["start"] + time_offset, 2),
                    "end": round(seg["end"] + time_offset, 2),
                    "text": text
                })

        full_text_parts.append(result["text"])

        from pydub import AudioSegment
        chunk_audio = AudioSegment.from_file(chunk_path)
        time_offset += len(chunk_audio) / 1000

    cleanup_temp_files()

    return {
        "text": " ".join(full_text_parts),
        "segments": all_segments,
        "language": "en"
    }