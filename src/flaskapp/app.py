import sys
sys.path.append("../")

from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from ..db.objects import Songs, Votes, Round, SelectedSongs, IPAddress

app = Flask(__name__)
app.config.from_pyfile('.secrets')

db = SQLAlchemy(app)


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
    vote_round = db.session.query(Round).order_by(Round.id.desc()).first()

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


if __name__ == '__main__':
    app.run(debug=False)




