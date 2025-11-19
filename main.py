
import time
import os
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv
from solver import solve_quiz

# Ensure .env is loaded
load_dotenv() 

app = FastAPI()

# --- Configuration ---
STUDENT_SECRET = os.getenv("STUDENT_SECRET")
STUDENT_EMAIL = "23f3003307@ds.study.iitm.ac.in" 
MAX_TIME_SECONDS = 175

class QuizPayload(BaseModel):
    email: str
    secret: str
    url: str

# -------------------------------
# CORE SOLVER LOOP (Runs in background)
# -------------------------------
def quiz_solver_loop(data: QuizPayload, start_time: float):
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
            current_url = result["url"]
            print(f"Status: Correct. Proceeding to: {current_url}")
            continue

        if not result.get("correct") and result.get("url"):
            current_url = result["url"]
            print(f"Status: Incorrect. Skipping to: {current_url}")
            continue

        if result.get("correct") is True and not result.get("url"):
            print("Status: Correct. Quiz chain completed successfully!")
            break
            
        if result.get("correct") is False and not result.get("url"):
            print(f"Status: Incorrect. Reason: {result.get('reason')}. Halting.")
            break
            
        print("Status: Loop terminated unexpectedly.")
        break


# -------------------------------
# GET HEALTH CHECK (New Endpoint!)
# -------------------------------
@app.get("/")
def health_check():
    """
    Returns a simple message when a browser or health checker accesses the root URL.
    """
    return {
        "status": "Online and Ready",
        "service": "LLM Quiz Solver API",
        "instructions": "Send POST request to this URL with email, secret, and quiz URL."
    }

# -------------------------------
# MAIN POST ENDPOINT
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
    start_time = time.time()
    
    # Delegate to Background Task
    background_tasks.add_task(quiz_solver_loop, data, start_time)

    # 3. Return immediate HTTP 200 acknowledgment
    return {"status": "Solver process initiated in background. Check logs for progress."}
    
