import json
import azure.functions as func
import azure.durable_functions as df

from typing import Union, Dict, Any
from transcribe.assembly import transcribe_url as assembly_transcribe_url
from metrics.sentiment import calc_sentiment, calc_sentence_sentiment
from utils import upload_blob_stream

quadzApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)


## An HTTP-Triggered Function with a Durable Functions Client binding
@quadzApp.route(route="orchestrators/{functionName}")
@quadzApp.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client):
    # functionName here is the name of the orchestration function - `analyse_orchestrator`
    function_name = req.route_params.get("functionName")
    req_data = req.get_json()

    instance_id = await client.start_new(function_name, None, req_data)
    response = client.create_check_status_response(req, instance_id)
    return response


## Orchestrator
@quadzApp.orchestration_trigger(context_name="context")
def analyse_orchestrator(context: df.DurableOrchestrationContext):
    input_context = context.get_input()
    audio_url = input_context.get("audio_url")
    model = input_context.get("model")
    _id = input_context.get("id")

    first_retry_interval_in_milliseconds = 5000
    max_number_of_attempts = 3

    retry_options = df.RetryOptions(
        first_retry_interval_in_milliseconds, max_number_of_attempts
    )

    transcribe_payload = {"url": audio_url, "model": model, "_id": _id}
    transcript_output = yield context.call_activity_with_retry(
        "transcribe_audio", retry_options, transcribe_payload
    )
    transcript_output = yield context.call_activity_with_retry(
        "calculate_overall_sentiment", retry_options, transcript_output
    )
    transcript_output = yield context.call_activity_with_retry(
        "calculate_sentence_sentiment", retry_options, transcript_output
    )
    transcript_output = yield context.call_activity_with_retry(
        "generate_wordcloud_data", retry_options, transcript_output
    )
    blob_url = yield context.call_activity_with_retry(
        "store_updated_transcript", retry_options, transcript_output
    )

    return blob_url


## Activities
# Naming convention for `input_name` allows only alphanumeric, no underscores
@quadzApp.activity_trigger(input_name="payload")
def transcribe_audio(payload: Dict[str, str]) -> Union[str, None]:
    """
    Transcribe audio using the model mentioned in the payload
    and returns the blob URL for the transcript file
    """
    if payload.get("model", "assemblyai") == "assemblyai":
        return assembly_transcribe_url(payload.get("url"), payload.get("_id"))
    else:
        return None


@quadzApp.activity_trigger(input_name="transcriptOutput")
def calculate_overall_sentiment(transcriptOutput: Dict[str, Any]) -> str:
    if transcriptOutput.get("sentiment_score"):
        return transcriptOutput

    transcriptOutput.update(
        {
            "json_response": {
                **transcriptOutput.get("json_response"),
                **calc_sentiment(transcriptOutput.get("text")),
            }
        }
    )
    return transcriptOutput


@quadzApp.activity_trigger(input_name="transcriptOutput")
def calculate_sentence_sentiment(transcriptOutput: str) -> str:
    transcriptOutput.update(
        {
            "utterances": calc_sentence_sentiment(
                transcriptOutput.get("json_response", {}).get("utterances", [])
            )
        }
    )
    return transcriptOutput


@quadzApp.activity_trigger(input_name="transcriptOutput")
def generate_wordcloud_data(transcriptOutput: str) -> str:
    """For now we are using the AssemblyAI's auto_highlights_result for wordcloud data"""
    return transcriptOutput


@quadzApp.activity_trigger(input_name="transcriptOutput")
def store_updated_transcript(transcriptOutput: str) -> str:
    updated_transcript_json = json.dumps(
        transcriptOutput.get("json_response"), indent=2
    )
    blob_url = upload_blob_stream(
        updated_transcript_json,
        f"{transcriptOutput.get('_id')}_transcript.json",
        "transcripts",
    )
    return blob_url
