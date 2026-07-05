from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
import uuid
import asyncio
from typing import Dict, Optional

# --- New Imports for Database ---
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models

# 1. Create the database tables automatically 
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lumina API",
    description="Asynchronous AI Content Analysis Engine - Phase 2",
    version="0.2.0"
)

# --- Pydantic Schemas ---
class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=10, description="The text content to be analyzed by the AI.")

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict] = None

# --- Database Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Background Worker ---
async def mock_ai_worker(task_id: str, text: str):
    # Open a fresh database session for the background task
    db = SessionLocal()
    
    # 1. Get the task from the DB
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        task.status = "Processing"
        db.commit() # Save changes to DB
    
    # 2. Simulate network delay (5 seconds)
    await asyncio.sleep(5) 
    
    # 3. Simulate the AI's response
    mock_ai_result = {
        "sentiment": "positive" if "excellent" in text.lower() else "neutral",
        "word_count": len(text.split()),
        "urgency": "low",
        "summary": "Successfully analyzed text payload."
    }
    
    # 4. Save result to database
    if task:
        task.status = "Completed"
        task.result = mock_ai_result
        db.commit()
    
    db.close()

# --- API Endpoints ---

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "message": "Lumina API Database is running."}

@app.post("/api/v1/analyze", response_model=TaskResponse, status_code=202, tags=["AI Analysis"])
async def analyze_text(request: AnalyzeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())
    
    # 1. Create a new DB row
    new_task = models.Task(
        id=task_id,
        status="Pending",
        original_text=request.text
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task) 
    
    # 2. Offload work to the background
    background_tasks.add_task(mock_ai_worker, task_id, request.text)
    
    return {"task_id": new_task.id, "status": new_task.status, "result": new_task.result}

@app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse, tags=["AI Analysis"])
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    # Query the database
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return {"task_id": task.id, "status": task.status, "result": task.result}