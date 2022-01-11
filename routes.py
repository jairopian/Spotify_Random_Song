from app import app
from models import User, Artist
import os
from genius import get_lyrics_link
from spotify import get_access_token, get_song_data

import flask
from flask_login import login_user, current_user, LoginManager
from flask_login.utils import login_required

import random
import base64
import requests


login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_name):
    return User.query.get(user_name)


MARKET = "US"
ARTIST_IDS = [
    "4UXqAaa6dQYAk18Lv7PEgX",  # FOB
    "3jOstUTkEu2JkjvRdBA5Gu",  # Weezer
    "7oPftvlwr6VrsViSDV7fJY",  # Green Day
]


def get_access_token():
    auth = base64.standard_b64encode(
        bytes(
            f"{os.getenv('SPOTIFY_CLIENT_ID')}:{os.getenv('SPOTIFY_CLIENT_SECRET')}",
            "utf-8",
        )
    ).decode("utf-8")
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"},
    )
    json_response = response.json()
    return json_response["access_token"]


@app.route("/signup")
def signup():
    return flask.render_template("signup.html")


@app.route("/signup", methods=["POST"])
def signup_post():
    username = flask.request.form.get("username")
    user = User.query.filter_by(username=username).first()
    if user:
        pass
    else:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()

    return flask.redirect(flask.url_for("login"))


@app.route("/login")
def login():
    return flask.render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    username = flask.request.form.get("username")
    user = User.query.filter_by(username=username).first()
    if user:
        login_user(user)
        return flask.redirect(flask.url_for("index"))

    else:
        return flask.jsonify({"status": 401, "reason": "Username or Password Error"})


@app.route("/save", methods=["POST"])
def save():
    artist_id = flask.request.form.get("artist_id")
    try:
        access_token = get_access_token()
        get_song_data(artist_id, access_token)
    except Exception:
        flask.flash("Invalid artist ID entered")
        return flask.redirect(flask.url_for("index"))

    username = current_user.username
    db.session.add(Artist(artist_id=artist_id, username=username))
    db.session.commit()
    return flask.redirect(flask.url_for("index"))


@app.route("/")
def main():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for("index"))
    return flask.redirect(flask.url_for("login"))


@app.route("/index")
@login_required
def index():
    artists = Artist.query.filter_by(username=current_user.username).all()
    artist_ids = [a.artist_id for a in artists]
    has_artists_saved = len(artist_ids) > 0
    if has_artists_saved:
        artist_id = random.choice(artist_ids)

        # API calls
        access_token = get_access_token()
        (song_name, song_artist, song_image_url, preview_url) = get_song_data(
            artist_id, access_token
        )
        genius_url = get_lyrics_link(song_name)

    else:
        (song_name, song_artist, song_image_url, preview_url, genius_url) = (
            None,
            None,
            None,
            None,
            None,
        )

    return flask.render_template(
        "index.html",
        has_artists_saved=has_artists_saved,
        song_name=song_name,
        song_artist=song_artist,
        song_image_url=song_image_url,
        preview_url=preview_url,
        genius_url=genius_url,
    )


if __name__ == "__main__":
    app.run(
        host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8080)), debug=True
    )
