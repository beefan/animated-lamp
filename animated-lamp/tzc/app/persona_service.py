import json
import logging
import os
from typing import List, Dict, Any
from .models import SessionLocal, Persona
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

PERSONA_GENERATION_PROMPT = """
Generate exactly 50 diverse personas. Each persona must have a name, age, job, and personality description.
Ensure a wide range of ages (18-90), diverse professions, and various personality traits.
The output MUST be a valid JSON array of objects with the following keys: "name", "age", "job", "personality".

Example format:
[
  {"name": "Alice Smith", "age": 28, "job": "Software Engineer", "personality": "Introverted, analytical, and detail-oriented."},
  ...
]
"""

def generate_personas_with_gemini() -> List[Dict[str, Any]]:
    """
    Calls Gemini API to generate 50 diverse personas.
    """
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not set.")
        raise ValueError("GEMINI_API_KEY is not set.")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": PERSONA_GENERATION_PROMPT}
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
        }
    }

    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        content_text = data['candidates'][0]['content']['parts'][0]['text']
        personas = json.loads(content_text)
        
        if not isinstance(personas, list):
            raise ValueError(f"Gemini did not return a list. Type: {type(personas)}")
            
        return personas
    except Exception as e:
        logger.error(f"Failed to generate personas via Gemini: {e}")
        raise

def seed_personas():
    """
    Service function to generate and save 50 personas to the database.
    """
    db = SessionLocal()
    try:
        logger.info("Generating personas via Gemini...")
        persona_data = generate_personas_with_gemini()
        
        personas_to_add = []
        for p in persona_data:
            # Basic validation
            if not all(k in p for k in ("name", "age", "job", "personality")):
                logger.warning(f"Skipping invalid persona data: {p}")
                continue
                
            persona = Persona(
                name=p["name"],
                age=p["age"],
                job=p["job"],
                personality=p["personality"]
            )
            personas_to_add.append(persona)
        
        if not personas_to_add:
            logger.error("No valid personas generated.")
            return

        db.add_all(personas_to_add)
        db.commit()
        logger.info(f"Successfully seeded {len(personas_to_add)} personas.")
        return len(personas_to_add)
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding personas: {e}")
        raise
    finally:
        db.close()
