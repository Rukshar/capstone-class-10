import sys
sys.path.append("../")

from datetime import datetime
import json
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from ..db.objects import Songs, Votes, Round, SelectedSongs, IPAddress

from src.jukebox.spotipy_config import CLIENT_ID, CLIENT_SECRET, USERNAME, REDIRECT_URI
from spotipy import oauth2
import docker
import os

app = Flask(__name__)
app.config.from_pyfile('.secrets')

db = SQLAlchemy(app)

scope = 'playlist-modify-public playlist-modify-private'
cache_path = ".cache-{}".format(USERNAME)

@app.route('/')
def main():
    return render_template('home.html')


@app.route('/vote')
def vote():
    """
    Registers votes and voters per round while checking if the specific user already voted in the current round
    :return: url to new route in app depending on what the user did and in what voting round we are
    """
    # Check whether a round is active, start one if not
    now = datetime.now()
    vote_round = db.session.query(Round).filter(and_(Round.start_date <= now, Round.end_date >= now)).first()

    if not vote_round:
        return redirect(url_for('main'))

    if 'song_id' in request.args and 'round_id' in request.args:
        vote_id = int(request.args['song_id'])
        round_id = int(request.args['round_id'])
        ip_address = request.environ['REMOTE_ADDR']

        # Check if a user already voted in the current round
        already_voted = db.session.query(db.exists().where(and_(IPAddress.ip_address == ip_address, 
            IPAddress.round_id == vote_round.id))).scalar()

        if round_id == vote_round.id:
            if already_voted:
                return redirect(url_for('already_voted'))
            else:
                db.session.add(IPAddress(request.environ['REMOTE_ADDR'], vote_round.id))
                db.session.add(Votes(vote_id, vote_round.id))
                db.session.commit()
                return redirect(url_for('vote_redirect'))
        else:
            print("Voting round expired!")

    selected_songs = db.session.query(SelectedSongs, Songs).filter_by(round_id=vote_round.id).join(Songs).all()

    return render_template('vote.html', songs=selected_songs)


@app.route('/vote_redirect')
def vote_redirect():
    return render_template('voted.html')


@app.route('/already_voted')
def already_voted():
    return render_template('already.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route("/login")
def spotify_oauth():
    # Auth Step 1: Authorization
    sp_oauth = oauth2.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI,
                                   scope=scope, cache_path=cache_path)

    token_info = sp_oauth.get_cached_token()

    if token_info['expires_at'] < datetime.now().timestamp():
        os.remove(cache_path)
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    elif not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    else:
        return redirect(url_for('login_succesful'))


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    sp_oauth = oauth2.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI,
                                   scope=scope, cache_path=cache_path)

    token_info = sp_oauth.get_cached_token()
    if not token_info:
        code = request.args['code']
        token = sp_oauth.get_access_token(code)

        with open(cache_path, 'w') as file:
            file.write(json.dumps(token))

    return redirect(url_for('login_succesful'))

@app.route('/login_succesful')
def login_succesful():
    return render_template('login_succesful.html')


@app.route('/start_jukebox')
def start_jukebox():
    if os.path.isfile(cache_path):
        # client = docker.from_env()
        # client.containers.run("jukebox:latest", detach=True)

        import subprocess
        subprocess.call(['python', 'run_jukebox.py'], shell=True)

        return render_template('jukebox_started')

    else:
        return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=False)




