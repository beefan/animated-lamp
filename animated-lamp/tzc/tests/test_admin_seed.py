import unittest
from fastapi.testclient import TestClient
import os
import sys

# Adjust path to import from tzc
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app, ADMIN_TOKEN

class TestAdminSeedEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_seed_personas_unauthorized(self):
        response = self.client.post("/admin/seed-personas", headers={"X-Admin-Token": "wrong-token"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing admin token"})

    def test_seed_personas_missing_header(self):
        response = self.client.post("/admin/seed-personas")
        self.assertEqual(response.status_code, 401)

    def test_seed_personas_success(self):
        # Mock the celery task delay
        from unittest.mock import patch
        with patch("app.main.generate_personas_task.delay") as mock_delay:
            mock_task = type('obj', (object,), {'id': 'test-task-id'})
            mock_delay.return_value = mock_task
            
            response = self.client.post(
                "/admin/seed-personas", 
                headers={"X-Admin-Token": ADMIN_TOKEN}
            )
            
            self.assertEqual(response.status_code, 202)
            self.assertEqual(response.json(), {"task_id": "test-task-id"})
            mock_delay.assert_called_once()

if __name__ == "__main__":
    unittest.main()
