# coding: utf-8
import sys
sys.path.append("../")
import json
import random
import spotipy
import spotipy.util as util

from datetime import datetime, timedelta
from operator import itemgetter
from sqlalchemy import and_, func, create_engine
from sqlalchemy.orm import sessionmaker
from src.db.objects import Base, Songs, Votes, Round, SelectedSongs
from src.db.populate import populate
from apscheduler.schedulers.background import BlockingScheduler

from src.jukebox.spotipy_config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, USERNAME

class JukeBox:
    def __init__(self, username, source_playlist_uri, db_uri):
        self.username = username
        self.target_playlist_uri = None
        self.source_playlist_uri = source_playlist_uri
        self.session = self.init_db(db_uri)


    def init_db(self, db_uri):
        self.engine = create_engine(db_uri, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        return self.session

    def _spotify_login(self, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI):
        scope = 'playlist-modify-public playlist-modify-private'
        cache_path = '.cache-{}'.format(self.username)

        token = json.load(open(cache_path))

        self.spotify = spotipy.Spotify(auth=token['access_token'])
        print("Spotify login succeeded.")
        return None

    def _create_spotify_target_playlist(self):
        today = datetime.today()
        target_playlist_title = '{}{}{}-XomniaBorrel'.format(today.year,
                                                             today.month,
                                                             today.day)
        print("Finding target playlist...")
        # check if playlist exists
        playlists = self.spotify.user_playlists(self.username)
        if not playlists['items']:
            return self.make_new_playlist(target_playlist_title)
        else:
            for p in playlists['items']:
                if p['name'] == target_playlist_title:
                    self.target_playlist_uri = p['id']
                    return None
                # otherwise create playlist and retrieve the id
                else:
                    return self.make_new_playlist(target_playlist_title)

    def make_new_playlist(self, playlist_title):
        print("Making new playlist...")
        self.spotify.user_playlist_create(self.username, playlist_title)

        # retreive playlist uri of the new playlist for playback
        playlists = self.spotify.user_playlists(self.username)
        print("Made playlist {}".format(playlists['items'][0]['name']))

        target_playlist = [p for p in playlists['items'] if p['name'] == playlist_title]
        self.target_playlist_uri = target_playlist[0]['id']
        return None


    def start_jukebox(self):
        """
        :param music_folder: string, path to music
        :param db_path: string, path to store database
        :return: None
        """
        # empty db and start new schema
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        self.session.commit()

        # login to spotify
        self._spotify_login()
        self._create_spotify_target_playlist()

        # get source playlist_content and populate database
        playlist = self.spotify.user_playlist(self.username,
                                              self.source_playlist_uri,
                                              fields=['tracks'])

        playlist = playlist['tracks']['items']

        populate(self.session, playlist)

        # start playing music
        _ = self.setup_new_round(first_round=True)

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
        3. Play next song

        :param session_obj: db session object
        :param scheduler: apschedular object
        :param music_folder: path to music

        :return: None
        """
        database_row_with_votes_per_song = self.count_votes_current_round()
        winning_song = self.determine_winning_song_current_round(database_row_with_votes_per_song)
        track_uri = [winning_song.uri]

        round_end = self.setup_new_round(song=winning_song, first_round=False)
        run_date = round_end - timedelta(minutes=0, seconds=1)
        print('New song at', run_date)
        self.scheduler.add_job(self.play_next_song, 'date', run_date=run_date, args=[])
        self.play_winning_song(track_uri)

    def play_winning_song(self, track_uri):
        self.spotify.user_playlist_add_tracks(self.username, self.target_playlist_uri, track_uri)

    def setup_new_round(self, first_round=False, song=None):
        """
        :param session: db session object
        :param first_round: Default: False. True if this is the first round to setup in jukebox session,
        :param song: song object to determine new round end
        :return:
        """
        # Randomly provide selection of songs to choose from
        songs = self.session.query(Songs).all()
        selected_song_ids = random.sample(songs, 4)

        if first_round:
            print('Setting up initial round')
            now = datetime.now()
            round_end = now + timedelta(minutes=0, seconds=2)
            vote_round = Round(now, round_end)

        else:
            previous_round = self.session.query(Round).order_by(Round.id.desc()).first()
            round_end = previous_round.end_date + timedelta(minutes=0,
                                                            seconds=song.duration)
            vote_round = Round(previous_round.end_date, round_end)

        self.session.add(vote_round)

        # new query to gain current round id. Why?
        # todo: check if this is best practice
        current_round = self.session.query(Round).order_by(Round.id.desc()).first()

        for song in selected_song_ids:
            selected_songs = SelectedSongs(song.id, current_round.id)
            self.session.add(selected_songs)

        self.session.flush()
        self.session.commit()

        return round_end
