Lumina: Asynchronous AI Content Analysis Engine

Lumina is a high-performance, asynchronous REST API designed to process, analyze, and route unstructured text payloads using background workers.

Built to demonstrate modern microservice architecture, Lumina solves the problem of API timeouts during heavy inference by offloading HTTP requests to a distributed background task queue.

🚀 Architecture

Ingress (FastAPI): A high-speed async API that receives text payloads. It immediately returns a task_id without blocking the main thread.

Message Broker (Redis - Upstash): Acts as the intermediary, securely holding tasks until a worker is ready.

Background Workers (Celery): Independent Python processes that consume tasks from Redis, simulate heavy processing, and parse the results.

Data Layer (SQLAlchemy & SQLite): A database layer that stores the initial payloads and the finalized analysis (Sentiment, Word Count, Urgency).

🔄 The Data Flow

Client -> POST /api/v1/analyze {"text": "..."}
  |
  |--> FastAPI validates data (Pydantic)
  |--> FastAPI saves "Pending" status to DB (SQLAlchemy)
  |--> FastAPI pushes Task to Redis
  |<-- FastAPI returns HTTP 202 Accepted {"task_id": "123"}
  
[Background Process]
Celery Worker pulls Task from Redis
  |--> Worker processes text (Heavy Lifting)
  |--> Worker parses response into structured JSON
  |--> Worker updates DB record to "Completed" (SQLAlchemy)

Client -> GET /api/v1/tasks/123
  |<-- FastAPI queries DB and returns Final Analysis


💻 API Endpoints

Method

Endpoint

Description

POST

/api/v1/analyze

Submit text for asynchronous AI analysis. Returns a task_id.

GET

/api/v1/tasks/{task_id}

Poll the status of a specific task. Returns Pending, Processing, or the completed JSON data.

GET

/health

Check the health of the API.