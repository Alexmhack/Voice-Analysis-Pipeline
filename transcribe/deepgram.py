import os

from typing import Dict, Any
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)


def transcribe_audio(audio_path: str) -> Dict[str, Any]:
    API_KEY = os.getenv("DG_API_KEY")
    deepgram = DeepgramClient(API_KEY)

    with open(audio_path, "rb") as file:
        buffer_data = file.read()

    payload: FileSource = {
        "buffer": buffer_data,
    }
    options = PrerecordedOptions(
        model="nova-2",
        smart_format=True,
    )
    response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

    return response.to_json()
