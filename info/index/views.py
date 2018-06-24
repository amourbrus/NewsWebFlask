from flask import current_app
from flask import render_template

from . import index_blue


@index_blue.route('/favicon.ico')
def favicon_trans():
    return current_app.send_static_file("news/favicon.ico")

@index_blue.route("/")
def index():
    return render_template("news/index.html")
