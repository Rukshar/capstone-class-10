import unittest
from sqlalchemy import and_, func, create_engine
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, Mock
import datetime
from src.jukebox.jukebox_functions import count_votes
from db.objects import Base, Songs, Votes, Round, SelectedSongs

#from src.jukebox.jukebox_functions import count_votes

class TestJukeboxFunctions(unittest.TestCase):

    def setUp(self):
        engine = create_engine('sqlite:///:memory:', echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)

        self.session = Session()
        self.session.flush()

        self.session.add(Songs('testSong','testArtist','testFilename',40.0))
        self.session.add(Songs('testSong2', 'testArtist2', 'testFilename2', 87.0))
        self.session.add(Round(datetime.datetime.now(), datetime.datetime.now()+datetime.timedelta(seconds=10)))
        # self.session.add(Votes(1,1))
        # self.session.add(Votes(2,1))
        # self.session.add(Votes(1,1))
        self.session.add(SelectedSongs(1,1))
        self.session.add(SelectedSongs(2,1))
        self.session.add(SelectedSongs(3,1))
        self.session.add(SelectedSongs(4,1))

        self.session.commit()

    #@patch('datetime.now')
    def test_count_votes(self): #, mock_datetime):
        now = datetime.datetime.now()
        test_winnaar = count_votes(self.session)
        test_winnaar_id = test_winnaar.id
        #all_titles = self.session.query(SelectedSongs.song_id)
        song_ids = []
        for song_id in self.session.query(SelectedSongs.song_id):
            song_ids.append(song_id)
        song_ids_ = [song[0] for song in song_ids]

        self.assertIn(test_winnaar_id, song_ids_)

        # self.session.add(Votes(1,1))
        # self.session.add(Votes(2,1))
        # self.session.add(Votes(1,1))
        #
        # test_winnaar = count_votes(self.session)
        # test_winnaar_title = test_winnaar.title
        #
        # self.assertEqual(test_winnaar_title,'testSong')