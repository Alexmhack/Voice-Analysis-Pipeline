def generalize_transcript(transcript_output: dict) -> dict:
    transcript_json = transcript_output.get("json_response")
    transcript_text = transcript_output.get("text")

    # using assemblyai output as the generalized output
    model_used = transcript_output.get("model", "assemblyai")

    if model_used == "assemblyai":
        generalized_transcript_json = {
            "text": transcript_text,
            "utterances": transcript_json.get("utterances"),
            # assembly provides us with wordcloud data as well in `auto_highlights_result`
            "wordcloud": transcript_json.get("auto_highlights_result"),
        }
    elif model_used == "google":
        generalized_transcript_json = {
            "utterances": [],
            "text": transcript_text,
            "wordcloud": [],
        }
        for tt_data in transcript_json.get("results", []):
            data = tt_data["alternatives"][0]
            transcript_text = data["transcript"]
            confidence = data["confidence"]
            speaker = data["words"][0]["speaker_tag"]
            start = round(float(data["words"][0]["start_time"].replace("s", "")))
            end = round(float(data["words"][-1]["end_time"].replace("s", "")))
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
        generalized_transcript_json = {
            "utterances": [],
            "text": transcript_text,
            "wordcloud": [],
        }
        for tt_data in transcript_json:
            transcript_text = tt_data["DisplayText"]
            speaker = tt_data["SpeakerId"]
            start = tt_data["Offset"]  # convert this to proper seconds
            end = tt_data["Offset"] + tt_data["Duration"]  # convert
            generalized_transcript_json["utterances"].append(
                {
                    "text": transcript_text,
                    "start": start,
                    "end": end,
                    "speaker": speaker,
                }
            )

    transcript_output["json_response"] = generalized_transcript_json
    return transcript_output
