import os
import json

from typing import List
from openai import OpenAI


def get_transcript_summary(transcript_text: str) -> List[str]:
    """Generate summary by the given transcript text using ChatGPT API"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print("TRANSCRIPT TEXT:", transcript_text)

    example_data_schema = {
        "summary": [],
    }
    system_content = (
        "You are expert in analyzing and providing the following,\n"
        "1. Summary of the given conversation in 5 points\n\n"
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
