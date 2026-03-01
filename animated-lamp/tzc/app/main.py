from fastapi import FastAPI
from .models import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Survey Funky")

@app.get("/health")
def health_check():
    return {"status": "ok"}
