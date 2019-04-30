# coding: utf-8
import time
import json
import random
import spotipy
import spotipy.oauth2 as oauth2
from datetime import datetime, timedelta
from operator import itemgetter
from sqlalchemy import and_, func, create_engine
from sqlalchemy.orm import sessionmaker
from src.db.objects import Base, Songs, Votes, Round, SelectedSongs
from src.db.populate import populate
from apscheduler.schedulers.background import BlockingScheduler
from src.jukebox.config import *
from dotenv import load_dotenv


class JukeBox:
    def __init__(self, config):
        self.config = config

        self.session = None

        self.token = None
        self.spotify = None
        self.spotify_oauth = None
        self.target_playlist_uri = None

        self.scheduler = None
        self.vote_round = None

    def _init_db(self):
        engine = create_engine(self.config.SQLALCHEMY_DATABASE_URI, echo=False)
        Session = sessionmaker(bind=engine)
        self.session = Session()

        # empty db and start new schema
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.session.commit()

        return None

    def _spotify_login(self):
        cache_path = '.cache-{}'.format(self.config.SPOTIFY_USERNAME)

        self.token = json.load(open(cache_path))
        
        # spotify object for querying playlists and adding new  songs
        self.spotify = spotipy.Spotify(auth=self.token['access_token'])
        
        # spotify oauth object for token refreshing
        self.spotify_oauth = oauth2.SpotifyOAuth(client_id=self.config.SPOTIFY_CLIENT_ID,
                                                 client_secret=self.config.SPOTIFY_CLIENT_SECRET,
                                                 redirect_uri=self.config.SPOTIFY_REDIRECT_URI,
                                                 scope=self.config.SCOPE,
                                                 cache_path=cache_path
                                                 )
        print("Spotify login succeeded.")
        return None
    
    def _spotify_refresh_token(self):

        if self.spotify_oauth._is_token_expired(self.token):
            self.token = self.spotify_oauth.refresh_access_token(self.token['refresh_token'])
            self.spotify = spotipy.Spotify(auth=self.token['access_token'])
            
        return None

    def _create_spotify_target_playlist(self):
        today = datetime.today()
        target_playlist_title = '{}{}{}-XomniaBorrel'.format(today.year,
                                                             today.month,
                                                             today.day)
        print("Finding target playlist...")
        # check if playlist exists
        playlists = self.spotify.user_playlists(self.config.SPOTIFY_USERNAME)
        if not playlists['items']:
            self.make_new_playlist(target_playlist_title)
        else:
            for p in playlists['items']:
                if p['name'] == target_playlist_title:
                    self.target_playlist_uri = p['id']
                    return None
                # otherwise create playlist and retrieve the id
                else:
                    self.make_new_playlist(target_playlist_title)
                    return None

    def make_new_playlist(self, playlist_title):
        print("Making new playlist...")
        self.spotify.user_playlist_create(self.config.SPOTIFY_USERNAME, playlist_title)

        # retreive playlist uri of the new playlist for playback
        playlists = self.spotify.user_playlists(self.config.SPOTIFY_USERNAME)
        print("Made playlist {}".format(playlists['items'][0]['name']))

        target_playlist = [p for p in playlists['items'] if p['name'] == playlist_title]
        self.target_playlist_uri = target_playlist[0]['id']
        return None

    def start_jukebox(self):
        """
        :return: None
        """
        print('Starting jukebox')
        cache_path = ".cache-{}".format(self.config.SPOTIFY_USERNAME)
        wait_for_spotify_login = True
        while wait_for_spotify_login:
            if os.path.isfile(cache_path):
                with open(cache_path, 'r') as f:
                    token = json.load(f)
                    if token['expires_at'] > int(datetime.now().timestamp()):
                        wait_for_spotify_login = False
                    else:
                        os.remove(cache_path)

            else:
                time.sleep(5)

        self._init_db()

        # login to spotify
        self._spotify_login()
        self._create_spotify_target_playlist()

        # get source playlist_content and populate database
        playlist = self.spotify.user_playlist(self.config.SPOTIFY_USERNAME,
                                              self.config.SPOTIFY_SOURCE_PLAYLIST_URI,
                                              fields=['tracks'])

        playlist = playlist['tracks']['items']

        populate(self.session, playlist)

        # start playing music
        self.setup_new_round(first_round=True)

        first_round = datetime.now() + timedelta(minutes=0, seconds=1)
        self.scheduler = BlockingScheduler(timezone="CET")

        # first songs starts after first round of voting (1 minute)
        self.scheduler.add_job(self.play_next_song, 'date', run_date=first_round)
        self.scheduler.start()

    def count_votes_current_round(self):
        """
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
        else:
            winner = self.select_random_song_from_database()
        return winner

    def select_random_song_from_database(self):
        random_song_id = self.session.query(SelectedSongs).filter(
            SelectedSongs.round_id == self.vote_round.id).order_by(func.random()).first().song_id
        winner = self.session.query(Songs).filter(Songs.id == random_song_id).first()
        return winner

    def play_next_song(self):
        """
        1. Check spotify token validity and refresh
        2. Call count votes
        3. Setup New Round
        4. Play next song

        :return: None
        """
        # refresh token if neccesary
        self._spotify_refresh_token()
        
        database_row_with_votes_per_song = self.count_votes_current_round()
        winning_song = self.determine_winning_song_current_round(database_row_with_votes_per_song)
        track_uri = [winning_song.uri]

        round_end = self.setup_new_round(song=winning_song, first_round=False)
        run_date = round_end - timedelta(minutes=0, seconds=1)
        print('New song at', run_date)
        self.scheduler.add_job(self.play_next_song, 'date', run_date=run_date, args=[])
        self.play_winning_song(track_uri)

    def play_winning_song(self, track_uri):
        self.spotify.user_playlist_add_tracks(self.config.SPOTIFY_USERNAME,
                                              self.target_playlist_uri,
                                              track_uri)

    def setup_new_round(self, first_round=False, song=None):
        """
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

        current_round = self.session.query(Round).order_by(Round.id.desc()).first()

        for song in selected_song_ids:
            selected_songs = SelectedSongs(song.id, current_round.id)
            self.session.add(selected_songs)

        self.session.flush()
        self.session.commit()

        return round_end
