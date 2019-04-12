import unittest
from sqlalchemy import and_, func, create_engine
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, Mock

import datetime
from src.jukebox.jukebox_functions import JukeBox
from db.objects import Base, Songs, Votes, Round, SelectedSongs

class TestJukebox(unittest.TestCase):
    @patch('src.jukebox.jukebox_functions.JukeBox.init_db')
    def setUp(self, MockInitDb):
        engine = create_engine('sqlite:///:memory:', echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)

        self.session = Session()
        self.session.flush()

        self.session.add(Songs('testSong','testArtist','testFilename', 40.0))
        self.session.add(Songs('testSong2', 'testArtist2', 'testFilename2', 87.0))
        self.session.add(Round(datetime.datetime(2019, 5, 1, 0, 0, 0), datetime.datetime(2019, 5, 1, 0, 0, 10)))
        self.session.add(Votes(1,1))
        self.session.add(Votes(2,1))
        self.session.add(Votes(1,1))
        self.session.add(SelectedSongs(1,1))
        self.session.add(SelectedSongs(2,1))
        self.session.add(SelectedSongs(3,1))
        self.session.add(SelectedSongs(4,1))

        self.session.commit()


        MockInitDb.return_value = self.session
        self.jukebox = JukeBox('empty_music', 'empty_db')

    @patch('src.jukebox.jukebox_functions.datetime')
    def test_count_votes_current_round(self, MockDatetime):
        MockDatetime.now = Mock()
        MockDatetime.now.return_value = datetime.datetime(2019, 5, 1, 0, 0, 5)

        counted_votes = self.jukebox.count_votes_current_round()
        counted_votes = [(v[2].id, v[0]) for v in counted_votes]

        truth = [(1,2), (2,1)]

        return self.assertEqual(truth, counted_votes)


    def test_determine_winning_song_current_round(self):
        now = datetime.datetime(2019, 5, 1, 0, 0, 5)
        vote_round = self.session.query(Round).filter(and_(Round.start_date <= now, Round.end_date >= now)).first()

        database_row_with_votes_per_song = self.session.query(func.count(Votes.song_id), Votes, Songs). \
            filter_by(round_id=vote_round.id). \
            join(Songs). \
            group_by(Songs.id).all()

        winner = self.jukebox.determine_winning_song_current_round(database_row_with_votes_per_song)
        truth = 1

        return self.assertEqual(truth, winner.id)

    def test_select_random_song(self):
        self.jukebox.vote_round = Mock()
        self.jukebox.vote_round.id = 1
        random_song = self.jukebox.select_random_song_from_database()

        song_ids = []
        for song_id in self.session.query(SelectedSongs.song_id):
            song_ids.append(song_id)
        song_ids_ = [song[0] for song in song_ids]

        return self.assertIn(random_song.id, song_ids_)



if __name__ == '__main__':
    unittest.main()
