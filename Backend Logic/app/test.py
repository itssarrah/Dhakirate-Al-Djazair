import unittest
import json
from flask import Flask
from app import create_app

# app/test_routes.py


class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    def test_ask_question_missing_fields(self):
        response = self.app.post('/ask', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing required fields',
                      response.get_data(as_text=True))

    # def test_ask_question_success(self):
    #     payload = {
    #         'email': 'test@example.com',
    #         'question': 'ما هي الأسباب الرئيسية وراء الاحتلال الفرنسي للجزائر؟',
    #         'educational_stage': 'PS5',
    #         'historical_era': ''
    #     }
    #     response = self.app.post('/ask', json=payload)
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.get_data(as_text=True))
    #     self.assertIn('session_nonce', data)
    #     self.assertIn('answer', data)

    def test_get_context_missing_fields(self):
        response = self.app.get('/context')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing required fields',
                      response.get_data(as_text=True))

    def test_get_context_success(self):
        response = self.app.get(
            '/context', query_string={'email': 'test@example.com', 'session_nonce': '12345'})
        self.assertEqual(response.status_code, 404)
        self.assertIn('Session not found', response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
