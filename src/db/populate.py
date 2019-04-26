from src.db.objects import Base, Songs, Votes, Round, IPAddress
from tinytag import TinyTag
import os
import re


def populate(session, playlist):
    for song in playlist:
        title = song['track']['name']
        artist = song['track']['artists'][0]['name']
        song_uri = song['track']['uri']
        duration = song['track']['duration_ms'] / 1000
        session.add(Songs(title, artist, song_uri, duration))

    session.flush()
    session.commit()

    return None

