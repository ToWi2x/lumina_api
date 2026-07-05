from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import uuid
import asyncio
from typing import Dict, Optional

# Initialize the FastAPI application
app = FastAPI(
    title="Lumina API",
    description="Asynchronous AI Content Analysis Engine - Phase 1",
    version="0.1.0"
)

# --- Pydantic Schemas (Data Validation) ---
# Pydantic validates incoming JSON and ensures data types are strictly correct.
class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=10, description="The text content to be analyzed by the AI.")

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict] = None

# --- Mock Database ---
MOCK_DB: Dict[str, Dict] = {}

# --- Mock AI Processing Function ---
async def mock_ai_worker(task_id: str, text: str):
    """
    This simulates a background worker taking time to call an AI API.
    In a later phase, this function moves to a completely separate server.
    """
    # 1. Update status to processing
    MOCK_DB[task_id]["status"] = "Processing"
    
    # 2. Simulate a 5-second network delay (e.g., waiting for LLM response)
    # Using asyncio.sleep won't freeze the rest of our API!
    await asyncio.sleep(5) 
    
    # 3. Simulate the AI's structured JSON response
    mock_ai_result = {
        "sentiment": "positive" if "excellent" in text.lower() else "neutral",
        "word_count": len(text.split()),
        "urgency": "low",
        "summary": "Successfully analyzed text payload."
    }
    
    # 4. Save result to database and mark completed
    MOCK_DB[task_id]["status"] = "Completed"
    MOCK_DB[task_id]["result"] = mock_ai_result

# --- API Endpoints ---

@app.get("/health", tags=["System"])
async def health_check():
    """Returns the health status of the API."""
    return {"status": "ok", "message": "Lumina API is running."}

@app.post("/api/v1/analyze", response_model=TaskResponse, status_code=202, tags=["AI Analysis"])
async def analyze_text(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Receives text, creates a task, and instantly returns the task_id.
    """
    # 1. Generate a unique ID for this job
    task_id = str(uuid.uuid4())
    
    # 2. Save initial state to our mock database
    MOCK_DB[task_id] = {
        "task_id": task_id,
        "status": "Pending",
        "result": None
    }
    
    # 3. Offload the heavy AI work to a background task
    background_tasks.add_task(mock_ai_worker, task_id, request.text)
    
    return MOCK_DB[task_id]

@app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse, tags=["AI Analysis"])
async def get_task_status(task_id: str):
    """
    Checks the database for the status of a specific task using its ID.
    """
    if task_id not in MOCK_DB:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return MOCK_DB[task_id]