# core/transcriber.py

from faster_whisper import WhisperModel

# Load model once globally
_model = None


def get_model(model_size: str = "base"):
    """Load Whisper model once and reuse."""
    global _model
    if _model is None:
        print(f"Loading Whisper {model_size} model...")
        _model = WhisperModel(model_size, device="cpu", compute_type="int8")
        print("Whisper model loaded")
    return _model


def transcribe_audio(audio_path: str,
                     model_size: str = "base") -> dict:
    """
    Transcribe audio file to text with timestamps.
    Returns dict with segments and text.
    """
    model = get_model(model_size)
    print(f"Transcribing: {audio_path}")

    segments, info = model.transcribe(
        audio_path,
        language="en",
        beam_size=5,
        word_timestamps=True
    )

    segments_list = list(segments)

    print(f"Transcription complete: {len(segments_list)} segments")
    print(f"Detected language: {info.language}")

    return {
        "segments": [
            {
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": seg.text.strip()
            }
            for seg in segments_list if seg.text.strip()
        ],
        "text": " ".join(seg.text.strip() for seg in segments_list if seg.text.strip()),
        "language": info.language
    }


def get_segments_with_timestamps(transcription_result: dict) -> list:
    """Extract clean segments with start/end times and text."""
    return transcription_result["segments"]


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

    if duration < 600:
        return transcribe_audio(audio_path, model_size)

    print("Long audio detected — splitting into chunks")
    chunks = split_audio_chunks(audio_path, chunk_minutes=5)

    all_segments = []
    full_text_parts = []
    time_offset = 0

    model = get_model(model_size)

    for i, chunk_path in enumerate(chunks):
        print(f"Transcribing chunk {i+1}/{len(chunks)}...")
        segments, _ = model.transcribe(chunk_path, language="en", beam_size=5)

        for seg in segments:
            text = seg.text.strip()
            if text:
                all_segments.append({
                    "start": round(seg.start + time_offset, 2),
                    "end": round(seg.end + time_offset, 2),
                    "text": text
                })
                full_text_parts.append(text)

        chunk_duration = get_audio_duration(chunk_path)
        time_offset += chunk_duration

    # Clean up only the chunk files created, leaving the main processed.wav intact for diarization
    for chunk_path in chunks:
        try:
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
        except Exception as e:
            print(f"Could not delete chunk {chunk_path}: {e}")

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