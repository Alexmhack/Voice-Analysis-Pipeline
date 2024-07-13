import json
import logging

from typing import Dict, Any

from transcribe import transcribe_url, generalize_transcript
from metrics import calc_sentiment, calc_sentence_sentiment, get_transcript_summary
from utils import upload_blob_stream


def calculate_overall_sentiment(transcript_output: Dict[str, Any]) -> str:
    if transcript_output.get("json_response", {}).get("sentiment_score") is not None:
        return transcript_output

    transcript_output["json_response"].update(
        {
            **calc_sentiment(transcript_output.get("text")),
        }
    )
    return transcript_output


def generate_wordcloud_data(transcript_output: Dict[str, Any]) -> Dict[str, Any]:
    """For now we are using the AssemblyAI's auto_highlights_result for wordcloud data"""
    return transcript_output


def calculate_sentence_sentiment(transcript_output: Dict[str, Any]) -> Dict[str, Any]:
    transcript_output["json_response"].update(
        {
            "utterances": calc_sentence_sentiment(
                transcript_output["json_response"].get("utterances", [])
            )
        }
    )
    return transcript_output


def generate_summary(transcript_output: Dict[str, Any]) -> Dict[str, Any]:
    if transcript_output.get("json_response", {}).get("summary"):
        return transcript_output

    transcript_output["json_response"].update(
        {
            "summary": get_transcript_summary(transcript_output.get("text")).get(
                "summary"
            )
        }
    )
    return transcript_output


def store_updated_transcript(transcript_output: Dict[str, Any]) -> Dict[str, Any]:
    updated_transcript_json = json.dumps(
        transcript_output.get("json_response"), indent=2
    )
    blob_url = upload_blob_stream(
        updated_transcript_json,
        f"{transcript_output.get('_id')}_transcript.json",
        "transcripts",
    )
    return blob_url


def main(payload: Dict[str, Any]):
    audio_url = payload.get("audio_url")
    model = payload.get("model")
    _id = payload.get("id")
    force = payload.get("force", False)

    transcribe_payload = {
        "url": audio_url,
        "model": model,
        "_id": _id,
        "force": force
    }

    transcript_output = transcribe_url(transcribe_payload)
    transcript_output = generalize_transcript(transcript_output)
    transcript_output = calculate_overall_sentiment(transcript_output)
    transcript_output = calculate_sentence_sentiment(transcript_output)
    transcript_output = generate_wordcloud_data(transcript_output)
    transcript_output = generate_summary(transcript_output)
    blob_url = store_updated_transcript(transcript_output)

    return blob_url
