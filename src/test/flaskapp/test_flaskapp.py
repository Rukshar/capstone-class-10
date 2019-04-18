import unittest
import datetime

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.objects import Base, Songs, Votes, Round, SelectedSongs
from src.flaskapp import create_app

from src.flaskapp.config import TestingConfig
from src.flaskapp.extensions import db

from unittest.mock import patch, Mock

class TestFlaskapp(unittest.TestCase):

	def setUp(self):
		# Create DB in SQLlite memory
		engine = create_engine('sqlite:///:memory:', echo=False)
		Base.metadata.create_all(engine)
		Session = sessionmaker(bind=engine)

		self.session = Session()
		self.session.flush()

		# Add dummy's (copied from jukebox test)
		self.session.add(Songs('testSong', 'testArtist', 'testFilename', 40.0))
		self.session.add(Songs('testSong2', 'testArtist2', 'testFilename2', 87.0))
		self.session.add(Round(datetime.datetime(2019, 5, 1, 0, 0, 0), datetime.datetime(2019, 5, 1, 0, 0, 10)))
		self.session.add(Votes(1, 1))
		self.session.add(Votes(2, 1))
		self.session.add(Votes(1, 1))
		self.session.add(SelectedSongs(1, 1))
		self.session.add(SelectedSongs(2, 1))
		self.session.add(SelectedSongs(3, 1))
		self.session.add(SelectedSongs(4, 1))

		self.session.commit()

		# Create app with testconfig that looks for a DB in sqllite:memory
		# We won't be using the session, because our app doesn't use the session
		# but instead uses the db = SQLAlchemy() object
		self.app = create_app(TestingConfig)
		self.app_context = self.app.app_context()
		self.app_context.push()

		# print(f"DB: {app.config['SQLALCHEMY_DATABASE_URI']}")
		# Create a test client that can make requests
		self.client = self.app.test_client()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_main_page(self):

		# This works
		print(f"{self.session.query(Round).first()}")

		# This doesn't
		print(f"{db.session.query(Round).first()}")

		# Neither does this
		with self.app.app_context():
			print(f"{db.session.query(Round).first()}")

		response = self.client.get('/', follow_redirects=True)
		return self.assertEqual(response.status_code, 200)

	# @patch('src.flaskapp.views.vote.vote.datetime')
	# def test_vote_page(self, MockDatetime):
	# 	MockDatetime.now = Mock()
	# 	MockDatetime.now.return_value = datetime.datetime(2019, 5, 1, 0, 0, 5)
	#
	# 	print(f"{db.session.query(Round)}")
	# 	print("TESTING VOTE PAGE")
	# 	response = self.client.get('/vote_song', follow_redirects=True)
	# 	print(response)
	# 	#TODO Link DB connection so page gives 200 instead of 501 (database not found)
	# 	return self.assertEqual(response.status_code, 501)

