import sys
import os
sys.path.append(os.getcwd())
import unittest
import uuid
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from tzc.app.models import Base, Survey, Persona, SurveyResult, SurveyStatus

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_survey_funky_unittest.db"

class TestModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )
        
        @event.listens_for(cls.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

        Base.metadata.create_all(bind=cls.engine)
        cls.Session = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=cls.engine)
        if os.path.exists("./test_survey_funky_unittest.db"):
            os.remove("./test_survey_funky_unittest.db")
        if os.path.exists("./test_survey_funky_unittest.db-shm"):
            os.remove("./test_survey_funky_unittest.db-shm")
        if os.path.exists("./test_survey_funky_unittest.db-wal"):
            os.remove("./test_survey_funky_unittest.db-wal")

    def test_sqlite_wal_mode(self):
        result = self.session.execute(text("PRAGMA journal_mode")).fetchone()
        self.assertEqual(result[0].lower(), "wal")
        result = self.session.execute(text("PRAGMA synchronous")).fetchone()
        # 1 is NORMAL, 2 is FULL
        self.assertEqual(result[0], 1)

    def test_survey_creation(self):
        survey = Survey(
            question="What is your favorite color?",
            choices=["Red", "Blue", "Green", "Yellow"],
            status=SurveyStatus.PENDING
        )
        self.session.add(survey)
        self.session.commit()
        self.session.refresh(survey)
        
        self.assertIsNotNone(survey.id)
        self.assertEqual(survey.status, SurveyStatus.PENDING)
        self.assertEqual(len(survey.choices), 4)

    def test_persona_creation(self):
        persona = Persona(
            name="Alice",
            age=30,
            job="Engineer",
            personality="Analytical"
        )
        self.session.add(persona)
        self.session.commit()
        self.session.refresh(persona)
        
        self.assertIsNotNone(persona.id)
        self.assertEqual(persona.name, "Alice")

    def test_survey_result_unique_constraint(self):
        survey = Survey(question="Q1", choices=["A", "B", "C", "D"])
        persona = Persona(name="P1", age=25, job="J1", personality="Pers1")
        self.session.add_all([survey, persona])
        self.session.commit()
        
        result1 = SurveyResult(survey_id=survey.id, persona_id=persona.id, choice_index=0)
        self.session.add(result1)
        self.session.commit()
        
        result2 = SurveyResult(survey_id=survey.id, persona_id=persona.id, choice_index=1)
        self.session.add(result2)
        
        with self.assertRaises(IntegrityError):
            self.session.commit()

if __name__ == "__main__":
    unittest.main()
