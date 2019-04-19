# coding: utf-8
import sys
sys.path.append("../")
import os
import subprocess
import random

from datetime import datetime, timedelta
from operator import itemgetter
from sqlalchemy import and_, func, create_engine
from sqlalchemy.orm import sessionmaker
from src.db.objects import Base, Songs, Votes, Round, SelectedSongs
from src.db.populate import populate
from apscheduler.schedulers.background import BlockingScheduler


class JukeBox:
    def __init__(self, music_folder, db_uri):
        self.music_folder = music_folder
        self.session = self.init_db(db_uri)


    def init_db(self, db_uri):
        self.engine = create_engine(db_uri, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        return self.session

    def start_jukebox(self):
        """
        :param music_folder: string, path to music
        :param db_path: string, path to store database
        :return: None
        """

        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        self.session.commit()

        populate(self.session, self.music_folder)

        _ = self.setup_initial_round()

        self.add_song_options()

        first_round = datetime.now() + timedelta(minutes=0, seconds=1)
        self.scheduler = BlockingScheduler(timezone="CET")

        # first songs starts after first round of voting (1 minute)
        self.scheduler.add_job(self.play_next_song, 'date', run_date=first_round)
        print('Starting Jukebox')
        self.scheduler.start()

    def count_votes_current_round(self):
        """
        :param session: db session object
        :return: object, database row with info of most voted song
        """
        now = datetime.now()
        self.vote_round = self.session.query(Round).filter(and_(Round.start_date <= now, Round.end_date >= now)).first()

        database_row_with_votes_per_song = self.session.query(func.count(Votes.song_id), Votes, Songs). \
            filter_by(round_id=self.vote_round.id). \
            join(Songs). \
            group_by(Votes.id, Songs.id).all()

        return database_row_with_votes_per_song

    def determine_winning_song_current_round(self, database_row_with_votes_per_song):
        if len(database_row_with_votes_per_song) > 0:
            winner = max(database_row_with_votes_per_song, key=itemgetter(0))[2]
            #TODO: Remove returned votes object instead of indexing to 2?
        else:
            winner = self.select_random_song_from_database()
        return winner

    def select_random_song_from_database(self):
        random_song_id = self.session.query(SelectedSongs).filter(
            SelectedSongs.round_id == self.vote_round.id).first().song_id
        winner = self.session.query(Songs).filter(Songs.id == random_song_id).first()
        return winner

    def play_next_song(self):
        """
        1. Call count votes
        2. Setup New Round
        3. Add song options
        4. Play next song

        :param session_obj: db session object
        :param scheduler: apschedular object
        :param music_folder: path to music

        :return: None
        """

        database_row_with_votes_per_song = self.count_votes_current_round()
        winning_song = self.determine_winning_song_current_round(database_row_with_votes_per_song)
        winning_song_path = os.path.join(self.music_folder, winning_song.filename)

        #TODO: split function further
        round_end = self.setup_new_round(song=winning_song)
        self.add_song_options()
        run_date = round_end - timedelta(minutes=0, seconds=1)
        self.scheduler.add_job(self.play_next_song, 'date', run_date=run_date, args=[])
        self.play_winning_song(winning_song, winning_song_path)

    def play_winning_song(self, winning_song, winning_song_path):
        #TODO: env for system (mac or windows)
        subprocess.call("afplay {}".format(winning_song_path), shell=True)
        # subprocess.call("vlc --one-instance --playlist-enqueue {}".format(winning_song_path), shell=True)
        print('Playing:', winning_song.filename)

    
    def setup_initial_round(self):
        # Setup the first round

        print('Setting up initial round')
        now = datetime.now()
        round_end = now + timedelta(minutes=0, seconds=2)
        vote_round = Round(now, round_end)

        self.session.add(vote_round)
        
    
    def setup_new_round(self, song=None):
        """
        :param session: db session object
        :param first_round: Default: False. True if this is the first round to setup in jukebox session,
        :param song: song object to determine new round end
        :return:
        """
        # Randomly provide selection of songs to choose from
        
        previous_round = self.session.query(Round).order_by(Round.id.desc()).first()
        print('previous round', previous_round.end_date)
        round_end = previous_round.end_date + timedelta(minutes=0,
                                                            seconds=song.duration)
        print('round end in setup_new_round', round_end)
        vote_round = Round(previous_round.end_date, round_end)

        self.session.add(vote_round)

        return round_end

    
    def add_song_options(self):
        # Provide songs that people can vote on

        current_round = self.session.query(Round).order_by(Round.id.desc()).first()

        songs = self.session.query(Songs).all()
        selected_song_ids = random.sample(songs, 4)

        for song in selected_song_ids:
            selected_songs = SelectedSongs(song.id, current_round.id)
            self.session.add(selected_songs)

        self.session.flush()
        self.session.commit()



