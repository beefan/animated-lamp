import enum
import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, JSON, Enum, DateTime, ForeignKey, UniqueConstraint, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class SurveyStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Survey(Base):
    __tablename__ = "surveys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(String, nullable=False)
    choices = Column(JSON, nullable=False)
    status = Column(Enum(SurveyStatus), default=SurveyStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    results = relationship("SurveyResult", back_populates="survey")

class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    job = Column(String, nullable=False)
    personality = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    results = relationship("SurveyResult", back_populates="persona")

class SurveyResult(Base):
    __tablename__ = "survey_results"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(String(36), ForeignKey("surveys.id"), nullable=False)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False)
    choice_index = Column(Integer, nullable=False)
    reasoning = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    survey = relationship("Survey", back_populates="results")
    persona = relationship("Persona", back_populates="results")

    __table_args__ = (
        UniqueConstraint("survey_id", "persona_id", name="uix_survey_persona"),
    )

# Database Configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./survey_funky.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
