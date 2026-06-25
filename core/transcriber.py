# core/transcriber.py

import whisper
import os

# Load model once globally
# Options: tiny, base, small, medium, large, large-v3
# Use "base" for development (fast)
# Use "large-v3" for final deployment (accurate)
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
    """
    Transcribe audio file to text with timestamps.
    Returns full result object with segments.
    """
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

    print(f"Transcription complete: {len(result['segments'])} segments")
    print(f"Detected language: {result['language']}")

    return result


def get_segments_with_timestamps(transcription_result: dict) -> list:
    """
    Extract clean segments with start/end times and text.
    """
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
    """
    Handle audio of any length.
    For files under 10 mins — direct transcription.
    For longer files — chunk and combine.
    """
    from core.audio_processor import (
        get_audio_duration,
        split_audio_chunks,
        cleanup_temp_files
    )

    duration = get_audio_duration(audio_path)
    print(f"Audio duration: {duration:.1f} seconds")

    # Under 10 minutes — transcribe directly
    if duration < 600:
        return transcribe_audio(audio_path, model_size)

    # Over 10 minutes — chunk approach
    print("Long audio detected — splitting into chunks")
    chunks = split_audio_chunks(audio_path, chunk_minutes=5)

    all_segments = []
    full_text_parts = []
    time_offset = 0

    model = get_model(model_size)

    for i, chunk_path in enumerate(chunks):
        print(f"Transcribing chunk {i+1}/{len(chunks)}...")
        result = model.transcribe(
            chunk_path,
            language="en",
            fp16=False
        )

        # Adjust timestamps
        for seg in result["segments"]:
            text = seg["text"].strip()
            if text:
                all_segments.append({
                    "start": round(seg["start"] + time_offset, 2),
                    "end": round(seg["end"] + time_offset, 2),
                    "text": text
                })

        full_text_parts.append(result["text"])

        # Calculate offset for next chunk
        from pydub import AudioSegment
        chunk_audio = AudioSegment.from_file(chunk_path)
        time_offset += len(chunk_audio) / 1000

    cleanup_temp_files()

    return {
        "text": " ".join(full_text_parts),
        "segments": all_segments,
        "language": "en"
    }


# Test directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = transcribe_audio(sys.argv[1])
        print("\nFull text:")
        print(result["text"])
        print(f"\nSegments: {len(result['segments'])}")
        for seg in result["segments"][:5]:
            print(f"[{seg['start']:.1f}s → {seg['end']:.1f}s] {seg['text']}")
    else:
        print("Usage: python core/transcriber.py audio.wav")