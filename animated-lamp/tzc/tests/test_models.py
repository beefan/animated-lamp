import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from ..app.models import Base, Survey, Persona, SurveyResult, SurveyStatus

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_survey_funky.db"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_sqlite_wal_mode(db_session):
    result = db_session.execute("PRAGMA journal_mode").fetchone()
    assert result[0].lower() == "wal"
    result = db_session.execute("PRAGMA synchronous").fetchone()
    # 1 is NORMAL, 2 is FULL
    assert result[0] == 1

def test_survey_creation(db_session):
    survey = Survey(
        question="What is your favorite color?",
        choices=["Red", "Blue", "Green"],
        status=SurveyStatus.PENDING
    )
    db_session.add(survey)
    db_session.commit()
    db_session.refresh(survey)
    
    assert survey.id is not None
    assert survey.status == SurveyStatus.PENDING
    assert len(survey.choices) == 3

def test_persona_creation(db_session):
    persona = Persona(
        name="Alice",
        age=30,
        job="Engineer",
        personality="Analytical"
    )
    db_session.add(persona)
    db_session.commit()
    db_session.refresh(persona)
    
    assert persona.id is not None
    assert persona.name == "Alice"

def test_survey_result_unique_constraint(db_session):
    survey = Survey(question="Q1", choices=["A", "B"])
    persona = Persona(name="P1", age=25, job="J1", personality="Pers1")
    db_session.add_all([survey, persona])
    db_session.commit()
    
    result1 = SurveyResult(survey_id=survey.id, persona_id=persona.id, choice_index=0)
    db_session.add(result1)
    db_session.commit()
    
    result2 = SurveyResult(survey_id=survey.id, persona_id=persona.id, choice_index=1)
    db_session.add(result2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
