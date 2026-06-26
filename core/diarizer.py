# core/diarizer.py

import torch
import numpy as np

from core.config import HF_TOKEN
_pipeline = None


def get_diarization_pipeline():
    """Load Pyannote pipeline once and reuse."""
    global _pipeline
    if _pipeline is None:
        print("Loading Pyannote diarization pipeline...")
        from pyannote.audio import Pipeline
        _pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=HF_TOKEN
        )
        print("Diarization pipeline loaded")
    return _pipeline


def load_audio_tensor(audio_path: str) -> dict:
    """
    Load audio using soundfile + numpy.
    Completely bypasses torchcodec and torchaudio.
    """
    import soundfile as sf

    print(f"Loading audio with soundfile: {audio_path}")

    # Read audio file
    waveform_np, sample_rate = sf.read(audio_path, dtype='float32')

    print(f"Original shape: {waveform_np.shape}, "
          f"sample_rate: {sample_rate}")

    # Handle stereo → mono
    if waveform_np.ndim == 2:
        waveform_np = waveform_np.mean(axis=1)

    # Resample to 16kHz if needed
    if sample_rate != 16000:
        import scipy.signal as signal
        num_samples = int(len(waveform_np) * 16000 / sample_rate)
        waveform_np = signal.resample(waveform_np, num_samples)
        sample_rate = 16000
        print(f"Resampled to 16kHz")

    # Convert to torch tensor — shape must be (1, time)
    waveform_tensor = torch.tensor(
        waveform_np, dtype=torch.float32
    ).unsqueeze(0)

    print(f"Tensor shape: {waveform_tensor.shape}, "
          f"sample_rate: {sample_rate}")

    return {
        "waveform": waveform_tensor,
        "sample_rate": sample_rate
    }

def get_speaker_timeline(
    audio_path: str,
    min_speakers: int = 1,
    max_speakers: int = 8
) -> list:
    """
    Identify who spoke when in audio.
    Returns list of speaker segments with timestamps.
    """
    pipeline = get_diarization_pipeline()

    print(f"Running diarization on: {audio_path}")

    audio_input = load_audio_tensor(audio_path)

    diarization = pipeline(
        audio_input,
        min_speakers=min_speakers,
        max_speakers=max_speakers
    )

    timeline = []

    # DiarizeOutput object — access .speaker_diarization
    annotation = diarization.speaker_diarization

    print(f"Annotation type: {type(annotation)}")

    # Standard pyannote Annotation API
    for segment, track, speaker in annotation.itertracks(yield_label=True):
        timeline.append({
            "speaker": speaker,
            "start": round(segment.start, 2),
            "end": round(segment.end, 2)
        })

    unique_speakers = list(set([t["speaker"] for t in timeline]))
    print(f"Complete: {len(unique_speakers)} speakers detected")
    print(f"Speakers: {unique_speakers}")
    print(f"Total segments: {len(timeline)}")

    return timeline

def rename_speakers(timeline: list,
                     name_map: dict = None) -> list:
    if not name_map:
        return timeline
    renamed = []
    for segment in timeline:
        new_segment = segment.copy()
        new_segment["speaker"] = name_map.get(
            segment["speaker"], segment["speaker"]
        )
        renamed.append(new_segment)
    return renamed


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        timeline = get_speaker_timeline(sys.argv[1])
        print("\nSpeaker timeline:")
        for segment in timeline[:10]:
            print(
                f"[{segment['start']:.1f}s → {segment['end']:.1f}s] "
                f"{segment['speaker']}"
            )
    else:
        print("Usage: python core/diarizer.py audio.wav")