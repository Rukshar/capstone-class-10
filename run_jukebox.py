from src.jukebox.jukebox_functions import JukeBox
from src.jukebox.spotipy_config import USERNAME, TARGET_PLAYLIST_URI, SOURCE_PLAYLIST_URI

db_uri = 'postgresql://postgres:docker@localhost:5432/postgres'
# db_uri = 'postgresql://postgres:docker@borrel_database:5432/postgres'

jukebox = JukeBox(username=USERNAME,
                  source_playlist_uri=SOURCE_PLAYLIST_URI,
                  db_uri=db_uri)

if __name__ == '__main__':
    jukebox.start_jukebox()