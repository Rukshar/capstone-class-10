from threading import Thread
from src.jukebox.jukebox_functions import start_jukebox
from src.flaskapp.app import app

music_folder = 'music/'
db_path = 'src/db/dev.db'

if __name__ == '__main__':
    jukebox_args = {"music_folder": music_folder, "db_path": db_path}
    flaskapp_args = {"debug": False,"host": "0.0.0.0","port": 5000}

    jukebox_thread = Thread(target=start_jukebox, kwargs=jukebox_args)
    flaskapp_thread = Thread(target=app.run, kwargs=flaskapp_args)

    jukebox_thread.start()
    flaskapp_thread.start()

