# Voice-Analysis-Pipeline
Production ready and scalable pipeline built for Voice(Audio) Analysis which includes Speech-to-Text(S2T) and then Enrichment(Summary, Sentiment, Word Cloud etc.) using Chat GPT.

Project is highly customizable and can be deployed as a standalone microservice on [Azure Durable Function App](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview?tabs=in-process%2Cnodejs-v3%2Cv1-model&pivots=csharp).

*A simple illustration of how this Microservice can be used for performing Voice Analysis*

![Voice Analysis Platform Workflow](https://github.com/Alexmhack/Voice-Analysis-Pipeline/blob/func-v1/Voice_Intelligence_Platform_Process_Flowchart.png?raw=true)

## Setup

Project was created in Python Version 3.10.12, any version above 3.10 should work fine.

Reference: [Quickstart](https://learn.microsoft.com/en-us/azure/azure-functions/durable/quickstart-python-vscode?tabs=windows%2Cazure-cli-set-indexing-flag&pivots=python-mode-configuration) - Python Durable Functions app in V1 programming model

1. `python -m venv venv`
2. `python -m pip install -U pip wheel setuptools uv`
3. `uv pip install -r requirements.txt`
4. Open the project in VS Code and run F5 (Debug command) to [Test the function locally](https://learn.microsoft.com/en-us/azure/azure-functions/durable/quickstart-python-vscode?tabs=windows%2Cazure-cli-set-indexing-flag&pivots=python-mode-configuration#test-the-function-locally)

## Reusability

1. To add or edit the Analysis Pipeline, make changes in *analysis/__init__.py*.
2. Google Speech APIs, Azure Speech APIs, Assembly AI is supported by default for S2T, you can add more S2T services or edit existing from the *transcribe* folder.
3. Encrichment includes generating Voice Conversation Summary, Overall & Sentences(utterances) sentiment, Wordcloud(excluding more than enough stop words), to generate something else or edit existing by making changes in the *metrics* folder.

[Postman Collection](https://github.com/Alexmhack/Voice-Analysis-Pipeline/blob/[branch]/image.jpg?raw=true)
