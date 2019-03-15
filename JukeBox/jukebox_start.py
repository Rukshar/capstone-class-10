import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.objects import Base
from db.populate import populate
from JukeBox.jukebox_functions import setup_new_round, play_next_song
from apscheduler.schedulers.background import BlockingScheduler

music_folder = '../music/'
db = '../db/dev.db'


def start_jukebox(music_folder=music_folder, db_path=db):
    """
    :param music_folder: string, path to music
    :param db_path: string, path to store database
    :return: None
    """

    db = 'sqlite:///{}'.format(db_path)

    engine = create_engine(db, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    # initiate database
    if not os.path.isfile('../db/dev.db'):
        print('No existing database found, starting new session')
        Base.metadata.create_all(engine)

    populate(session, music_folder)

    round_end = setup_new_round(session, first_round=True)
    first_round = datetime.now() + timedelta(minutes=0, seconds=1)
    scheduler = BlockingScheduler()

    # first songs starts after first round of voting (1 minute)
    scheduler.add_job(play_next_song, 'date', run_date=first_round, args=[Session, scheduler, music_folder])
    print('Starting Jukebox')
    scheduler.start()

    return None


if __name__ == '__main__':
    start_jukebox()






