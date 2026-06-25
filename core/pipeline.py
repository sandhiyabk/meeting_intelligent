# core/pipeline.py

from core.audio_processor import (
    validate_audio_file,
    process_audio,
    cleanup_temp_files
)
from core.transcriber import transcribe_long_audio, get_segments_with_timestamps
from core.diarizer import get_speaker_timeline
from core.transcript_builder import (
    build_transcript,
    merge_consecutive_speakers,
    format_transcript_for_llm,
    format_transcript_for_display
)
from core.extractor import extract_meeting_insights
import json


def process_meeting(
    audio_file_path: str,
    meeting_title: str = "Meeting",
    min_speakers: int = 1,
    max_speakers: int = 8,
    whisper_model: str = "base"
) -> dict:
    """
    Complete meeting intelligence pipeline.

    Steps:
    1. Validate audio file
    2. Process audio (convert to 16kHz mono WAV)
    3. Transcribe with Whisper
    4. Diarize speakers with Pyannote
    5. Build speaker-labeled transcript
    6. Extract insights with LLM
    7. Return structured result
    """

    print("\n" + "="*50)
    print("MEETING INTELLIGENCE PIPELINE")
    print("="*50)

    # Step 1: Validate
    print("\nStep 1: Validating audio file...")
    validation = validate_audio_file(audio_file_path)
    if not validation["valid"]:
        return {
            "success": False,
            "error": validation["error"]
        }
    print(f"Valid audio: {validation['size_mb']}MB, {validation['format']}")

    # Step 2: Process audio
    print("\nStep 2: Processing audio...")
    processed_path = process_audio(audio_file_path)

    # Step 3: Transcribe
    print("\nStep 3: Transcribing with Whisper...")
    transcription = transcribe_long_audio(processed_path, whisper_model)
    whisper_segments = get_segments_with_timestamps(transcription)
    print(f"Transcription: {len(whisper_segments)} segments")

    # Step 4: Diarize
    print("\nStep 4: Identifying speakers with Pyannote...")
    speaker_timeline = get_speaker_timeline(
        processed_path,
        min_speakers=min_speakers,
        max_speakers=max_speakers
    )

    # Step 5: Build transcript
    print("\nStep 5: Building speaker-labeled transcript...")
    raw_transcript = build_transcript(whisper_segments, speaker_timeline)
    merged_transcript = merge_consecutive_speakers(raw_transcript)
    transcript_text = format_transcript_for_llm(merged_transcript)
    display_transcript = format_transcript_for_display(merged_transcript)

    # Step 6: Extract insights
    print("\nStep 6: Extracting insights with LLM...")
    insights = extract_meeting_insights(transcript_text, meeting_title)

    # Step 7: Cleanup
    print("\nStep 7: Cleaning up temp files...")
    cleanup_temp_files()

    print("\n" + "="*50)
    print("PIPELINE COMPLETE")
    print("="*50 + "\n")

    return {
        "success": True,
        "meeting_title": meeting_title,
        "full_transcript_text": transcript_text,
        "transcript": display_transcript,
        "insights": insights
    }


# Test directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = process_meeting(
            audio_file_path=sys.argv[1],
            meeting_title="Test Meeting",
            min_speakers=2,
            max_speakers=5
        )
        if result["success"]:
            print("\nINSIGHTS:")
            print(json.dumps(result["insights"], indent=2))
        else:
            print(f"Error: {result['error']}")
    else:
        print("Usage: python core/pipeline.py your_meeting.mp3")