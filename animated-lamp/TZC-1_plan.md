# TZC-1: Scaffold FastAPI & Database Models Implementation Plan

## Overview
Initialize the FastAPI project structure with SQLite (WAL mode) and core models for the Survey Funky app.

## Project Structure
```
tzc/
├── alembic/            # Migrations (if needed)
├── src/
│   ├── __init__.py
│   ├── main.py         # App entry point
│   ├── database.py     # Engine & Session setup (WAL mode)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py     # Declarative Base
│   │   ├── survey.py   # Survey model & Enum
│   │   ├── persona.py  # Persona model
│   │   └── result.py   # SurveyResult model & UniqueConstraint
│   └── schemas/        # Pydantic models (optional for TZC-1)
└── tests/
    ├── __init__.py
    ├── conftest.py     # Test DB setup
    └── test_models.py  # Model & Constraint verification
```

## Database Configuration (WAL Mode)
To ensure SQLite handles concurrent reads/writes from FastAPI and Celery:
```python
from sqlalchemy import create_engine, event

engine = create_engine("sqlite:///./tzc.db", connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()
```

## Model Definitions

### Survey
- `id`: UUID (Primary Key)
- `question`: String
- `choices`: JSON (List of 4 strings)
- `status`: Enum (`pending`, `processing`, `completed`, `failed`)
- `created_at`: DateTime

### Persona
- `id`: Integer (Primary Key)
- `name`: String
- `age`: Integer
- `job`: String
- `personality`: Text
- `created_at`: DateTime

### SurveyResult
- `id`: Integer (Primary Key)
- `survey_id`: UUID (FK -> Survey.id)
- `persona_id`: Integer (FK -> Persona.id)
- `choice_index`: Integer
- `reasoning`: Text
- `created_at`: DateTime
- **Constraint**: `UniqueConstraint('survey_id', 'persona_id', name='uix_survey_persona')`

## Test Cases
1. **WAL Verification**: Connect to DB and check `PRAGMA journal_mode`.
2. **Enum Verification**: Ensure `Survey` only accepts valid status values.
3. **Constraint Verification**: Attempt to insert duplicate `(survey_id, persona_id)` into `SurveyResult` and verify `IntegrityError`.
4. **Model Creation**: Verify all models can be instantiated and saved.
