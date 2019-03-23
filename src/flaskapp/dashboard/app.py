import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from db.objects import db, Votes, Round, SelectedSongs, Songs, IPAddress
from sqlalchemy import func

from flask import Flask

"""
    DATA MANIPULATION
"""


"""
    DASHBOARD LAYOUT / VIEW
"""
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
server.config.from_pyfile('.secrets')

app = dash.Dash(__name__,
                server=server,
                external_stylesheets=external_stylesheets)

with server.app_context():
    db.init_app(server)

app.layout = html.Div(
    html.Div(children=[
        html.H1('Borrel.AI - Live Voting', style={'text-align':'center'}),
        dcc.Graph(id='live-update-voting',
                  figure={
                      'layout': {'width': 10}
                  }),
        dcc.Interval(
            id='interval-component',
            interval = 5000,
            n_intervals = 0
        )
    ], style = {'display': 'inline-block', 'width': '70%'})
)

"""
    INTERACTION BETWEEN COMPONENTS / CONTROLLER
"""
@app.callback(Output('live-update-voting', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_daily_total(n):

    current_round = db.session.query(Round).order_by(Round.id.desc()).first().id

    df_songs = pd.read_sql(db.session.query(SelectedSongs).
                           filter(SelectedSongs.round_id == current_round).statement,
                           db.session.bind)

    df_votes = pd.read_sql(
        db.session.query(Votes, func.count(Votes.song_id)).
        filter(Votes.round_id == current_round).
        group_by(Votes.song_id).statement, db.session.bind)

    if len(df_votes) > 0:
        for row in df_votes.itertuples():
            df_songs.loc[df_songs.song_id == int(row.song_id), 'n_votes'] = row.count_1

        df_songs['n_votes'] = df_songs['n_votes'] / df_songs['n_votes'].sum() * 100
        df_songs.fillna(0)
    else:
        df_songs['n_votes'] = 0

    for t in df_songs.itertuples():
        title = db.session.query(Songs).filter(Songs.id == t.song_id).first().title
        df_songs.loc[df_songs.song_id == t.song_id, 'title'] = title

    # create graphics
    trace = [go.Bar(
        x=df_songs['title'],
        y=df_songs['n_votes'],
        name='Live Voting'
        )
    ]

    return {'data': trace,
            'layout': go.Layout(
                title=f'Current Round: {current_round}',
                xaxis=dict(title=''),
                yaxis=dict(title='% of votes', range=[0, 100])
                )
            }


# Start Flask server
if __name__ == '__main__':
    server.run(host='0.0.0.0', port=8050)
