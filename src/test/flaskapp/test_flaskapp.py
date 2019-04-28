import unittest
import datetime

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.objects import Base, Songs, Votes, Round, SelectedSongs
from src.flaskapp import create_app

from src.flaskapp.config import TestingConfig

from unittest.mock import patch, Mock


orig_import = __import__
mock_import = Mock()


def import_mock(name, *args, **kwargs):
    if name == 'src.jukebox.spotipy_config':
        return mock_import
    return orig_import(name, *args, **kwargs)


with patch('builtins.__import__', side_effect=import_mock):
    from src.jukebox.spotipy_config import CLIENT_ID, CLIENT_SECRET, USERNAME, REDIRECT_URI


class TestFlaskapp(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///src/db/test.db', echo=False)
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)

        self.session = Session()

        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create a test client that can make requests
        self.client = self.app.test_client()

    def tearDown(self):
        self.session.flush()
        Base.metadata.drop_all(self.engine)


    def test_main_page(self):
        response = self.client.get('/', follow_redirects=True)
        return self.assertEqual(response.status_code, 200)

    def test_vote_no_db(self):
        response = self.client.get('/vote/', follow_redirects=True)
        assert b'No database connection found.' in response.data
        self.assertEqual(response.status_code, 200)

    @patch('src.flaskapp.views.vote.vote.datetime')
    def test_vote_db(self, MockDateTime):
        MockDateTime.now = Mock()
        MockDateTime.now.return_value = datetime.datetime(2019, 5, 1, 0, 0, 5)

        self.session.add(Round(datetime.datetime(2019, 5, 1, 0, 0, 0), datetime.datetime(2019, 5, 1, 0, 0, 10)))
        self.session.commit()

        response = self.client.get('/vote/', follow_redirects=True)
        assert b'Voting' in response.data
        self.assertEqual(response.status_code, 200)

    # @patch('src.flaskapp.views.vote.vote.vote_song.datetime')
    # def test_vote_song(self, MockDateTime):
    # 	MockDateTime.now = Mock()
    # 	MockDateTime.now.return_value = datetime.datetime(2019, 5, 1, 0, 0, 5)
    #
    # 	self.session.add(Round(datetime.datetime(2019, 5, 1, 0, 0, 0), datetime.datetime(2019, 5, 1, 0, 0, 10)))
    # 	self.session.add(Round(datetime.datetime(2019, 5, 1, 0, 0, 10), datetime.datetime(2019, 5, 1, 0, 0, 20)))
    # 	self.session.commit()

        # with self.client as c:
        # 	response = c.get('/vote/vote_song?song_id=1&round_id=1', follow_redirects=True)
        # 	assert request.args['song_id'] == '1'
        # 	assert request.args['round_id'] == '2'
        # 	assert request.environ['REMOTE_ADDR'] == '127.0.0.1'
        #
        # assert b'Voting round expired! Try again' in response.data



