import sys
import pandas as pd
from src.db.objects import Songs, Votes, Round, SelectedSongs
from flask import Blueprint, request, render_template, redirect, url_for
from sqlalchemy import func
from bokeh.plotting import figure
from bokeh.embed import components
from src.flaskapp.extensions import db

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def fetch_data():
    """
    @return DataFrame with information about the voting
    """
    current_round = db.session.query(Round).order_by(Round.id.desc()).first().id

    df_songs = pd.read_sql(db.session.query(SelectedSongs).
                           filter(SelectedSongs.round_id == current_round).statement,
                           db.session.bind)

    df_votes = pd.read_sql(
        db.session.query(Votes, func.count(Votes.song_id)).
            filter(Votes.round_id == current_round).
            group_by(Votes.id, Votes.song_id).statement, db.session.bind)

    if len(df_votes) > 0:
        for row in df_votes.itertuples():
            df_songs.loc[df_songs.song_id == int(row.song_id), 'n_votes'] = row.count_1

        df_songs['n_votes'] = df_songs['n_votes'] / df_songs['n_votes'].sum() * 100
        df_songs.fillna(0)
    else:
        df_songs['n_votes'] = 0

    for t in df_songs.itertuples():
        song = db.session.query(Songs).filter(Songs.id == t.song_id).first()
        df_songs.loc[df_songs.song_id == t.song_id, 'title'] = "{} - {}".format(song.artist,
                                                                                song.title
                                                                                )

    return df_songs


def create_figure():
    """
    @return Bokeh figure visualising the votes
    """
    data = fetch_data()

    p = figure(x_range=data['title'],
               y_range=(0, 100),
               plot_width=1000,
               plot_height=500,
               title='',
               toolbar_location=None
               )

    p.vbar(x=data['title'], top=data['n_votes'], width=0.9)

    # Set the x axis label
    p.xaxis.axis_label = ''
    p.xgrid.grid_line_color = None

    return p


@dashboard.route('/')
def index():
    plot = create_figure()

    script, div = components(plot)

    return render_template("dashboard/dashboard.html", script=script, div=div)
