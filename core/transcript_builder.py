# core/transcript_builder.py


def match_speaker_to_segment(whisper_segment: dict,
                               speaker_timeline: list) -> str:
    """
    Find which speaker was talking during a Whisper segment
    by calculating timestamp overlap.
    """
    seg_start = whisper_segment["start"]
    seg_end = whisper_segment["end"]

    best_speaker = "UNKNOWN"
    best_overlap = 0

    for speaker_turn in speaker_timeline:
        sp_start = speaker_turn["start"]
        sp_end = speaker_turn["end"]
        speaker = speaker_turn["speaker"]

        # Calculate overlap duration
        overlap_start = max(seg_start, sp_start)
        overlap_end = min(seg_end, sp_end)
        overlap = max(0, overlap_end - overlap_start)

        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = speaker

    return best_speaker


def build_transcript(whisper_segments: list,
                      speaker_timeline: list) -> list:
    """
    Combine Whisper text segments with Pyannote speaker labels
    using timestamp overlap matching.
    """
    transcript = []

    for segment in whisper_segments:
        text = segment["text"].strip()
        if not text:
            continue

        speaker = match_speaker_to_segment(segment, speaker_timeline)

        transcript.append({
            "speaker": speaker,
            "start": segment["start"],
            "end": segment["end"],
            "text": text
        })

    return transcript


def merge_consecutive_speakers(transcript: list) -> list:
    """
    Merge consecutive segments from same speaker
    into natural speaking turns.
    """
    if not transcript:
        return []

    merged = [transcript[0].copy()]

    for segment in transcript[1:]:
        last = merged[-1]

        # Same speaker — merge
        if segment["speaker"] == last["speaker"]:
            last["text"] += " " + segment["text"]
            last["end"] = segment["end"]
        else:
            merged.append(segment.copy())

    return merged


def format_transcript_for_llm(transcript: list) -> str:
    """
    Format transcript as clean text for LLM input.
    """
    lines = []
    for segment in transcript:
        speaker = segment["speaker"]
        text = segment["text"]
        start = int(segment["start"])
        minutes = start // 60
        seconds = start % 60
        timestamp = f"{minutes:02d}:{seconds:02d}"
        lines.append(f"[{speaker}] ({timestamp}): {text}")

    return "\n".join(lines)


def format_transcript_for_display(transcript: list) -> list:
    """
    Format transcript for UI display.
    """
    formatted = []
    for segment in transcript:
        start = int(segment["start"])
        minutes = start // 60
        seconds = start % 60
        formatted.append({
            "speaker": segment["speaker"],
            "timestamp": f"{minutes:02d}:{seconds:02d}",
            "text": segment["text"]
        })
    return formatted


# Test directly
if __name__ == "__main__":
    # Sample test data
    whisper_segs = [
        {"start": 0.0, "end": 5.0, "text": "Hello everyone welcome"},
        {"start": 5.0, "end": 10.0, "text": "Today we discuss budget"},
        {"start": 10.0, "end": 15.0, "text": "I think we should increase"},
    ]

    speaker_tl = [
        {"speaker": "SPEAKER_00", "start": 0.0, "end": 8.0},
        {"speaker": "SPEAKER_01", "start": 8.0, "end": 20.0},
    ]

    transcript = build_transcript(whisper_segs, speaker_tl)
    merged = merge_consecutive_speakers(transcript)
    formatted = format_transcript_for_llm(merged)

    print("Formatted Transcript:")
    print(formatted)