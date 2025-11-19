# import json
# import os
# from google import genai
# from google.genai import types
# from dotenv import load_dotenv

# # --- CRITICAL FIX: Ensure environment variables are loaded immediately ---
# load_dotenv() 

# # --- LLM Client Initialization ---
# API_KEY = os.environ.get("GEMINI_API_KEY", "")

# # Initialize client. 
# client = genai.Client(api_key=API_KEY)
# MODEL = 'gemini-2.5-flash'

# def is_client_initialized_properly():
#     """Checks if the client has a key or is in a mock environment."""
#     return bool(API_KEY)

# def generate_plan(quiz_question: str, data_url: str) -> dict:
#     """
#     Uses the LLM to convert a natural language quiz question into a structured, 
#     machine-executable JSON plan.
#     """
#     if not is_client_initialized_properly():
#         print("Warning: Using mock plan as API key is missing. Using mock data.")
#         return {
#             "action": "mock_sum", 
#             "data_url": data_url,
#             "file_type": "PDF",
#             "operation": "SUM",
#             "target_column": "value",
#             "page_criteria": "2",
#             "answer_type": "number"
#         }

#     system_prompt = (
#         "You are a Quiz Solving Agent. Your task is to analyze the quiz question and data URL, "
#         "and output a precise, structured JSON plan for a Python script to execute. "
#         "Infer the required operation (SUM, AVG, FILTER, VISUALIZE), the file type, "
#         "and any specific criteria (like a page number or column name). "
#         "The output MUST be a valid JSON object matching the defined schema."
#     )
    
#     json_schema = {
#         "type": "OBJECT",
#         "properties": {
#             "file_type": {"type": "STRING", "description": "Inferred type: CSV, JSON, PDF, or IMAGE."},
#             "data_url": {"type": "STRING", "description": "The URL of the data file."},
#             "operation": {"type": "STRING", "description": "Required operation: SUM, AVG, MAX, FILTER, VISUALIZE, or STRING_EXTRACT."},
#             "target_column": {"type": "STRING", "description": "Column name to operate on, or 'N/A' if non-tabular."},
#             "page_criteria": {"type": "STRING", "description": "Specific page number for PDF, or filtering text/condition, or 'N/A'."},
#             "answer_type": {"type": "STRING", "description": "Expected answer type: number, string, boolean, or base64_image."}
#         },
#         "required": ["file_type", "data_url", "operation", "target_column", "page_criteria", "answer_type"]
#     }
    
#     user_prompt = f"Quiz Question: \"{quiz_question}\" Data URL: \"{data_url}\""
    
#     try:
#         response = client.models.generate_content(
#             model=MODEL,
#             contents=[
#                 types.Content(role="system", parts=[types.Part.from_text(system_prompt)]),
#                 types.Content(role="user", parts=[types.Part.from_text(user_prompt)])
#             ],
#             config=types.GenerateContentConfig(
#                 response_mime_type="application/json",
#                 response_schema=json_schema
#             )
#         )
#         return json.loads(response.text)
    
#     except Exception as e:
#         print(f"LLM Planning Error: {e}")
#         raise ValueError("Failed to generate executable plan from LLM.")

# def extract_quiz_details(html_content: str) -> dict:
#     """Uses LLM to safely extract the question, data URL, and submit URL."""
#     if not is_client_initialized_properly():
#         print("Warning: Using mock extraction as API key is missing. Using mock data.")
#         return {
#             "question": "Q1. Download file. What is the sum of 'value' column in table on page 2?",
#             "data_url": "https://example.com/data.pdf",
#             "submit_url": "https://example.com/submit"
#         }
        
#     system_prompt = (
#         "Analyze the provided HTML content. Extract the full natural language quiz question, "
#         "the URL of the data file (from any <a> tag), and the URL where the answer must be posted "
#         "(from the 'Post your answer to' instruction). Return the results in the exact JSON format."
#     )
    
#     json_schema = {
#         "type": "OBJECT",
#         "properties": {
#             "question": {"type": "STRING"},
#             "data_url": {"type": "STRING"},
#             "submit_url": {"type": "STRING"}
#         },
#         "required": ["question", "data_url", "submit_url"]
#     }
    
#     user_prompt = f"HTML Content:\n---\n{html_content}\n---"

#     try:
#         response = client.models.generate_content(
#             model=MODEL,
#             contents=[
#                 types.Content(role="system", parts=[types.Part.from_text(system_prompt)]),
#                 types.Content(role="user", parts=[types.Part.from_text(user_prompt)])
#             ],
#             config=types.GenerateContentConfig(
#                 response_mime_type="application/json",
#                 response_schema=json_schema
#             )
#         )
#         return json.loads(response.text)
#     except Exception as e:
#         print(f"LLM Extraction Error: {e}")
#         raise ValueError("Failed to extract quiz details from page using LLM.")

######################################################################################################
# import json
# import os
# from google import genai
# from google.genai import types
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv() 

# API_KEY = os.environ.get("GEMINI_API_KEY", "")
# client = genai.Client(api_key=API_KEY)
# MODEL = 'gemini-2.5-flash'

# def is_client_initialized_properly():
#     return bool(API_KEY)

# def generate_plan(quiz_question: str, data_url: str) -> dict:
#     if not is_client_initialized_properly():
#         return {"action": "mock", "file_type": "PDF", "operation": "SUM", "target_column": "value", "page_criteria": "N/A", "answer_type": "number"}

#     # --- STRATEGY: PREFER VISUALIZATION FOR VAGUE DATA ---
#     # This matches the snippet you requested.
#     system_prompt = (
#         "You are a Quiz Solving Agent. Analyze the request and output a JSON plan.\n"
#         "RULES:\n"
        
#         "1. Use 'SUM' or 'AVG' only if the question specifically implies calculation or aggregation.\n"
#         "2. For PDF text, default to STRING_EXTRACT.\n"
#         "3. If the question is vague, calculate the SUM.\n"
#         "4. If the data type is unclear, prefer VISUALIZE.\n"
#     )
    
#     json_schema = {
#         "type": "OBJECT",
#         "properties": {
#             "file_type": {"type": "STRING", "enum": ["CSV", "JSON", "PDF"]},
#             "data_url": {"type": "STRING"},
#             "operation": {"type": "STRING", "enum": ["SUM", "AVG", "MAX", "FILTER", "VISUALIZE", "STRING_EXTRACT"]},
#             "target_column": {"type": "STRING"},
#             "page_criteria": {"type": "STRING"},
#             "answer_type": {"type": "STRING"}
#         },
#         "required": ["file_type", "data_url", "operation", "target_column", "page_criteria", "answer_type"]
#     }
    
#     # Combined prompt to handle role requirements
#     full_prompt = f"SYSTEM:\n{system_prompt}\n\nUSER:\nQuestion: \"{quiz_question}\" Data URL: \"{data_url}\""
    
#     try:
#         response = client.models.generate_content(
#             model=MODEL,
#             contents=[types.Content(role="user", parts=[types.Part(text=full_prompt)])],
#             config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=json_schema)
#         )
#         return json.loads(response.text)
#     except Exception as e:
#         print(f"LLM Planning Error: {e}")
#         return {"file_type": "N/A", "data_url": "", "operation": "N/A", "target_column": "N/A", "page_criteria": "N/A", "answer_type": "N/A"}

# def extract_quiz_details(html_content: str) -> dict:
#     if not is_client_initialized_properly():
#         return {"question": "Mock", "data_url": "", "submit_url": ""}
        
#     system_prompt = "Extract 'question', 'data_url', and 'submit_url' from the HTML. Return JSON."
    
#     json_schema = {
#         "type": "OBJECT",
#         "properties": {
#             "question": {"type": "STRING"},
#             "data_url": {"type": "STRING"},
#             "submit_url": {"type": "STRING"}
#         },
#         "required": ["question", "data_url", "submit_url"]
#     }
    
#     full_prompt = f"SYSTEM:\n{system_prompt}\n\nUSER:\nHTML:\n{html_content}"

#     try:
#         response = client.models.generate_content(
#             model=MODEL,
#             contents=[types.Content(role="user", parts=[types.Part(text=full_prompt)])],
#             config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=json_schema)
#         )
#         return json.loads(response.text)
#     except Exception as e:
#         print(f"LLM Extraction Error: {e}")
#         return {"question": "Error", "data_url": "", "submit_url": ""}
    
import json
import os
import time
import random
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv() 
API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY)
MODEL = 'gemini-2.5-flash'

def is_client_initialized_properly():
    return bool(API_KEY)

def generate_with_retry(model, contents, config, retries=5, initial_delay=2):
    delay = initial_delay
    for attempt in range(retries):
        try:
            return client.models.generate_content(model=model, contents=contents, config=config)
        except Exception as e:
            error_str = str(e)
            if any(code in error_str for code in ["503", "429", "500"]):
                print(f"[LLM] API Busy. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2 + random.uniform(0, 1)
            else:
                raise e
    raise Exception("Max retries exceeded.")

def generate_plan(quiz_question: str, data_url: str) -> dict:
    if not is_client_initialized_properly():
        return {"action": "mock", "file_type": "PDF", "operation": "SUM", "target_column": "value", "page_criteria": "N/A", "answer_type": "number"}

    # Rules to prevent "Wrong sum" or "Cannot visualize" errors
    system_prompt = (
        "You are a Quiz Solving Agent. Analyze the request and output a JSON plan.\n"
        "RULES:\n"
        "1. If the question is vague (e.g. 'Analyze data', 'What is the answer?'), DEFAULT TO OPERATION: 'SUM' on the last numeric column.\n"
        "2. ONLY choose 'VISUALIZE' if the user explicitly asks for a chart, plot, or image.\n"
        "3. For CSVs, if no specific column is named, target the LAST numeric column.\n"
        "4. For PDF text, default to STRING_EXTRACT unless asked to sum numbers."
    )
    
    json_schema = {
        "type": "OBJECT",
        "properties": {
            "file_type": {"type": "STRING", "enum": ["CSV", "JSON", "PDF"]},
            "data_url": {"type": "STRING"},
            "operation": {"type": "STRING", "enum": ["SUM", "AVG", "MAX", "FILTER", "VISUALIZE", "STRING_EXTRACT"]},
            "target_column": {"type": "STRING"},
            "page_criteria": {"type": "STRING"},
            "answer_type": {"type": "STRING"}
        },
        "required": ["file_type", "data_url", "operation", "target_column", "page_criteria", "answer_type"]
    }
    
    full_prompt = f"SYSTEM:\n{system_prompt}\n\nUSER:\nQuestion: \"{quiz_question}\" Data URL: \"{data_url}\""
    
    try:
        response = generate_with_retry(
            model=MODEL,
            contents=[types.Content(role="user", parts=[types.Part(text=full_prompt)])],
            config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=json_schema)
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"LLM Planning Error: {e}")
        return {"file_type": "N/A", "data_url": "", "operation": "N/A", "target_column": "N/A", "page_criteria": "N/A", "answer_type": "N/A"}

def extract_quiz_details(html_content: str) -> dict:
    if not is_client_initialized_properly():
        return {"question": "Mock", "data_url": "", "submit_url": ""}
        
    system_prompt = "Extract 'question', 'data_url', and 'submit_url' from the HTML. Return JSON."
    
    json_schema = {
        "type": "OBJECT",
        "properties": {
            "question": {"type": "STRING"},
            "data_url": {"type": "STRING"},
            "submit_url": {"type": "STRING"}
        },
        "required": ["question", "data_url", "submit_url"]
    }
    
    full_prompt = f"SYSTEM:\n{system_prompt}\n\nUSER:\nHTML:\n{html_content}"

    try:
        response = generate_with_retry(
            model=MODEL,
            contents=[types.Content(role="user", parts=[types.Part(text=full_prompt)])],
            config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=json_schema)
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"LLM Extraction Error: {e}")
        return {"question": "Error", "data_url": "", "submit_url": ""}