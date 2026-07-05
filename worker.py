from celery import Celery
import time
from database import SessionLocal
import models

# 1. Initialize Celery connect to Upstash Redis database
celery_app = Celery(
    "lumina_worker",
    broker="rediss://default:gQAAAAAAAVAGAAIgcDEzNzc4NjZkMDllNDA0ODUwOGMzNTZmNzNlMDFkZDQ1Yg@becoming-dinosaur-86022.upstash.io:6379?ssl_cert_reqs=CERT_NONE",  # <--- PASTE YOUR URL HERE
    backend="rediss://default:gQAAAAAAAVAGAAIgcDEzNzc4NjZkMDllNDA0ODUwOGMzNTZmNzNlMDFkZDQ1Yg@becoming-dinosaur-86022.upstash.io:6379?ssl_cert_reqs=CERT_NONE"  
)

# 2. Define the background task
# standard synchronous python (time.sleep) here because Celery 
# runs on entirely different threads from FastAPI.
@celery_app.task(name="analyze_text_task")
def analyze_text_task(task_id: str, text: str):
    db = SessionLocal()
    
    # 1. Update status to Processing
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        task.status = "Processing"
        db.commit()
    
    # 2. Simulate AI delay
    time.sleep(5) 
    
    # 3. Simulate the AI's structured response
    mock_ai_result = {
        "sentiment": "positive" if "excellent" in text.lower() else "neutral",
        "word_count": len(text.split()),
        "urgency": "low",
        "summary": "Processed asynchronously by Celery Background Worker!"
    }
    
    # 4. Save result to database
    if task:
        task.status = "Completed"
        task.result = mock_ai_result
        db.commit()
        
    db.close()