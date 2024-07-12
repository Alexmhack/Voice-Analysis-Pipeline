import os

from typing import Dict, Any
from speechmatics.batch_client import BatchClient


def transcribe_audio(audio_path: str) -> Dict[str, Any]:
    API_KEY = os.getenv("SPEECHMATICS_API_KEY")
    LANGUAGE = "auto"

    # Define transcription parameters
    conf = {
        "type": "transcription",
        "transcription_config": {"language": LANGUAGE},
        "language_identification_config": {"low_confidence_action": "allow"},
    }

    with BatchClient(API_KEY) as client:
        job_id = client.submit_job(audio_path, transcription_config=conf)
        print(f"job {job_id} submitted successfully, waiting for transcript")

        # Note that in production, you should set up notifications instead of polling.
        # Notifications are described here: https://docs.speechmatics.com/features-other/notifications
        transcript = client.wait_for_completion(job_id, transcription_format="json")
        total_text = []
        transcript_data = []
        for result in transcript.get("results", []):
            tt_data = result["alternatives"][0]
            total_text.append(tt_data["content"])
            speaker = tt_data["speaker"]
            start_time = result["start_time"]
            end_time = result["end_time"]
            transcript_data.append(
                {
                    "speaker": speaker,
                    "start": start_time,
                    "end": end_time,
                    "text": tt_data["content"],
                }
            )
