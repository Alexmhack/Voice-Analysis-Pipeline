import os
import io
import json
import assemblyai as aai

from utils import (
    upload_blob_stream,
    check_blob_exists,
    download_blob_to_stream,
    get_blob_url,
)

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")


def transcribe_url(file_url: str, _id: str) -> str:
    file_name, folder_name = f"{_id}_transcript.json", "transcripts"
    if check_blob_exists(folder_name, file_name):
        json_response = json.loads(download_blob_to_stream(folder_name, file_name))
        return {
            "_id": _id,
            "blob_url": get_blob_url(folder_name, file_name),
            "text": json_response.get("text"),
            "json_response": json_response,
        }

    config = aai.TranscriptionConfig(speaker_labels=True, auto_highlights=True)

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file_url, config=config)

    # TODO: when using multiple transciption models,
    # normalize the output transcript to a generalized format.

    transcript_json = json.dumps(transcript.json_response, indent=2)

    # upload to azure blob storage
    blob_url = upload_blob_stream(
        transcript_json, f"{_id}_transcript.json", "transcripts"
    )
    return {
        "_id": _id,
        "blob_url": blob_url,
        "text": transcript.text,
        "json_response": json.loads(transcript_json),
    }
