import os, time
import json
from datetime import datetime
from src.jukebox.jukebox_functions import JukeBox
from src.jukebox.spotipy_config import USERNAME, TARGET_PLAYLIST_URI, SOURCE_PLAYLIST_URI

db_uri = 'postgresql://postgres:docker@localhost:5432/postgres'
# db_uri = 'postgresql://postgres:docker@borrel_database:5432/postgres'

cache_path = ".cache-{}".format(USERNAME)

jukebox = JukeBox(username=USERNAME,
                  source_playlist_uri=SOURCE_PLAYLIST_URI,
                  db_uri=db_uri)

wait_for_spotify_login = True

if __name__ == '__main__':
    while wait_for_spotify_login:
        if os.path.isfile(cache_path):
            token = json.load(open(cache_path))
            if token['expires_at'] > int(datetime.now().timestamp()):
                wait_for_spotify_login = False
            else:
                os.remove(cache_path)

        else:
            time.sleep(5)

    jukebox.start_jukebox()