import os
import json
import assemblyai as aai

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")


def transcribe_audio(audio_path: str) -> str:
    config = aai.TranscriptionConfig(speaker_labels=True, auto_highlights=True)

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_path, config=config)

    # TODO: when using multiple transciption models,
    # normalize the output transcript to a generalized format.

    transcript_json = json.dumps(transcript.json_response, indent=2)

    return {
        "text": transcript.text,
        "json_response": json.loads(transcript_json),
    }
