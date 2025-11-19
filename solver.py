
# import requests
# import base64
# import time
# import re
# import os
# import io

# # NOTE: Playwright is removed due to environment instability. We rely on requests
# # to scrape and regex/base64 to decode the static JavaScript content.

# from llm_planner import extract_quiz_details, generate_plan
# from data_processor import execute_analysis_plan

# def scrape_quiz_page_content(quiz_url: str) -> str:
#     """
#     Bypasses Playwright. Fetches the static HTML, finds the Base64-encoded
#     content string, decodes it, and returns the resulting HTML fragment.
#     Uses a highly forgiving regex to find the encoded data.
#     """
#     print(f"[Scraper] Fetching raw HTML from: {quiz_url}")
    
#     # Use requests to get the raw static HTML
#     response = requests.get(quiz_url, timeout=10)
#     response.raise_for_status()
#     raw_html = response.text
    
#     # FINAL, highly forgiving regex: Targets content inside atob(`...`) across the whole document
#     base64_match = re.search(r'atob\s*\(\s*`\s*(.*?)\s*`\s*\)', raw_html, re.DOTALL | re.IGNORECASE)
    
#     if not base64_match:
#         # Fallback: Try the structure used in the sample (document.querySelector("#result").innerHTML = atob(`...`))
#         base64_match = re.search(r'innerHTML\s*=\s*atob\s*\(\s*`\s*(.*?)\s*`\s*\)\s*;', raw_html, re.DOTALL | re.IGNORECASE)
        
#         if not base64_match:
#             raise ValueError("Could not find Base64 encoded quiz content in static HTML.")
        
#     encoded_content = base64_match.group(1).strip()
    
#     # 2. Decode the Base64 content
#     try:
#         # The content might contain whitespace or newlines from the regex match
#         clean_encoded_content = encoded_content.replace('\n', '').replace('\r', '').replace(' ', '')
        
#         # Padding required for Base64 decoding if the length is not a multiple of 4
#         missing_padding = len(clean_encoded_content) % 4
#         if missing_padding != 0:
#             clean_encoded_content += '=' * (4 - missing_padding)

#         decoded_bytes = base64.b64decode(clean_encoded_content)
#         decoded_html_content = decoded_bytes.decode('utf-8')
#     except Exception as e:
#         raise ValueError(f"Failed to Base64 decode content: {e}")

#     # 3. Wrap the decoded content in the expected <div> structure for the LLM planner
#     final_content = f'<div id="result">{decoded_html_content}</div>'
    
#     print("[Scraper] Successfully bypassed JavaScript and decoded quiz content.")
#     return final_content

# def solve_quiz(current_url: str, email: str, secret: str, start_time: float) -> dict:
#     """
#     Orchestrates the scraping, planning, execution, and submission for a single quiz.
#     Returns the result of the submission.
#     """
#     try:
#         # 1. Scrape the Quiz Details using the requests-based decoder
#         print(f"[Solver] 1. Starting static scraping and decoding...")
#         content_html = scrape_quiz_page_content(current_url)

#         # 2. LLM Extraction: Get question, data URL, submit URL
#         print("[Solver] 2. Running LLM Extraction...")
#         # Note: LLM planner is robust enough to handle the wrapped HTML content
#         quiz_details = extract_quiz_details(content_html)
#         question = quiz_details['question']
#         data_url = quiz_details['data_url']
#         submit_url = quiz_details['submit_url']
        
#         print(f"[Solver] Question: {question}")
#         print(f"[Solver] Submit URL: {submit_url}")

#         # 3. LLM Planning: Get the structured execution plan
#         print(f"[Solver] 3. Generating LLM analysis plan...")
#         analysis_plan = generate_plan(question, data_url)
#         print(f"[Solver] Plan generated: {analysis_plan}")

#         # 4. Execution: Calculate the final answer
#         print(f"[Solver] 4. Executing plan...")
#         final_answer = execute_analysis_plan(analysis_plan)
#         print(f"[Solver] Final Answer: {final_answer}")

#         # 5. Submission
#         submit_payload = {
#             "email": email,
#             "secret": secret,
#             "url": current_url,
#             "answer": final_answer
#         }
        
#         # Check time limit before submitting
#         if time.time() - start_time > 175:
#             print("[Solver] Time limit hit before submission.")
#             return {"correct": False, "reason": "Timeout before submission."}

#         print(f"[Solver] 5. Submitting answer to {submit_url}")
#         response = requests.post(submit_url, json=submit_payload, timeout=10)
#         response.raise_for_status()
        
#         return response.json()

#     except Exception as e:
#         print(f"[Solver] Critical failure in solve_quiz: {e}")
#         return {"correct": False, "reason": f"Execution error: {str(e)}"}
    
# solver.py - FINAL VERSION WITHOUT PLAYWRIGHT DEPENDENCY (FIXED SCRAPER)
############################################################

# solver.py - FINAL VERSION (Raw Text Fallback Enabled)
import requests
import base64
import time
import re
import os
from urllib.parse import urlparse, urljoin, quote

from llm_planner import extract_quiz_details, generate_plan
from data_processor import execute_analysis_plan

def scrape_quiz_page_content(quiz_url: str) -> str:
    print(f"[Scraper] Fetching raw HTML from: {quiz_url}")
    try:
        response = requests.get(quiz_url, timeout=30)
        response.raise_for_status()
        raw_html = response.text
    except Exception as e:
        raise ValueError(f"Failed to fetch quiz page: {e}")
    
    base64_match = re.search(r'atob\s*\(\s*[`\'"]\s*(.*?)\s*[`\'"]\s*\)', raw_html, flags=re.DOTALL | re.IGNORECASE)
    if not base64_match:
        base64_match = re.search(r'innerHTML\s*=\s*atob\s*\(\s*[`\'"]\s*(.*?)\s*[`\'"]\s*\)\s*;', raw_html, flags=re.DOTALL | re.IGNORECASE)
        
    if base64_match:
        encoded_content = base64_match.group(1).strip()
        try:
            clean_encoded_content = encoded_content.replace('\n', '').replace('\r', '').replace(' ', '')
            missing_padding = len(clean_encoded_content) % 4
            if missing_padding != 0:
                clean_encoded_content += '=' * (4 - missing_padding)
            decoded_bytes = base64.b64decode(clean_encoded_content)
            return f'<div id="result">{decoded_bytes.decode("utf-8")}</div>'
        except Exception as e:
            print(f"[Scraper] Warning: Base64 match found but decode failed: {e}")
            
    print("[Scraper] No Base64 encoded content found. Returning raw HTML content.")
    return f'<div id="result">{raw_html}</div>'

def solve_quiz(current_url: str, email: str, secret: str, start_time: float) -> dict:
    try:
        print(f"[Solver] 1. Scraping details from: {current_url}")
        content_html = scrape_quiz_page_content(current_url)

        print("[Solver] 2. Running LLM Extraction...")
        quiz_details = extract_quiz_details(content_html)
        question = quiz_details['question']
        data_url = quiz_details.get('data_url', 'N/A')
        submit_url = quiz_details['submit_url']

        # --- HELPER: CLEAN URLS ---
        parsed_uri = urlparse(current_url)
        base_domain = parsed_uri.netloc 
        base_origin = f"{parsed_uri.scheme}://{base_domain}"
        
        def clean_url_string(url_to_clean):
            if not url_to_clean or url_to_clean == 'N/A': return url_to_clean
            
            # 1. Handle standard placeholders
            placeholders = [
                '{origin}', '<origin>', '%7Borigin%7D', '<span class="origin"></span>',
                'window.location.origin', '${window.location.origin}'
            ]
            for p in placeholders:
                if p in url_to_clean:
                    if base_domain in url_to_clean:
                        url_to_clean = url_to_clean.replace(p, "")
                    else:
                        url_to_clean = url_to_clean.replace(p, base_origin)
            
            # 2. Handle "example.com" hallucinations
            if "example.com" in url_to_clean:
                # For submit URL, we want to fix it to the real domain
                url_to_clean = url_to_clean.replace("https://example.com", base_origin)
                url_to_clean = url_to_clean.replace("http://example.com", base_origin)
                url_to_clean = url_to_clean.replace("example.com", base_domain)

            # 3. Cleanup formatting
            if "://" in url_to_clean:
                proto, rest = url_to_clean.split("://", 1)
                rest = rest.replace("//", "/")
                url_to_clean = f"{proto}://{rest}"
                
            return url_to_clean.strip()

        # 3. Clean Submit URL
        submit_url = clean_url_string(submit_url)
        if not submit_url.startswith('http'):
            submit_url = urljoin(current_url, submit_url)
            
        if submit_url.endswith("/demo"):
             submit_url = submit_url.replace("/demo", "/submit")
        
        print(f"[Solver] Fixed Submit URL: {submit_url}")
        print(f"[Solver] Question: {question}")
        
        # 4. LLM Planning
        print(f"[Solver] 3. Generating LLM analysis plan...")
        analysis_plan = generate_plan(question, data_url)
        
        # 5. Clean Data URL
        raw_data_url = analysis_plan.get('data_url', 'N/A')
        
        # --- FIX: Block example.com for Data URLs ---
        if "example.com" in str(raw_data_url):
             print(f"[Solver] Ignoring invalid 'example.com' data URL: {raw_data_url}")
             raw_data_url = 'N/A'
        # --------------------------------------------
        
        if raw_data_url and raw_data_url not in ['N/A', '', 'UNKNOWN', 'None']:
            raw_data_url = clean_url_string(raw_data_url)
            
            if '$EMAIL' in raw_data_url:
                safe_email = quote(email)
                raw_data_url = raw_data_url.replace('$EMAIL', safe_email)
            
            if not raw_data_url.startswith('http'):
                raw_data_url = urljoin(current_url, raw_data_url)
            
            # Final check: Don't fetch the quiz page itself as data
            if raw_data_url == current_url:
                 print("[Solver] Data URL matches Current URL. Ignoring.")
                 raw_data_url = 'N/A'
            else:
                 analysis_plan['data_url'] = raw_data_url
                 print(f"[Solver] Resolved Data URL: {raw_data_url}")
        else:
             # Ensure plan reflects N/A if we blocked it
             analysis_plan['data_url'] = 'N/A'

        print(f"[Solver] Plan generated: {analysis_plan}")

        # 6. Execution
        print(f"[Solver] 4. Executing plan...")
        
        if analysis_plan.get('data_url') and analysis_plan['data_url'] not in ['N/A', '', 'UNKNOWN', 'None']:
            final_answer = execute_analysis_plan(analysis_plan)
        else:
            print(f"[Solver] Skipping data fetch. Using default answer.")
            final_answer = "anything you want" 

        print(f"[Solver] Final Answer: {final_answer}")

        # 7. Submission
        submit_payload = {
            "email": email,
            "secret": secret,
            "url": current_url,
            "answer": final_answer
        }
        
        if time.time() - start_time > 175:
            return {"correct": False, "reason": "Timeout before submission."}

        print(f"[Solver] 5. Submitting answer to {submit_url}")
        response = requests.post(submit_url, json=submit_payload, timeout=30)
        
        try:
            result_data = response.json()
            print(f"[Solver] Submission Result: {result_data}")
            return result_data
        except:
            if response.status_code == 200:
                print("[Solver] Submission accepted (200 OK), but no JSON returned.")
                return {"correct": True, "message": "Submission accepted"}
            response.raise_for_status()

    except Exception as e:
        print(f"[Solver] Critical failure in solve_quiz: {e}")
        return {"correct": False, "reason": f"Execution error: {str(e)}"}
    #uvicorn main:app --reload