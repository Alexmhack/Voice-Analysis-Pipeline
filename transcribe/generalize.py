import json

from utils import upload_blob_stream


def generalize_transcript(transcript_output: dict) -> dict:
    transcript_json = transcript_output.get("json_response")
    transcript_text = transcript_output.get("text")
    force = transcript_output.get("force")

    # don't generalize, use cached data instead
    if isinstance(transcript_json, dict) and (
        transcript_json.get("generalized") and not force
    ):
        return transcript_output

    # using assemblyai output as the generalized output
    model_used = transcript_output.get("model", "assemblyai")

    # generalized transcript for final use in UI
    generalized_transcript_json = {
        "utterances": [],
        "text": transcript_text,
        "wordcloud": [],
        "generalized": True,
    }

    if model_used == "assemblyai":
        generalized_transcript_json["utterances"] = transcript_json.get("utterances")
        # assembly provides us with wordcloud data as well in `auto_highlights_result`
        generalized_transcript_json["wordcloud"] = transcript_json.get(
            "auto_highlights_result", {}
        ).get("result")
    elif model_used == "google":
        for tt_data in transcript_json.get("results", []):
            data = tt_data["alternatives"][0]
            transcript_text = data["transcript"]
            confidence = data["confidence"]
            speaker = data["words"][0]["speaker_tag"]
            start = float(data["words"][0]["start_time"].replace("s", "")) * 1000
            end = float(data["words"][-1]["end_time"].replace("s", "")) * 1000
            generalized_transcript_json["utterances"].append(
                {
                    "text": transcript_text,
                    "start": start,
                    "end": end,
                    "speaker": speaker,
                    "confidence": confidence,
                }
            )
    elif model_used == "azure":
        for tt_data in transcript_json:
            transcript_text = tt_data["DisplayText"]
            speaker = tt_data["SpeakerId"]
            start = tt_data["Offset"] / 10000  # convert this to proper seconds
            end = (tt_data["Offset"] + tt_data["Duration"]) / 10000  # convert
            generalized_transcript_json["utterances"].append(
                {
                    "text": transcript_text,
                    "start": start,
                    "end": end,
                    "speaker": speaker,
                }
            )

    transcript_output["json_response"] = generalized_transcript_json

    # upload generalized transcript for caching
    upload_blob_stream(
        json.dumps(generalized_transcript_json, indent=2),
        f"{transcript_output.get('_id')}_transcript.json",
        "transcripts",
    )

    return transcript_output
