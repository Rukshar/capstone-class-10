from src.jukebox.jukebox_functions import JukeBox
from src.jukebox.test_config import USERNAME, TARGET_PLAYLIST_URI, SOURCE_PLAYLIST_URI

db_uri = 'postgresql://postgres:docker@localhost:5432/postgres'

jukebox = JukeBox(username=USERNAME,
                  target_playlist_uri=TARGET_PLAYLIST_URI,
                  source_playlist_uri=SOURCE_PLAYLIST_URI,
                  db_uri=db_uri)

if __name__ == '__main__':
    jukebox.start_jukebox()