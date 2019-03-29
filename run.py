from threading import Thread
from src.jukebox.jukebox_functions import JukeBox
from src.flaskapp.app import app

music_folder = 'music/'
db_path = 'src/db/dev.db'

jukebox = JukeBox(music_folder, db_path)

if __name__ == '__main__':
    flaskapp_args = {"debug": False,"host": "0.0.0.0","port": 5000}

    jukebox_thread = Thread(target=jukebox.start_jukebox)
    flaskapp_thread = Thread(target=app.run, kwargs=flaskapp_args)

    jukebox_thread.start()
    flaskapp_thread.start()

