from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Songs(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Float(), nullable=False)
    year = db.Column(db.Integer, nullable=True)

    def __init__(self, title, artist, filename, duration, year=None):
        self.title = title
        self.artist = artist
        self.filename = filename
        self.duration = duration
        if year:
            self.year = year


class Round(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    round_winner = db.Column(db.Integer, db.ForeignKey('songs.id'))

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    last_active = db.Column(db.DateTime, nullable=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email


class IPAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    ip_address = db.Column(db.String(100), nullable=False, unique=False)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), nullable=False)

    def __init__(self, ip_address, round_id):
        self.ip_address = ip_address
        self.round_id = round_id


class SelectedSongs(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), nullable=False)

    def __init__(self, song_id, round_id):
        self.song_id = song_id
        self.round_id = round_id


class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, song_id, round_id):
        self.song_id = song_id
        self.round_id = round_id
        # self.user_id = user_id


