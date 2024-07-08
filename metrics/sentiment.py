import os
import json

from typing import List, Dict, Any
from openai import OpenAI


def calc_sentiment(transcript_text: str) -> float:
    """Calculate sentiment by parsing the text from the transcript url and calling ChatGPT API"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    example_data_schema = {
        "sentiment_score": 0,
    }
    system_content = (
        "You are expert in analyzing and providing the following,\n"
        "1. Sentiment of given text on a scale from -1 to 1\n\n"
        "Trim the input text if it exceedes the model context length."
        f"Generate JSON in schema: {json.dumps(example_data_schema)}"
    )

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": f"Analyze the following: {transcript_text}"},
    ]
    completion = client.chat.completions.create(
        model="gpt-4-turbo",  # best results are being given by gpt-4-turbo
        messages=messages,
        temperature=0,
        top_p=0,
        response_format={"type": "json_object"},
    )
    return json.loads(completion.choices[0].message.content)


def calc_sentence_sentiment(transcript_utterances: List[Dict[str, Any]]):
    """Calculate sentiment of each sentences by looping over the list and calling ChatGPT API"""

    for transcript_dict in transcript_utterances:
        if transcript_dict.get("sentiment_score") is not None:
            continue

        transcript_text = transcript_dict["text"]
        transcript_sentiment = calc_sentiment(transcript_text)
        if isinstance(transcript_sentiment, dict):
            transcript_sentiment = transcript_sentiment.get("sentiment_score")
            transcript_dict["sentiment_score"] = transcript_sentiment

    return transcript_utterances
