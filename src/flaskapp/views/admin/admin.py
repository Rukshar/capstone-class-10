import os
from flask import Blueprint, render_template
from datetime import datetime
import json
from flask import request, render_template, redirect, url_for
from spotipy import oauth2
from src.flaskapp.extensions import basic_auth

admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('/')
@basic_auth.required
def index():
    return render_template('admin/home.html')


@admin.route("/login")
@basic_auth.required
def spotify_oauth():
    scope = 'playlist-modify-public playlist-modify-private'
    cache_path = ".cache-{}".format(os.environ.get('SPOTIFY_USERNAME'))

    # Auth Step 1: Authorization
    sp_oauth = oauth2.SpotifyOAuth(os.environ.get('SPOTIFY_CLIENT_ID'),
                                   os.environ.get('SPOTIFY_CLIENT_SECRET'),
                                   os.environ.get('SPOTIFY_REDIRECT_URI'),
                                   scope=scope,
                                   cache_path=cache_path)

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
    scope = 'playlist-modify-public playlist-modify-private'
    cache_path = ".cache-{}".format(os.environ.get('SPOTIFY_USERNAME'))

    # Auth Step 4: Requests refresh and access tokens
    sp_oauth = oauth2.SpotifyOAuth(os.environ.get('SPOTIFY_CLIENT_ID'),
                                   os.environ.get('SPOTIFY_CLIENT_SECRET'),
                                   os.environ.get('SPOTIFY_REDIRECT_URI'),
                                   scope=scope,
                                   cache_path=cache_path)

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