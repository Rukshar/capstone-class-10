import os
from flask import Blueprint, render_template
from datetime import datetime
import json
from flask import request, render_template, redirect, url_for
from flask import current_app as app
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
    #TODO: make it so that we only need to change this in one place

    # Auth Step 1: Authorization
    sp_oauth = oauth2.SpotifyOAuth(client_id=os.environ.get('SPOTIFY_CLIENT_ID'),
                                   client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET'),
                                   redirect_uri=app.config['SPOTIFY_REDIRECT_URI'],
                                   scope=scope,
                                   cache_path=app.config['CACHE_PATH'])

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
    #TODO: make it so that we only need to change this in one place
    scope = 'playlist-modify-public playlist-modify-private'

    # Auth Step 4: Requests refresh and access tokens
    sp_oauth = oauth2.SpotifyOAuth(client_id=os.environ.get('SPOTIFY_CLIENT_ID'),
                                   client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET'),
                                   redirect_uri=app.config['SPOTIFY_REDIRECT_URI'],
                                   scope=scope,
                                   cache_path=app.config['CACHE_PATH'])

    token_info = sp_oauth.get_cached_token()
    if not token_info:
        code = request.args['code']
        token = sp_oauth.get_access_token(code)

        with open(app.config['CACHE_PATH'], 'w') as file:
            file.write(json.dumps(token))

    return redirect(url_for('admin.login_succesful'))

@admin.route('/login_succesful')
@basic_auth.required
def login_succesful():
    return render_template('admin/login_succesful.html')