import json

from utils import (
    check_blob_exists,
    download_blob_to_stream,
    get_blob_url,
    convert_to_wav,
    download_audio_from_url,
)
from .assembly import transcribe_audio as assembly_transcribe_audio
from .google import transcribe_audio as google_transcribe_audio
from .azure import transcribe_audio as azure_transcribe_audio


def transcribe_url(payload: dict) -> dict:
    _id = payload.get("_id")
    ## if force refresh the transcript then transcribe again
    force = payload.get("force", False)

    ## if transcript already exists then return it
    folder_name, file_name = "transcripts", f"{_id}_transcript.json"
    if not force and check_blob_exists(folder_name, file_name):
        json_response = json.loads(download_blob_to_stream(folder_name, file_name))
        return {
            "_id": _id,
            "blob_url": get_blob_url(folder_name, file_name),
            "text": json_response.get("text"),
            "json_response": json_response,
        }

    ## download audio from url & convert to wav format for generalized audio format
    audio_path = download_audio_from_url(payload.get("url"), "/tmp/")
    wav_audio_output = convert_to_wav(audio_path)
    if wav_audio_output.get("success"):
        wav_audio_path = wav_audio_output.get("output")
    else:
        raise RuntimeError(f"Conversion to wav failed for Payload: {payload}")

    # by default transcript service is `assemblyai` if no model passed
    if payload.get("model", "assemblyai") == "assemblyai":
        return {**payload, **assembly_transcribe_audio(wav_audio_path)}
    elif payload.get("model") == "google":
        return {
            **payload,
            **google_transcribe_audio(wav_audio_path),
        }
    elif payload.get("model") == "azure":
        return {
            **payload,
            **azure_transcribe_audio(wav_audio_path),
        }
    else:
        raise RuntimeError(f"No model configuration found: {payload}")
