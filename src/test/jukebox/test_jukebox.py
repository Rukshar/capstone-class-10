import datetime
import os

from sqlalchemy import and_, func
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.objects import Base, Songs, Votes, Round, SelectedSongs

import unittest
from unittest.mock import patch, Mock
from src.jukebox import create_jukebox


class TestJukebox(unittest.TestCase):

    def setUp(self):
        os.environ['ENV'] = 'test'
        self.jukebox = create_jukebox()
        self.jukebox._init_db()

        self.jukebox.session
        self.jukebox.session.add(Songs('testSong', 'testArtist', 'testFilename', 40.0))
        self.jukebox.session.add(Songs('testSong2', 'testArtist2', 'testFilename2', 87.0))
        self.jukebox.session.add(Round(datetime.datetime(2019, 5, 1, 0, 0, 0), datetime.datetime(2019, 5, 1, 0, 0, 10)))
        self.jukebox.session.add(Votes(1, 1))
        self.jukebox.session.add(Votes(2, 1))
        self.jukebox.session.add(Votes(1, 1))
        self.jukebox.session.add(SelectedSongs(1, 1))
        self.jukebox.session.add(SelectedSongs(2, 1))
        self.jukebox.session.add(SelectedSongs(3, 1))
        self.jukebox.session.add(SelectedSongs(4, 1))

        self.jukebox.session.commit()

    @patch('src.jukebox.jukebox.datetime')
    def test_count_votes_current_round(self, MockDatetime):
        MockDatetime.now = Mock()
        MockDatetime.now.return_value = datetime.datetime(2019, 5, 1, 0, 0, 5)

        counted_votes = self.jukebox.count_votes_current_round()
        counted_votes = [(v[2].id, v[0]) for v in counted_votes]

        truth = [(1, 1), (2, 1), (1, 1)]

        return self.assertEqual(truth, counted_votes)

    def test_determine_winning_song_current_round(self):
        now = datetime.datetime(2019, 5, 1, 0, 0, 5)
        vote_round = self.jukebox.session.query(Round).filter(and_(Round.start_date <= now, Round.end_date >= now)).first()

        database_row_with_votes_per_song = self.jukebox.session.query(func.count(Votes.song_id), Votes, Songs). \
            filter_by(round_id=vote_round.id). \
            join(Songs). \
            group_by(Votes.id, Songs.id).all()

        winner = self.jukebox.determine_winning_song_current_round(database_row_with_votes_per_song)
        truth = 1

        return self.assertEqual(truth, winner.id)

    def test_select_random_song(self):
        self.jukebox.vote_round = Mock()
        self.jukebox.vote_round.id = 1
        random_song = self.jukebox.select_random_song_from_database()

        song_ids = []
        for song_id in self.jukebox.session.query(SelectedSongs.song_id):
            song_ids.append(song_id)
        song_ids_ = [song[0] for song in song_ids]

        return self.assertIn(random_song.id, song_ids_)

