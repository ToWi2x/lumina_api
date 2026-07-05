from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import uuid
from typing import Dict, Optional

# Imports for Database
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models

# --- Phase 3: Import our Celery Task! ---
from worker import analyze_text_task

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lumina API",
    description="Asynchronous AI Content Analysis Engine - Phase 3 (Celery & Redis)",
    version="0.3.0"
)

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=10, description="The text content to be analyzed by the AI.")

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "message": "Lumina API Phase 3 is running."}

@app.post("/api/v1/analyze", response_model=TaskResponse, status_code=202, tags=["AI Analysis"])
async def analyze_text(request: AnalyzeRequest, db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())
    
    # 1. Save "Pending" state to Database
    new_task = models.Task(
        id=task_id,
        status="Pending",
        original_text=request.text
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task) 
    
    # 2. The Magic: Push the job to Redis/Celery!
    # The .delay() command means "Don't run this now, put it in the queue!"
    analyze_text_task.delay(task_id, request.text)
    
    return {"task_id": new_task.id, "status": new_task.status, "result": new_task.result}

@app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse, tags=["AI Analysis"])
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task.id, "status": task.status, "result": task.result}