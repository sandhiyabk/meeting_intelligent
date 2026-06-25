# tests/test_pipeline.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.transcript_builder import (
    build_transcript,
    merge_consecutive_speakers,
    format_transcript_for_llm
)
from core.extractor import extract_meeting_insights


def test_transcript_builder():
    """Test transcript building without audio."""
    print("\nTEST: Transcript Builder")

    whisper_segments = [
        {"start": 0.0, "end": 5.0, "text": "Hello everyone welcome"},
        {"start": 5.0, "end": 10.0, "text": "Today we discuss Q3 results"},
        {"start": 10.0, "end": 18.0, "text": "I think we should increase budget"},
        {"start": 18.0, "end": 25.0, "text": "Agreed Priya can you prepare proposal"},
        {"start": 25.0, "end": 30.0, "text": "Sure I will send it by Thursday"},
    ]

    speaker_timeline = [
        {"speaker": "SPEAKER_00", "start": 0.0, "end": 12.0},
        {"speaker": "SPEAKER_01", "start": 12.0, "end": 22.0},
        {"speaker": "SPEAKER_00", "start": 22.0, "end": 26.0},
        {"speaker": "SPEAKER_01", "start": 26.0, "end": 32.0},
    ]

    transcript = build_transcript(whisper_segments, speaker_timeline)
    merged = merge_consecutive_speakers(transcript)
    formatted = format_transcript_for_llm(merged)

    print("Formatted transcript:")
    print(formatted)
    print(f"Segments: {len(merged)}")
    assert len(merged) > 0, "Transcript should not be empty"
    print("✅ PASS")
    return formatted


def test_llm_extractor(transcript_text: str):
    """Test LLM extraction."""
    print("\nTEST: LLM Extractor")

    result = extract_meeting_insights(
        transcript_text,
        "Test Meeting"
    )

    print("Extracted insights:")
    import json
    print(json.dumps(result, indent=2))

    assert "summary" in result
    assert "action_items" in result
    assert "decisions" in result
    print("✅ PASS")


def run_all_tests():
    print("="*50)
    print("MEETING INTELLIGENCE — TEST SUITE")
    print("="*50)

    transcript = test_transcript_builder()
    test_llm_extractor(transcript)

    print("\n" + "="*50)
    print("ALL TESTS PASSED")
    print("="*50)


if __name__ == "__main__":
    run_all_tests()