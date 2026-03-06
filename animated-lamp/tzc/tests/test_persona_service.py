import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adjust path to import from tzc.app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.persona_service import generate_personas_with_gemini, seed_personas
from app.models import Persona

class TestPersonaService(unittest.TestCase):

    @patch('requests.post')
    @patch('os.getenv')
    def test_generate_personas_with_gemini(self, mock_getenv, mock_post):
        mock_getenv.return_value = "fake-api-key"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": '[{"name": "John Doe", "age": 30, "job": "Developer", "personality": "Kind"}]'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        personas = generate_personas_with_gemini()
        
        self.assertEqual(len(personas), 1)
        self.assertEqual(personas[0]['name'], "John Doe")
        mock_post.assert_called_once()

    @patch('code.animated_lamp.animated_lamp.tzc.app.persona_service.generate_personas_with_gemini')
    @patch('code.animated_lamp.animated_lamp.tzc.app.persona_service.SessionLocal')
    def test_seed_personas(self, mock_session_local, mock_generate):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_generate.return_value = [
            {"name": "John Doe", "age": 30, "job": "Developer", "personality": "Kind"},
            {"name": "Jane Doe", "age": 25, "job": "Designer", "personality": "Creative"}
        ]
        
        count = seed_personas()
        
        self.assertEqual(count, 2)
        self.assertEqual(mock_db.add_all.call_count, 1)
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
