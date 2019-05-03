import pandas as pd
import json
import textwrap
from flask import Blueprint, render_template
from sqlalchemy import func
import plotly
import plotly.graph_objs as go
from src.db.objects import Songs, Votes, Round, SelectedSongs
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
    # textwrap long titles
    df_songs['title'] = ['<br>'.join(textwrap.wrap(i, 20)) for i in df_songs.title]

    # fix possibility of duplicate tracks in one random pick
    df_songs = df_songs.groupby('title').n_votes.sum().reset_index()

    return df_songs


def create_figure():
    """
    @return Plotly figure visualising the votes
    """
    data = fetch_data()

    trace = [go.Bar(
        x = data['title'],
        y= data['n_votes'],
        name='',
        marker=dict(
            color='rgb(34,50,132)'
        )
    )]

    layout = go.Layout(
        xaxis=dict(
            title='',
            tickfont=dict(
                size=16
            )
        ),
        yaxis=dict(
            title='% of Votes',
            range=[0, 100],
            showline=True,
            tickfont=dict(
                size=16,
            )
        )
    )

    fig = go.Figure(data=trace, layout=layout)
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graph_json


@dashboard.route('/')
def index():
    plot = create_figure()

    return render_template("dashboard/dashboard.html", plot=plot)
