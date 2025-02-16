import asyncio
import datetime
from idlelib.rpc import response_queue

import aiohttp
import json
import csv

# =======================
# Configuration Constants
# =======================
OPENROUTER_API_KEY_1 = "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"
OPENROUTER_API_KEY_2 = "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"
SERPAPI_API_KEY = "8706f4a156d896f21f6b0a8073730312a235dafbe17df1538530b055377ae9d9"
JINA_API_KEY = "jina_00b9f446343e4fb882ae966a4d6b2938rgwSI3s0w3nygZ2A4p3xkfOWnf1v"

# Endpoints
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
SERPAPI_URL = "https://serpapi.com/search"
JINA_BASE_URL = "https://r.jina.ai/"

# Default LLM model (can be changed if desired)
DEFAULT_MODEL = "anthropic/claude-3.5-haiku"
# DEFAULT_MODEL = "gpt-3.5-turbo"

# ============================
# Asynchronous Helper Functions
# ============================

async def call_openrouter_async(session, messages, model=DEFAULT_MODEL):
    """
    Asynchronously call the OpenRouter chat completion API with the provided messages.
    Returns the content of the assistant’s reply.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY_2}",
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


async def generate_search_queries_async(session, user_query):
    """
    Ask the LLM to produce up to four precise search queries (in Python list format)
    based on the user’s query.
    """
    prompt = (
        "You are an expert research assistant. Given the user's query, generate up to four distinct, "
        "precise search queries that would help gather comprehensive information on the topic. "
        "Return only a Python list of strings, for example: ['query1', 'query2', 'query3']."
    )
    messages = [
        {"role": "system", "content": "You are a helpful and precise research assistant."},
        {"role": "user", "content": f"User Query: {user_query}\n\n{prompt}"}
    ]
    response = await call_openrouter_async(session, messages)
    if response:
        try:
            # Expect exactly a Python list (e.g., "['query1', 'query2']")
            search_queries = eval(response)
            if isinstance(search_queries, list):
                return search_queries
            else:
                print("LLM did not return a list. Response:", response)
                return []
        except Exception as e:
            print("Error parsing search queries:", e, "\nResponse:", response)
            return []
    return []


async def perform_search_async(session, query):
    """
    Asynchronously perform a Google search using SERPAPI for the given query.
    Returns a list of result URLs.
    """
    params = {
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "engine": "google"
    }
    try:
        async with session.get(SERPAPI_URL, params=params) as resp:
            if resp.status == 200:
                results = await resp.json()
                if "organic_results" in results:
                    links = [item.get("link") for item in results["organic_results"] if "link" in item]
                    return links
                else:
                    print("No organic results in SERPAPI response.")
                    return []
            else:
                text = await resp.text()
                print(f"SERPAPI error: {resp.status} - {text}")
                return []
    except Exception as e:
        print("Error performing SERPAPI search:", e)
        return []


async def fetch_webpage_text_async(session, url):
    """
    Asynchronously retrieve the text content of a webpage using Jina.
    The URL is appended to the Jina endpoint.
    """
    full_url = f"{JINA_BASE_URL}{url}"
    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}"
    }
    try:
        async with session.get(full_url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.text()
            else:
                text = await resp.text()
                print(f"Jina fetch error for {url}: {resp.status} - {text}")
                return ""
    except Exception as e:
        print("Error fetching webpage text with Jina:", e)
        return ""


async def is_page_useful_async(session, user_query, page_text):
    """
    Ask the LLM if the provided webpage content is useful for answering the user's query.
    The LLM must reply with exactly "Yes" or "No".
    """
    prompt = (
        "You are a critical research evaluator. Given the user's query and the content of a webpage, "
        "determine if the webpage contains information relevant and useful for addressing the query. "
        "Respond with exactly one word: 'Yes' if the page is useful, or 'No' if it is not. Do not include any extra text."
    )
    messages = [
        {"role": "system", "content": "You are a strict and concise evaluator of research relevance."},
        {"role": "user",
         "content": f"User Query: {user_query}\n\nWebpage Content (first 20000 characters):\n{page_text[:20000]}\n\n{prompt}"}
    ]
    response = await call_openrouter_async(session, messages)
    if response:
        answer = response.strip()
        if answer in ["Yes", "No"]:
            return answer
        else:
            # Fallback: try to extract Yes/No from the response.
            if "Yes" in answer:
                return "Yes"
            elif "No" in answer:
                return "No"
    return "No"


async def extract_relevant_context_async(session, user_query, search_query, page_text):
    """
    Given the original query, the search query used, and the page content,
    have the LLM extract all information relevant for answering the query.
    """
    prompt = (
        "You are an expert information extractor. Given the user's query, the search query that led to this page, "
        "and the webpage content, extract all pieces of information that are relevant to answering the user's query. "
        "Return only the relevant context as plain text without commentary."
    )
    messages = [
        {"role": "system", "content": "You are an expert in extracting and summarizing relevant information."},
        {"role": "user",
         "content": f"User Query: {user_query}\nSearch Query: {search_query}\n\nWebpage Content (first 20000 characters):\n{page_text[:20000]}\n\n{prompt}"}
    ]
    response = await call_openrouter_async(session, messages)
    if response:
        return response.strip()
    return ""


async def get_new_search_queries_async(session, user_query, previous_search_queries, all_contexts):
    """
    Based on the original query, the previously used search queries, and all the extracted contexts,
    ask the LLM whether additional search queries are needed. If yes, return a Python list of up to four queries;
    if the LLM thinks research is complete, it should return "<done>".
    """
    context_combined = "\n".join(all_contexts)
    prompt = (
        "You are an analytical research assistant. Based on the original query, the search queries performed so far, "
        "and the extracted contexts from webpages, determine if further research is needed. "
        "If further research is needed, provide up to four new search queries as a Python list (for example, "
        "['new query1', 'new query2']). If you believe no further research is needed, respond with exactly <done>."
        "\nOutput only a Python list or the token <done> without any additional text."
    )
    messages = [
        {"role": "system", "content": "You are a systematic research planner."},
        {"role": "user",
         "content": f"User Query: {user_query}\nPrevious Search Queries: {previous_search_queries}\n\nExtracted Relevant Contexts:\n{context_combined}\n\n{prompt}"}
    ]
    response = await call_openrouter_async(session, messages)
    if response:
        cleaned = response.strip()
        if cleaned == "<done>":
            return "<done>"
        try:
            new_queries = eval(cleaned)
            if isinstance(new_queries, list):
                return new_queries
            else:
                print("LLM did not return a list for new search queries. Response:", response)
                return []
        except Exception as e:
            print("Error parsing new search queries:", e, "\nResponse:", response)
            return []
    return []


'''async def generate_final_report_async(session, user_query, all_contexts):
    """
    Generate the final comprehensive report using all gathered contexts.
    """
    context_combined = "\n".join(all_contexts)
    prompt = (
        "You are an expert researcher and report writer. Based on the gathered contexts below and the original query, "
        "write a report with only one word: Da, if the answer to the original query is positive, or Ne, if its not. "
    )
    messages = [
        {"role": "system", "content": "You are a skilled report writer."},
        {"role": "user",
         "content": f"User Query: {user_query}\n\nGathered Relevant Contexts:\n{context_combined}\n\n{prompt}"}
    ]
    report = await call_openrouter_async(session, messages)
    return report
'''

#New function for generating the final report, including Da/Ne answer and an explanation in case of a Ne
async def generate_final_report_async(session, user_query, all_contexts):
    """
    Generate the final comprehensive report using all gathered contexts.
    """
    context_combined = "\n".join(all_contexts)
    prompt = (
    "You are an expert researcher and report writer. Based on the gathered contexts below and the original query, provide a clear and definitive answer."
    "Start the response with Da if the gathered contexts confirm a positive answer, or Ne if they confirm a negative answer."
    "If the answer is Ne, follow it with a brief explanation in one sentence, which provides the correct answer. If the answer is Da, do not include any explanation—just write Da."
    "If the information in the gathered contexts is insufficient or unclear, respond **only** with: '-- Nije moguće sa sigurnošću utvrditi tačan odgovor na osnovu dostupnih podataka.'"
    "Do not add any additional explanation, reasoning, or commentary in this case—write **exactly** the specified text and nothing else."
    "Make the best possible conclusion based on the available data, but strictly follow this response format."
    )

    messages = [
        {"role": "system", "content": "You are a skilled report writer."},
        {"role": "user",
         "content": f"User Query: {user_query}\n\nGathered Relevant Contexts:\n{context_combined}\n\n{prompt}"}
    ]
    report = await call_openrouter_async(session, messages)
    return report

async def process_link(session, link, user_query, search_query, links_useful):
    """
    Process a single link: fetch its content, judge its usefulness, and if useful, extract the relevant context.
    """
    #print(f"Fetching content from: {link}")
    page_text = await fetch_webpage_text_async(session, link)
    if not page_text:
        return None
    usefulness = await is_page_useful_async(session, user_query, page_text)
    #print(f"Page usefulness for {link}: {usefulness}")
    if usefulness == "Yes":
        context = await extract_relevant_context_async(session, user_query, search_query, page_text)
        if context:
            #print(f"Extracted context from {link} (first 200 chars): {context[:200]}")
            links_useful.append(link)
            return context
    return None


# =========================
# OUR CODE
# =========================

# Asynchronous proccesing of all queries
async def process_queries(queries):
    """
      Process a list of queries concurrently:
      - For each query, make an asynchronous request.
      - Aggregate the responses and track the links used.

      Parameters:
      - queries (List[str]): A list of queries to be processed asynchronously.

      Returns:
      - Triple[List[str], List[str], List[str]]:
        1. A list of strings, where string 0 represents a response to query 0, string 1 a response to query 1 etc.
        2. A list of strings, where string 0 represents the aggregated links used for query 0, string 1 represents the aggregated links used for query 1 etc.
        3. A list od strings, where string 0 represents the right answer to query 0, string 1 the right answer to query 1 etc. If the response is 'Da', the answer is ''
      """
    responses = []
    results = []
    aggregated_links_used = []
    right_answers = []


    # Create one session for all the requests
    async with aiohttp.ClientSession() as session:
        tasks = [async_main(query, session) for query in queries]    # Create a list of tasks for each query to be processed
        results = await asyncio.gather(*tasks)       # Wait for all tasks to complete and gather results

        # Extract the responses and aggregated links which async_main function returns as a list of tuples
        responses = [r[0] for r in results]
        aggregated_links_used = [r[1] for r in results]
        right_answers = [r[2] for r in results]
    links_str = []
    for elem in aggregated_links_used:
        str = ", ".join(elem)       # Join the links for one query into a single string
        links_str.append(str)

    return responses,right_answers,links_str

# Main asynchronous routine - calls
async def async_main(user_query, session):
    """
     Perform an iterative search and context extraction process based on a user's query:
     - Generate initial search queries.
     - Perform searches iteratively to collect relevant links.
     - Process each link to extract useful context.
     - Continue until iteration limit is reached or no new context is found.

     Parameters:
     - user_query (str): The query provided by the user for searching.
     - session (aiohttp.ClientSession): The session used for making HTTP requests.

     Returns:
     - Tuple[str, List[str]]:
       1. A final report generated based on the aggregated context.
       2. A list of links that were deemed useful during the process.
    """
    iter_limit = DEFAULT_ITERATION
    links_used = []             # List to store links that are useful
    aggregated_contexts = []    # List to store all contexts gathered during the search process
    all_search_queries = []     # List to track all the search queries generated
    iteration = 0

    # Generate initial search queries based on the user query
    new_search_queries = await generate_search_queries_async(session, user_query)
    if not new_search_queries:
        return "No search queries were generated."

    all_search_queries.extend(new_search_queries)       # Add the generated queries to the list

    # Perform the search iteratively up to the iteration limit
    while iteration < iter_limit:
        iteration_contexts = []
        search_tasks = [perform_search_async(session, query) for query in new_search_queries]
        search_results = await asyncio.gather(*search_tasks)        # Gather the search results concurrently

        counter = 0
        unique_links = {}       # Dictionary to store unique links with their associated queries
        for idx, links in enumerate(search_results):
            query_used = new_search_queries[idx]
            for link in links:
                if link not in unique_links:
                    unique_links[link] = query_used
                    counter+=1
                if counter==LINKS_LIMIT: break        # Stop after finding LINKS_LIMIT number of unique links
            if counter == LINKS_LIMIT: break

        link_tasks = [process_link(session, link, user_query, unique_links[link], links_used) for link in unique_links]      # Process the unique links concurrently to extract relevant context
        link_results = await asyncio.gather(*link_tasks)     # Gather the results of processing each link

        for res in link_results:
            if res:
                iteration_contexts.append(res)

        if iteration_contexts:
            aggregated_contexts.extend(iteration_contexts)
        else:
            break  # If no new context is found, stop the process

        # Generate new search queries based on the aggregated contexts
        new_search_queries = await get_new_search_queries_async(session, user_query, all_search_queries,
                                                                aggregated_contexts)
        if new_search_queries == "<done>":
            break
        elif new_search_queries:
            all_search_queries.extend(new_search_queries)        # Add new search queries to the list
        else:
            break

        iteration += 1

    # Generate the final report based on the aggregated contexts
    final_report = await generate_final_report_async(session, user_query, aggregated_contexts)

    binary_answer = final_report[:2]
    right_answer = final_report[2:]

    return binary_answer, right_answer, links_used     # Return the final report and the useful links

async def extract_questions(session, text,speaker,date):
    """
        Function that uses AI model to extract mentioned facts from text and make questions from them.

        Parameters:
        - session (aiohttp.ClientSession): The session used for making HTTP requests.
        - text (str): Text from which we make extractions.

        Returns:
        - report (str): A list of questions generated by AI in the form of a string, where every question is separated by a \n.
    """
    prompt = (
        f"You are an expert information extractor. From the text that is sent to you, extract all facts that are said and that can be checked for truthfullness by searching through the internet, turn them into a question in Serbian language that has a format of 'Yes' or 'No' answer (without questions like: 'Da li je govornik rekao to i to'), without any comma in a single question, replace all commas with ; and make a list of all these questions. Have in mind that this speach is given by {speaker} on {date} date."
    )
    messages = [
        {"role": "system", "content": "You are a skilled information extractor."},
        {"role": "user",
         "content": f"Text: {text}\n\n{prompt}"}
    ]
    report = await call_openrouter_async(session, messages)
    return report




#Limits for search
DEFAULT_ITERATION = 2
LINKS_LIMIT = 5

QUERY_INDEX = 0
ANSWER_INDEX = 1
EXPECTED_INDEX = 2
PRECISION_INDEX = 3
RIGHT_ANSWER_INDEX = 4
LINKS_INDEX = 5

PATH_SPEECH =".\\speeches\\"
SPEECH_FILE_NAME= "govor_vucic_jagodina_miting.txt"     # Change SPEECH_FILE_NAME when reading new text
PATH_TO_SPEECH_FILE = PATH_SPEECH + SPEECH_FILE_NAME

PATH_DATA = ".\\data\\"     
CSV_FILE_NAME = "data_jagodina.csv"                 # Change CSV_FILE_NAME when writing a new one
PATH_TO_CSV_FILE = PATH_DATA + CSV_FILE_NAME

PATH_PRECISION = ".\\precision\\"
LOG_FILE_NAME = "precision_log.txt"                  # Don't change
PATH_TO_LOG_FILE = PATH_PRECISION + LOG_FILE_NAME

PATH_QUESTIONS = ".\\questions\\"
QUESTIONS_FILE_NAME = "izdvojena_pitanja_jagodina.txt"              # Change QUESTIONS_FILE_NAME when reading from a new example
PATH_TO_QUESTIONS_FILE = PATH_QUESTIONS + QUESTIONS_FILE_NAME

HEADER = "Pitanje, Odgovor, Očekivan odgovor, Tačnost, Tačan odgovor, Linkovi, Likovi za referencu\n"

SPEAKER = "Aleksadar Vučić" #Bice ucitano iz JSON-a
DATE = "24.01.2025"

# CSV reader
def read_file_csv(filename):
    """
        Reads a CSV file and extracts its contents while skipping the header row.

        Parameters:
        - filename (str): The path to the CSV file.

        Returns:
        - Tuple[List[List[str]], List[str]]:
          1. A list of rows (EXCLUDING the header), where each row is a list of strings.
          2. A list of queries extracted from the specific column defined by QUERY_INDEX (0).
    """
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)
        return rows[1:], [row[QUERY_INDEX] for row in rows[1:] if row]

# Funkcija za upisivanje odgovora u CSV fajl
def write_results(csv_filename, log_filename, data, rows, links_used, right_answers):
    """
        Writes processed results back to a CSV file:
        - Updates the answer and precision columns.
        - Stores the links used for each query.
        - Calculates and records the overall accuracy percentage in log file.

        Parameters:
        - filename (str): The path to the output CSV file.
        - data (List[str]): A list of generated answers.
        - rows (List[List[str]]): The original CSV data without header.
        - links_used (List[str]): A list of links used for each query.
    """
    counterPrecision=0
    for i, value in enumerate(data):
        rows[i][ANSWER_INDEX] = value
        rows[i][RIGHT_ANSWER_INDEX] = str(right_answers[i])
        rows[i][RIGHT_ANSWER_INDEX] = right_answers[i].replace(", ", "").strip()
        if (rows[i][ANSWER_INDEX] == rows[i][EXPECTED_INDEX]):
            rows[i][PRECISION_INDEX] = 1
            counterPrecision+=1
        else:
            rows[i][PRECISION_INDEX] = 0

        rows[i][LINKS_INDEX] = links_used[i][1:-1]      # Slicing from 1 to -1 because the first and last characters are ", so we slice them to get only links

    # Write back to the CSV file
    with open(csv_filename, "w", encoding="utf-8", newline="") as file:
        file.write(HEADER)              # Write the header row
        writer = csv.writer(file)
        writer.writerows(rows)          # Write the modified rows

    accuracy_percentage = counterPrecision/len(rows)*100

    # Write to log file
    with open(log_filename, "a", encoding="utf-8") as logfile:
        logfile.write(f"{datetime.datetime.now()}: {accuracy_percentage:.2f}%\n")

    print(f"Accuracy percentage ({accuracy_percentage:.2f}%) writen into {log_filename}.")


def read_file_text(filename):
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
def write_results_csv(csv_filename, data):
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
    
async def asyncio_extraction_questions(text):
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
        tasks = [extract_questions(session,text,SPEAKER,DATE)]    
        result = await asyncio.gather(*tasks)    
        res=result[0].split("\n")
        write_results_csv(PATH_TO_CSV_FILE,res)

def main():
    text = read_file_text(PATH_TO_SPEECH_FILE)
    asyncio.run(asyncio_extraction_questions(text))
    input_file, queries = read_file_csv(PATH_TO_CSV_FILE)
    results, links_used, right_answers = asyncio.run(process_queries(queries))
    write_results(PATH_TO_CSV_FILE, PATH_TO_LOG_FILE, results, input_file, links_used,right_answers)


if __name__ == "__main__":
    main()