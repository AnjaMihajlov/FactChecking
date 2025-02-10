import asyncio
import datetime

import aiohttp
import json
import csv

# =======================
# Configuration Constants
# =======================
OPENROUTER_API_KEY = "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"

# Endpoints
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Default LLM model (can be changed if desired)
# DEFAULT_MODEL = "anthropic/claude-3.5-haiku"
DEFAULT_MODEL = "gpt-3.5-turbo"


# ============================
# Asynchronous Helper Functions
# ============================
async def call_openrouter_async(session, messages, model=DEFAULT_MODEL):
    """
    Asynchronously call the OpenRouter chat completion API with the provided messages.
    Returns the content of the assistant’s reply.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "X-Title": "OpenDeepResearcher, by Matt Shumer",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages
    }
    try:
        async with session.post(OPENROUTER_URL, headers=headers, json=payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                try:
                    return result['choices'][0]['message']['content']
                except (KeyError, IndexError) as e:
                    print("Unexpected OpenRouter response structure:", result)
                    return None
            else:
                text = await resp.text()
                print(f"OpenRouter API error: {resp.status} - {text}")
                return None
    except Exception as e:
        print("Error calling OpenRouter:", e)
        return None

async def extract_questions(session, text):
    """
        Function that uses AI model to extract mentioned facts from text and make questions from them.

        Parameters:
        - session (aiohttp.ClientSession): The session used for making HTTP requests.
        - text (str): Text from which we make exreactions.

        Returns:
        - report (str): A list of questions generated by AI.
    """
    prompt = (
        "You are an expert information extractor. From the text that is sent to you, extract all facts that are said, turn them into a question that has a format of 'Yes' or 'No' answer and make a list of all these questions."
    )
    messages = [
        {"role": "system", "content": "You are a skilled information extractor."},
        {"role": "user",
         "content": f"Text: {text}\n\n{prompt}"}
    ]
    report = await call_openrouter_async(session, messages)
    return report

FOLDER_PATH =".\\govori_u_tekstualnom_obliku\\"
FILE_PATH = "govor_vucic_izbori_2017.txt"

PATH_TO_TEXT = FOLDER_PATH + FILE_PATH

def read_file(filename):
    """
        Reads a TXT file and extracts its contents

        Parameters:
        - filename (str): The path to the file.

        Returns:
        - Extracted text (str)
    """
    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()
        return text


    
async def asyncio_main(text):
    async with aiohttp.ClientSession() as session:
        tasks = [extract_questions(session,text)]    
        result = await asyncio.gather(*tasks)    
        print(result)

def main():
    text = read_file(PATH_TO_TEXT)
    asyncio.run(asyncio_main(text))


if __name__ == "__main__":
    main()