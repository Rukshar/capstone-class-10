from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey

Base = declarative_base()

class Songs(Base):
    __tablename__= 'songs'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    title = Column(String(100), nullable=False)
    artist = Column(String(100), nullable=False)
    filename = Column(String(100), nullable=False)
    duration = Column(Float(), nullable=False)
    year = Column(Integer, nullable=True)

    def __init__(self, title, artist, filename, duration, year=None):
        self.title = title
        self.artist = artist
        self.filename = filename
        self.duration = duration
        if year:
            self.year = year


class Round(Base):
    __tablename__ = 'round'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    round_winner = Column(Integer, ForeignKey('songs.id'))

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(100), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    last_active = Column(DateTime, nullable=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email


class IPAddress(Base):
    __tablename__ = 'ipaddress'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    ip_address = Column(String(100), nullable=False, unique=False)
    round_id = Column(Integer, ForeignKey('round.id'), nullable=False)

    def __init__(self, ip_address, round_id):
        self.ip_address = ip_address
        self.round_id = round_id


class SelectedSongs(Base):
    __tablename__ = 'selectedsongs'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    song_id = Column(Integer, ForeignKey('songs.id'), nullable=False)
    round_id = Column(Integer, ForeignKey('round.id'), nullable=False)

    def __init__(self, song_id, round_id):
        self.song_id = song_id
        self.round_id = round_id


class Votes(Base):
    __tablename__ = 'votes'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    song_id = Column(Integer, ForeignKey('songs.id'), nullable=False)
    round_id = Column(Integer, ForeignKey('round.id'), nullable=False)
    # user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __init__(self, song_id, round_id):
        self.song_id = song_id
        self.round_id = round_id
        # self.user_id = user_id


