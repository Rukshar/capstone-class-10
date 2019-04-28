from threading import Thread
from src.jukebox.jukebox_functions import JukeBox
from src.flaskapp import routes

music_folder = 'music/'
db_path = 'postgresql://postgres:docker@localhost:5432/postgres'

jukebox = JukeBox(music_folder, db_path, None)

if __name__ == '__main__':
    flaskapp_args = {"debug": False,"host": "0.0.0.0","port": 5000}

    jukebox_thread = Thread(target=jukebox.start_jukebox)
    flaskapp_thread = Thread(target=routes.run, kwargs=flaskapp_args)

    jukebox_thread.start()
    flaskapp_thread.start()

