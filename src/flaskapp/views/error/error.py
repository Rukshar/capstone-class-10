from flask import render_template, Blueprint


error = Blueprint('error', __name__)


@error.app_errorhandler(400)
def unhandled_exception(e):
    return render_template('error/400.html'), 400


@error.app_errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


@error.app_errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500


@error.app_errorhandler(Exception)
def unhandled_exception(e):
    return render_template('error/500.html'), 501
