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
        - text (str): Text from which we make extractions.

        Returns:
        - report (str): A list of questions generated by AI in the form of a string, where every question is separated by a \n.
    """
    prompt = (
        "You are an expert information extractor. From the text that is sent to you, extract all facts that are said and that can be checked for truthfullness by searching through the internet, turn them into a question in Serbian language that has a format of 'Yes' or 'No' answer (without questions like: 'Da li je govornik rekao to i to'), without any comma in a single question, replace all commas with ; and make a list of all these questions."
    )
    messages = [
        {"role": "system", "content": "You are a skilled information extractor."},
        {"role": "user",
         "content": f"Text: {text}\n\n{prompt}"}
    ]
    report = await call_openrouter_async(session, messages)
    return report

QUERY_INDEX = 0
ANSWER_INDEX = 1
EXPECTED_INDEX = 2
PRECISION_INDEX = 3
LINKS_INDEX = 4

PATH_SPEECH =".\\speeches\\"
SPEECH_FILE_NAME= "govor_vucic_jagodina_miting.txt"        # Change SPEECH_FILE_NAME when reading new text
PATH_TO_SPEECH_FILE = PATH_SPEECH + SPEECH_FILE_NAME

PATH_DATA = ".\\data\\"     
CSV_FILE_NAME = "data_jagodina2.csv"                 # Change CSV_FILE_NAME when writing a new one
PATH_TO_CSV_FILE = PATH_DATA + CSV_FILE_NAME

PATH_PRECISION = ".\\precision\\"
LOG_FILE_NAME = "precision_log.txt"                    # Don't change
PATH_TO_LOG_FILE = PATH_PRECISION + LOG_FILE_NAME

PATH_QUESTIONS = ".\\questions\\"
QUESTIONS_FILE_NAME = "izdvojena_pitanja_jagodina.txt"              # Change QUESTIONS_FILE_NAME when reading from a new example
PATH_TO_QUESTIONS_FILE = PATH_QUESTIONS + QUESTIONS_FILE_NAME

HEADER = "Pitanje, Odgovor, Očekivan odgovor, Tačnost, Linkovi, Likovi za referencu\n"

def read_file(filename):
    """
        Reads a TXT file and extracts its content.

        Parameters:
        - filename (str): The path to the file.

        Returns:
        - text(str): Extracted text
    """
    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()
        return text


# Funkcija za upisivanje odgovora u CSV fajl
def write_results(csv_filename, data):
    """
        Writes generated questions to a CSV file:
        - Updates the question column (0).
        - Stores the links used for each query.
        - Calculates and records the overall accuracy percentage in log file.

        Parameters:
        - filename (str): The path to the output CSV file.
        - data (List[str]): A list of generated answers.
    """
    rows = []
    for i, value in enumerate(data):
        rows.append(value+",,,,,,\n")       # All commas are for all the empty columns in a new CSV file

    # Write back to the CSV file
    with open(csv_filename, "w", encoding="utf-8", newline="") as file:
        file.write(HEADER)                  # Write the header row
        file.write("".join(rows))
    
async def asyncio_main(text):
    """
        Asynchronous function that extracts questions from the given text using an AI model and writes the results to a CSV file.

        Parameters:
        - text (str): The input text from which questions will be generated.

        Workflow:
        1. Creates an asynchronous HTTP session using aiohttp.
        2. Calls the extract_questions function to generate questions from the text.
        3. Uses asyncio.gather to handle asynchronous execution.
        4. Splits the result into a list of questions.
        5. Writes the extracted questions to a CSV file.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [extract_questions(session,text)]    
        result = await asyncio.gather(*tasks)    
        res=result[0].split("\n")
        write_results(PATH_TO_CSV_FILE,res)

def main():
    text = read_file(PATH_TO_SPEECH_FILE)
    asyncio.run(asyncio_main(text))

if __name__ == "__main__":
    main()