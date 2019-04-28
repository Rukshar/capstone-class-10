from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for
from sqlalchemy import and_
from src.db.objects import Songs, Votes, Round, SelectedSongs, IPAddress
from src.flaskapp.extensions import db

vote = Blueprint('vote', __name__, url_prefix='/vote')


@vote.route('/', methods=['GET'])
def index():
    """
    Registers votes and voters per round while checking if the specific user already voted in the current round
    :return: url to new route in app depending on what the user did and in what voting round we are
    """
    now = datetime.now()
    vote_round = db.session.query(Round).filter(and_(Round.start_date <= now, Round.end_date >= now)).first()

    if vote_round is None:
        return render_template('error/not_active.html')

    selected_songs = db.session.query(SelectedSongs, Songs).filter_by(round_id=vote_round.id).join(Songs).all()
    return render_template('vote/vote.html', songs=selected_songs)


@vote.route('/vote_song')
def vote_song():
    now = datetime.now()
    vote_round = db.session.query(Round).filter(and_(Round.start_date <= now, Round.end_date >= now)).first()

    if vote_round is None:
        return render_template('error/not_active.html')

    vote_id = int(request.args['song_id'])
    round_id = int(request.args['round_id'])
    ip_address = request.environ['REMOTE_ADDR']

    # Check if a user already voted in the current round
    already_voted = db.session.query(db.exists().where(and_(IPAddress.ip_address == ip_address,
        IPAddress.round_id == vote_round.id))).scalar()

    if round_id == vote_round.id:
        if already_voted:
            return redirect(url_for('vote.already_voted'))
        else:
            db.session.add(IPAddress(request.environ['REMOTE_ADDR'], vote_round.id))
            db.session.add(Votes(vote_id, vote_round.id))
            db.session.commit()
            return redirect(url_for('vote.vote_redirect'))
    else:
        return redirect(url_for('vote.expired'))

@vote.route('/vote_redirect')
def vote_redirect():
    return render_template('vote/voted.html')


@vote.route('/not_active')
def not_active():
    return render_template('error/not_active.html')


@vote.route('/already_voted')
def already_voted():
    return render_template('vote/already.html')


@vote.route('/expired')
def expired():
    return render_template('vote/expired.html')
