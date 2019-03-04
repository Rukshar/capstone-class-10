import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.objects import Base
from db.populate import populate
from JukeBox.jukebox_functions import setup_new_round, play_next_song
from apscheduler.schedulers.background import BlockingScheduler

music_folder = '../music/'

engine = create_engine('sqlite:///../db/dev.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
# note: removed session.configure and put bind in sessionmaker
# todo: after few rounds error in database threads

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






