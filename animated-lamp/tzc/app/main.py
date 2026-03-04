import os
from fastapi import FastAPI, Header, HTTPException, status
from .models import engine, Base, SessionLocal
from .worker import generate_personas_task

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Survey Funky")

from .persona_service import seed_personas, generate_personas_with_gemini

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "super-secret-admin-token")

@app.post("/admin/seed-personas", status_code=status.HTTP_202_ACCEPTED)
def seed_personas_endpoint(x_admin_token: str = Header(None)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin token",
        )
    
    task = generate_personas_task.delay()
    return {"task_id": task.id}

@app.post("/personas/generate")
def trigger_persona_generation():
    """
    Endpoint to trigger persona generation.
    In a real app, this should probably be a Celery task.
    """
    count = seed_personas()
    return {"message": f"Successfully generated and seeded {count} personas."}

@app.get("/health")
def health_check():
    return {"status": "ok"}
