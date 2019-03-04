# coding: utf-8
import os
import subprocess
import random
from datetime import datetime, timedelta
from operator import itemgetter
from sqlalchemy import and_, func
from db.objects import Songs, Votes, Round, SelectedSongs


def count_votes(session):
    now = datetime.now()
    vote_round = session.query(Round).filter(and_(Round.start_date <= now, Round.end_date >= now)).first()

    counted_votes = session.query(func.count(Votes.song_id), Votes, Songs). \
        filter_by(round_id=vote_round.id). \
        join(Songs). \
        group_by(Votes.song_id).all()

    # handle rounds without votes
    if len(counted_votes) > 0:
        winner = max(counted_votes, key=itemgetter(0))[2]  # Remove returned votes object instead of indexing to 2?
    else:
        random_song_id = session.query(SelectedSongs).filter(SelectedSongs.round_id == vote_round.id).first().song_id
        winner = session.query(Songs).filter(Songs.id == random_song_id).first()

    return winner


def play_next_song(session_obj, scheduler, music_folder):
    session = session_obj()
    song = count_votes(session)
    round_end = setup_new_round(session=session, song=song)

    song_path = os.path.join(music_folder, song.filename)

    run_date = round_end - timedelta(minutes=0, seconds=1)
    print('New song at', run_date)
    scheduler.add_job(play_next_song, 'date', run_date=run_date, args=[session_obj, scheduler, music_folder])

    print('Playing:', song.filename)
    # if on RasPi use 'vlc --one-instance --playlist-enqueue'
    subprocess.call("vlc --play-and-stop {}".format(song_path), shell=True)

    return None


def setup_new_round(session, first_round=False, song=None):
    # Randomly provide selection of songs to choose from
    songs = session.query(Songs).all()
    selected_song_ids = random.sample(songs, 4)

    if first_round:
        print('Setting up initial round')
        now = datetime.now()
        round_end = now + timedelta(minutes=0, seconds=2)
        vote_round = Round(now, round_end)

    else:
        previous_round = session.query(Round).order_by(Round.id.desc()).first()
        round_end = previous_round.end_date + timedelta(minutes=0,
                                                        seconds=song.duration)
        vote_round = Round(previous_round.end_date, round_end)

    session.add(vote_round)

    # new query to gain current round id. Why?
    # todo: check if this is best practice
    current_round = session.query(Round).order_by(Round.id.desc()).first()

    for song in selected_song_ids:
        selected_songs = SelectedSongs(song.id, current_round.id)
        session.add(selected_songs)

    session.flush()
    session.commit()

    return round_end




