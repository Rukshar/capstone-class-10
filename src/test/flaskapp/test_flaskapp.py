import unittest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.objects import Base, Songs, Votes, Round, SelectedSongs
from src.flaskapp import create_app


class TestFlaskapp(unittest.TestCase):
	render_templates = False

	def setUp(self):
		app = create_app()
		self.app = app.test_client()

		engine = create_engine('sqlite:///:memory:', echo=True)
		Base.metadata.create_all(engine)
		Session = sessionmaker(bind=engine)

		self.session = Session()
		self.session.flush()

		self.session.add(Songs('testSong', 'testArtist', 'testFilename', 40.0))
		self.session.add(Songs('testSong2', 'testArtist2', 'testFilename2', 87.0))
		# self.session.add(Round(datetime.datetime(2019, 5, 1, 0, 0, 0), datetime.datetime(2019, 5, 1, 0, 0, 10)))
		# self.session.add(Votes(1,1))
		# self.session.add(SelectedSongs(1,1))

		self.session.commit()

	def tearDown(self):
		pass

	def test_main_page(self):
		response = self.app.get('/', follow_redirects=True)
		return self.assertEqual(response.status_code, 200)

	def test_vote_page(self):
		response = self.app.get('/vote', follow_redirects=True)
		#TODO Link DB connection so page gives 200 instead of 501 (database not found)
		return self.assertEqual(response.status_code, 501)

