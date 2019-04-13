from src.jukebox.jukebox_functions import JukeBox

music_folder = 'music/'
db_uri = 'postgresql://postgres:docker@localhost:5432/postgres'

jukebox = JukeBox(user_playlist_uri='44x9Ip9p7A9Po4nXVgiPsZ',
                  source_playlist_uri='6gIAkN8yDny047kJjj2bNy',
                  db_uri=db_uri)

if __name__ == '__main__':
    jukebox.start_jukebox()