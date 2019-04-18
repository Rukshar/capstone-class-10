from src.jukebox.jukebox_functions import JukeBox

music_folder = 'music/'
# db_uri = 'postgresql://postgres:docker@localhost:5432/postgres'
db_uri = 'sqlite:///:dev.db:'

jukebox = JukeBox(music_folder, db_uri)

if __name__ == '__main__':
    jukebox.start_jukebox()