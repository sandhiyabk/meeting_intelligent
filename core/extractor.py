# core/extractor.py

import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

from core.config import GROQ_API_KEY
client = Groq(api_key=GROQ_API_KEY)


def extract_meeting_insights(transcript: str,
                              meeting_title: str = "Meeting") -> dict:
    """
    Use LLM to extract structured insights from transcript.
    """
    prompt = f"""You are an expert meeting analyst.

Analyze this meeting transcript carefully and extract:
1. A concise summary (3 sentences max)
2. Key decisions made during the meeting
3. Action items with owner names and deadlines if mentioned
4. Open questions that were not resolved
5. Main topics discussed
6. List of participant speaker labels

MEETING TRANSCRIPT:
{transcript}

Return ONLY valid JSON with no text before or after:
{{
    "summary": "3 sentence summary of the meeting",
    "decisions": [
        "decision 1",
        "decision 2"
    ],
    "action_items": [
        {{
            "task": "what needs to be done",
            "owner": "person name or UNKNOWN",
            "deadline": "date/timeframe or UNKNOWN"
        }}
    ],
    "open_questions": [
        "unresolved question 1"
    ],
    "topics": [
        "topic 1",
        "topic 2"
    ],
    "participants": [
        "SPEAKER_00",
        "SPEAKER_01"
    ],
    "meeting_duration_estimate": "X minutes"
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a meeting intelligence system. "
                               "Extract structured insights from meeting "
                               "transcripts. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=2000,
        )

        raw = response.choices[0].message.content
        clean = re.sub(r'```json|```', '', raw).strip()
        return json.loads(clean)

    except json.JSONDecodeError:
        return {
            "summary": "Could not parse meeting summary",
            "decisions": [],
            "action_items": [],
            "open_questions": [],
            "topics": [],
            "participants": [],
            "meeting_duration_estimate": "Unknown",
            "raw_response": raw[:500]
        }

    except Exception as e:
        return {
            "summary": f"Extraction failed: {str(e)}",
            "decisions": [],
            "action_items": [],
            "open_questions": [],
            "topics": [],
            "participants": [],
            "meeting_duration_estimate": "Unknown"
        }


# Test directly
if __name__ == "__main__":
    test_transcript = """
[SPEAKER_00] (00:00): Good morning everyone. Let's start the meeting.
[SPEAKER_01] (00:05): Good morning. I have the Q3 report ready.
[SPEAKER_00] (00:10): Great. Let's review the budget first.
[SPEAKER_01] (00:15): We need to increase the marketing budget by 20%.
[SPEAKER_02] (00:22): I agree. Can we get approval by Friday?
[SPEAKER_00] (00:28): Yes. Rahul please prepare the proposal by Thursday.
[SPEAKER_01] (00:35): Sure I will send it by Thursday evening.
[SPEAKER_00] (00:40): Good. Any open questions?
[SPEAKER_02] (00:44): What about the Q4 targets? We haven't discussed that.
[SPEAKER_00] (00:50): We will cover that in the next meeting.
"""

    result = extract_meeting_insights(test_transcript)
    print(json.dumps(result, indent=2))