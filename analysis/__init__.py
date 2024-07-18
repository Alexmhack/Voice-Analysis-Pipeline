import json
import logging
import requests

from typing import Dict, Any

from transcribe import transcribe_url, generalize_transcript
from metrics import calc_sentiment, calc_sentence_sentiment, get_transcript_summary
from utils import upload_blob_stream, get_wordcloud_data


def calculate_overall_sentiment(transcript_output: Dict[str, Any]) -> str:
    if transcript_output.get("json_response", {}).get("sentiment_score") is not None:
        logging.info(
            f"Using cached overall sentiment score for _id: {transcript_output['_id']}"
        )
        return transcript_output

    transcript_output["json_response"].update(
        {
            **calc_sentiment(transcript_output.get("text")),
        }
    )
    return transcript_output


def generate_wordcloud_data(transcript_output: Dict[str, Any]) -> Dict[str, Any]:
    """For now we are using the AssemblyAI's auto_highlights_result for wordcloud data"""
    if transcript_output.get("json_response", {}).get("wordcloud"):
        logging.info(f"Using cached wordcloud for _id: {transcript_output['_id']}")
        return transcript_output

    transcript_output["json_response"].update(
        {"wordcloud": get_wordcloud_data(transcript_output.get("text"))}
    )
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
        logging.info(f"Using cached summary for _id: {transcript_output['_id']}")
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


def call_callback_url(blob_url: str, callback_url: str) -> bool:
    response = requests.post(callback_url, json={"transcript_url": blob_url})
    return response.json()


def main(payload: Dict[str, Any]):
    audio_url = payload.get("audio_url")
    model = payload.get("model")
    _id = payload.get("id")
    force = payload.get("force", False)
    callback_url = payload.get("callback_url")

    logging.info(f"Recevied event payload: {payload}")

    transcribe_payload = {
        "url": audio_url,
        "model": model,
        "_id": _id,
        "force": force,
        "callback_url": callback_url,
    }

    logging.info(f"Starting analysis with payload: {transcribe_payload}")

    transcript_output = transcribe_url(transcribe_payload)
    logging.info(f"Transcription done with model: {model}")

    transcript_output = generalize_transcript(transcript_output)
    output = transcript_output.get("json_response", {}).keys()
    logging.info(f"Generalizing transcript done: {output}")

    transcript_output = calculate_overall_sentiment(transcript_output)
    sentiment_score = transcript_output.get("json_response", {}).get("sentiment_score")
    logging.info(f"Overall sentiment calculation done: {sentiment_score}")

    transcript_output = calculate_sentence_sentiment(transcript_output)
    logging.info("Sentences sentiment calculation done")

    transcript_output = generate_wordcloud_data(transcript_output)
    logging.info("Wordcloud data generation done")

    transcript_output = generate_summary(transcript_output)
    summary = transcript_output.get("json_response", {}).get("summary")
    logging.info(f"Summary generated: {summary}")

    blob_url = store_updated_transcript(transcript_output)
    logging.info(f"Transcript stored in blob: {blob_url}")
    if callback_url:
        logging.info(f"Calling callback URL: {callback_url} with Blob: {blob_url}")
        callback_res = call_callback_url(blob_url, callback_url)
        logging.info(f"Callback call complete: {callback_res}")

    return blob_url
