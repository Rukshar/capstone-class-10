import unittest
from src.flaskapp.app import app, main, vote

class TestFlaskApp(unittest.TestCase):

	def setUp(self):
		self.app = app.test_client()

	def tearDown(self):
		pass

	def test_main_page(self):
		response = self.app.get('/', follow_redirects=True)
		return self.assertEqual(response.status_code, 200)

	def test_vote_page(self):
		response = self.app.get('/vote', follow_redirects=True)
		return self.assertEqual(response.status_code, 200)

