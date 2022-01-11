import flask
from flask_login.utils import login_required
import os
import json
import flask
import os
from flask import request
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
from flask_sqlalchemy import SQLAlchemy
import os
from genius import get_lyrics_link
from spotify import get_access_token, get_song_data
import flask
from flask_login import login_user, current_user, LoginManager
import random
import base64
import requests

app = flask.Flask(__name__, static_folder="./build/static")
# Point SQLAlchemy to your Heroku database
db_url = os.getenv("DATABASE_URL")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
# Gets rid of a warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("KEY")

from flask_login import UserMixin

db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))

    def __repr__(self):
        return f"<User {self.username}>"

    def get_username(self):
        return self.username


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.String(80), nullable=False, unique=True)
    username = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"<Artist {self.artist_id}>"

db.create_all()

# This tells our Flask app to look at the results of `npm build` instead of the
# actual files in /templates when we're looking for the index page file. This allows
# us to load React code into a webpage. Look up create-react-app for more reading on
# why this is necessary.
bp = flask.Blueprint("bp", __name__, template_folder="./build")


@bp.route("/index")
@login_required
def index():
    # TODO: insert the data fetched by your app main page here as a JSON
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

    DATA = {
        "has_artists_saved": has_artists_saved,
        "song_name": song_name,
        "song_artist": song_artist,
        "song_image_url": song_image_url,
        "preview_url": preview_url,
        "genius_url": genius_url,
        "username": current_user.username,
        "artist_ids": artist_ids,
    }
    data = json.dumps(DATA)
    return flask.render_template(
        "index.html",
        data=data,
    )


app.register_blueprint(bp)


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
        return flask.redirect(flask.url_for("bp.index"))

    else:
        return flask.jsonify({"status": 401, "reason": "Username or Password Error"})





@app.route("/")
def main():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for("bp.index"))
    return flask.redirect(flask.url_for("login"))


@app.route("/save-songs", methods=["POST"])
@login_required
def save_songs():
    request_data = request.get_json()
    artist_ids = request_data.get("artist_list")
    username = current_user.username
    for artist_id in artist_ids:
        try:
            access_token = get_access_token()
            get_song_data(artist_id, access_token)
        except Exception:
            #return flask.jsonify({"status": 401, "reason": "Username or Password Error"})
            return flask.jsonify({'artist_server': artist_ids},{'message':"artistidnotvalid"})
            #flask.flash(f"Invalid artist ID: {artist_id} entered")
            #return flask.redirect(flask.url_for("bp.index"))
    artist = Artist(username=username, artist_id=artist_id)
    db.session.add(artist)
    db.session.commit()

    return flask.redirect("bp.index")
    #return flask.jsonify({'artist_server': artist_ids})


app.run(
    host=os.getenv("IP", "0.0.0.0"),
    port=int(os.getenv("PORT", 8081)),
)
