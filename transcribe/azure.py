import os
import time
import json
import azure.cognitiveservices.speech as speechsdk


def transcribe_audio(audio_path: str, **kwargs):
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_SPEECH_API_KEY"),
        region=os.getenv("AZURE_SPEECH_API_REGION"),
    )

    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)

    lang = kwargs.get("lang")
    if not lang:
        # auto detect speech language
        auto_detect_source_language_config = (
            speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
                languages=["en-US", "en-IN", "hi-IN"]
            )
        )
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            auto_detect_source_language_config=auto_detect_source_language_config,
            audio_config=audio_config,
        )
        recognize_result = speech_recognizer.recognize_once()
        auto_detect_source_language_result = speechsdk.AutoDetectSourceLanguageResult(
            recognize_result
        )
        lang = auto_detect_source_language_result.language

    speech_config.speech_recognition_language = lang

    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
    conversation_transcriber = speechsdk.transcription.ConversationTranscriber(
        speech_config=speech_config, audio_config=audio_config
    )
    done = False

    def stop_cb(evt):
        print("CLOSING on {}".format(evt))
        conversation_transcriber.stop_transcribing_async()
        nonlocal done
        done = True

    all_results = []

    def handle_transcribed_event(evt):
        all_results.append(evt.result)

    # conversation_transcriber.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    conversation_transcriber.transcribed.connect(handle_transcribed_event)
    conversation_transcriber.session_started.connect(
        lambda evt: print("SESSION STARTED: {}".format(evt))
    )
    conversation_transcriber.session_stopped.connect(
        lambda evt: print("SESSION STOPPED {}".format(evt))
    )
    conversation_transcriber.canceled.connect(
        lambda evt: print("CANCELED {}".format(evt))
    )

    conversation_transcriber.session_stopped.connect(stop_cb)
    conversation_transcriber.canceled.connect(stop_cb)

    conversation_transcriber.start_transcribing_async()
    while not done:
        time.sleep(0.5)

    if done:
        return {
            "text": "\n".join([result.text for result in all_results]),
            "json_response": [json.loads(result.json) for result in all_results],
        }
