from flask import Blueprint, render_template
import sys
sys.path.append("../")
from datetime import datetime
import json
from flask import request, render_template, redirect, url_for

from src.jukebox.spotipy_config import CLIENT_ID, CLIENT_SECRET, USERNAME, REDIRECT_URI
from spotipy import oauth2
import os

from src.flaskapp.extensions import basic_auth

admin = Blueprint('admin', __name__, url_prefix='/admin')

scope = 'playlist-modify-public playlist-modify-private'
cache_path = ".cache-{}".format(USERNAME)


@admin.route('/')
@basic_auth.required
def index():
    return render_template('admin/home.html')


@admin.route("/login")
@basic_auth.required
def spotify_oauth():
    # Auth Step 1: Authorization
    sp_oauth = oauth2.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI,
                                   scope=scope, cache_path=cache_path)

    token_info = sp_oauth.get_cached_token()

    if token_info and token_info['expires_at'] < datetime.now().timestamp():
        os.remove(cache_path)
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    elif not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    else:
        return redirect(url_for('admin.login_succesful'))


@admin.route("/callback/q")
@basic_auth.required
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

    return redirect(url_for('admin.login_succesful'))

@admin.route('/login_succesful')
@basic_auth.required
def login_succesful():
    return render_template('admin/login_succesful.html')