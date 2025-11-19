import time
import json
import requests
import os
import threading
from fastapi import FastAPI, Request, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv

# Import the orchestrator function
from solver import solve_quiz

load_dotenv()

app = FastAPI()

# --- Configuration (Read from .env) ---
STUDENT_SECRET = os.getenv("STUDENT_SECRET")
# Assuming you set this in the environment or passed it in the JWT decoded email
STUDENT_EMAIL = "23f3003307@ds.study.iitm.ac.in" 
MAX_TIME_SECONDS = 175 # 3 minutes total

class QuizPayload(BaseModel):
    email: str
    secret: str
    url: str

# -------------------------------
# CORE SOLVER LOOP (Runs in background)
# -------------------------------

def quiz_solver_loop(data: QuizPayload, start_time: float):
    """
    This function runs in a background thread/process and handles the full quiz chain.
    """
    current_url = data.url
    
    print(f"\n--- Starting Quiz Chain (Initial URL: {current_url}) ---")
    
    while True:
        elapsed_time = time.time() - start_time
        
        if elapsed_time > MAX_TIME_SECONDS:
            print(f"--- Timeout reached after {elapsed_time:.2f}s. Halting. ---")
            break

        print(f"\n--- Starting Quiz: {current_url} (Elapsed: {elapsed_time:.2f}s) ---")
        
        # Calls the orchestrator to solve one quiz and submit the answer
        result = solve_quiz(
            current_url=current_url, 
            email=STUDENT_EMAIL, 
            secret=STUDENT_SECRET,
            start_time=start_time
        )

        # Check for correctness and next URL
        if result.get("correct") and result.get("url"):
            # Correct and received next URL
            current_url = result["url"]
            print(f"Status: Correct. Proceeding to: {current_url}")
            continue

        if not result.get("correct") and result.get("url"):
            # Incorrect but received next URL (Option to skip)
            current_url = result["url"]
            print(f"Status: Incorrect. Skipping to: {current_url}")
            continue

        if result.get("correct") is True and not result.get("url"):
            # Correct, no new URL - Quiz chain finished
            print("Status: Correct. Quiz chain completed successfully!")
            break
            
        if result.get("correct") is False and not result.get("url"):
            # Incorrect, no new URL - The problem is in the current quiz.
            # Here you would implement LLM self-correction/re-submission logic.
            print(f"Status: Incorrect. Reason: {result.get('reason')}. Halting.")
            break
            
        print("Status: Loop terminated unexpectedly.")
        break


# -------------------------------
# MAIN ENDPOINT
# -------------------------------

@app.post("/")
async def quiz_handler(data: QuizPayload, background_tasks: BackgroundTasks):
    
    # 1. Verification
    if data.secret != STUDENT_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid secret")
    
    # 2. Check if the provided email matches the hardcoded student email
    if data.email != STUDENT_EMAIL:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email mismatch")

    # The entire process must be non-blocking. 
    # Use a thread for the long-running process to avoid blocking the main async event loop.
    
    # We pass the start_time (current time) to the background process 
    # so it can manage its own 3-minute deadline.
    start_time = time.time()
    
    # Delegate the long-running quiz loop to a thread
    background_tasks.add_task(quiz_solver_loop, data, start_time)

    # 3. Return immediate HTTP 200 acknowledgment
    return {"status": "Solver process initiated in background. Check logs for progress."}