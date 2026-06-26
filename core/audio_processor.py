# core/audio_processor.py

import os
from pathlib import Path
import soundfile as sf
import scipy.signal as signal
import numpy as np

ALLOWED_FORMATS = ['.mp3', '.mp4', '.wav', '.m4a', '.flac', '.ogg']
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
TEMP_DIR = "temp"


def validate_audio_file(file_path: str) -> dict:
    """
    Validate uploaded audio file format and size.
    """
    path = Path(file_path)

    if not path.exists():
        return {"valid": False, "error": "File not found"}

    if path.suffix.lower() not in ALLOWED_FORMATS:
        return {
            "valid": False,
            "error": f"Format {path.suffix} not supported. Use: {ALLOWED_FORMATS}"
        }

    size = os.path.getsize(file_path)
    if size > MAX_FILE_SIZE:
        return {
            "valid": False,
            "error": f"File too large: {size/1024/1024:.1f}MB. Max 100MB"
        }

    return {
        "valid": True,
        "format": path.suffix.lower(),
        "size_mb": round(size / 1024 / 1024, 2)
    }


def process_audio(file_path: str) -> str:
    """
    Convert any audio to 16kHz mono WAV.
    Uses soundfile instead of pydub.
    """
    import subprocess
    os.makedirs(TEMP_DIR, exist_ok=True)
    output_path = os.path.join(TEMP_DIR, "processed.wav")

    # Use ffmpeg directly
    subprocess.run([
        "ffmpeg", "-i", file_path,
        "-ar", "16000",
        "-ac", "1",
        "-y", output_path
    ], capture_output=True)

    return output_path
def get_audio_duration(file_path: str) -> float:
    """Returns duration in seconds."""
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000


def split_audio_chunks(file_path: str,
                        chunk_minutes: int = 5) -> list:
    """
    Split long audio into chunks for processing.
    Returns list of chunk file paths.
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    audio = AudioSegment.from_file(file_path)
    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]
        chunk_path = os.path.join(TEMP_DIR, f"chunk_{i:03d}.wav")
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
        print(f"Created chunk {i+1}: {len(chunk)/1000:.1f}s")

    return chunks


def cleanup_temp_files():
    """Remove all temporary audio files."""
    if os.path.exists(TEMP_DIR):
        for file in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, file)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Could not delete {file}: {e}")
        print("Temp files cleaned up")


# Test directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file = sys.argv[1]
        validation = validate_audio_file(file)
        print("Validation:", validation)
        if validation["valid"]:
            processed = process_audio(file)
            duration = get_audio_duration(processed)
            print(f"Duration: {duration:.1f} seconds")
    else:
        print("Usage: python core/audio_processor.py your_audio.mp3")