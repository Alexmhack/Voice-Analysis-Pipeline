import os
import ast
import proto

from typing import Dict, Any
from google.cloud import speech_v1p1beta1 as speech, storage


def transcribe_audio(
    audio_path: str,
) -> Dict[str, Any]:
    gcp_service_account_info = ast.literal_eval(os.getenv("GCP_SERVICE_ACCOUNT_INFO"))
    speech_client = speech.SpeechClient.from_service_account_info(
        gcp_service_account_info
    )

    # upload to GCP storage for speech purpose
    storage_client = storage.Client.from_service_account_info(gcp_service_account_info)
    bucket = storage_client.get_bucket(os.getenv("GCP_STORAGE_BUCKET_NAME"))
    file_name = os.path.basename(audio_path)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(audio_path)

    gcs_uri = f"gs://{bucket.name}/{file_name}"
    audio = speech.RecognitionAudio(uri=gcs_uri)

    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=10,
    )

    config = speech.RecognitionConfig(
        # audio encoding not needed when using .wav file formats
        # encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=8000,
        language_code="en-US",
        diarization_config=diarization_config,
        enable_automatic_punctuation=True,
    )

    operation = speech_client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=3600 * 3)

    transcript = []
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        transcript.append(f"{result.alternatives[0].transcript}\n")

    response_dict = proto.Message.to_dict(response)
    transcript_text = "".join(transcript)

    return {
        "text": transcript_text,
        "json_response": response_dict,
    }
