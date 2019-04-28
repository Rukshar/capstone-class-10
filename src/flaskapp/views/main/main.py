from flask import Blueprint, render_template

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main/home.html')
