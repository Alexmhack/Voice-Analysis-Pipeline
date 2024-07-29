import os
import json
import logging

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
from .speechmatics import transcribe_audio as speechmatics_transcribe_audio
from .whisper import transcribe_audio as whisper_transcribe_audio
from .deepgram import transcribe_audio as deepgram_transcribe_audio


def transcribe_url(payload: dict) -> dict:
    _id = payload.get("_id")
    ## if force refresh the transcript then transcribe again
    force = payload.get("force", False)

    ## if transcript already exists then return it
    folder_name, file_name = "transcripts", f"{_id}_transcript.json"
    if not force and check_blob_exists(folder_name, file_name):
        blob_url = get_blob_url(folder_name, file_name)
        logging.info(f"Using cached transcript: {blob_url}")
        json_response = json.loads(download_blob_to_stream(folder_name, file_name))
        return {
            "_id": _id,
            "blob_url": blob_url,
            "text": json_response.get("text"),
            "json_response": json_response,
        }

    if force:
        logging.info(f"Force transcribing audio with payload: {payload}")

    ## download audio from url & convert to wav format for generalized audio format
    audio_path = download_audio_from_url(payload.get("url"), "/tmp/")
    wav_audio_output = convert_to_wav(audio_path)
    if (
        wav_audio_output.get("success")
        and (wav_audio_path := wav_audio_output.get("output"))
        and (wav_audio_exists := os.path.exists(wav_audio_path))
    ):
        logging.info(
            f"Convert to wav done for Payload: {payload} with wav output: {wav_audio_output} "
            f"and path exists: {wav_audio_exists}"
        )
    else:
        raise RuntimeError(
            f"Conversion to wav failed for Payload: {payload} with wav output: {wav_audio_output}"
        )

    model_used = payload.get("model", "assemblyai")

    logging.info(
        f"Starting transcription with model: {model_used} and payload: {payload}"
    )
    # by default transcript service is `assemblyai` if no model passed
    if model_used == "assemblyai":
        return {**payload, **assembly_transcribe_audio(wav_audio_path)}
    elif model_used == "google":
        return {**payload, **google_transcribe_audio(wav_audio_path)}
    elif model_used == "azure":
        return {**payload, **azure_transcribe_audio(wav_audio_path)}
    elif model_used == "speechmatics":
        return {**payload, **speechmatics_transcribe_audio(wav_audio_path)}
    elif model_used == "whisper":
        return {**payload, **whisper_transcribe_audio(wav_audio_path)}
    elif model_used == "deepgram":
        return {**payload, **deepgram_transcribe_audio(wav_audio_path)}

    else:
        raise RuntimeError(f"No model/service configuration found: {payload}")
