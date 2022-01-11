import os
import requests
import base64
import random

MARKET = "US"

def get_access_token():
	auth = base64.standard_b64encode(
		bytes(
			f"{os.getenv('SPOTIFY_CLIENT_ID')}:{os.getenv('SPOTIFY_CLIENT_SECRET')}", "utf-8"
		)
	).decode("utf-8")
	response = requests.post(
		"https://accounts.spotify.com/api/token",
		headers={"Authorization": f"Basic {auth}"},
		data={"grant_type": "client_credentials"}
	)
	json_response = response.json()
	return json_response["access_token"]

def get_song_data(artist_id, access_token):
    response = requests.get(
		f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks",
		headers={"Authorization": f"Bearer {access_token}"},
		params={"market": MARKET}
	)
    json_response = response.json()
    track_json = random.choice(json_response["tracks"])  # choose random track
    song_name = track_json["name"]
    song_artist = ", ".join([artist["name"] for artist in track_json["artists"]])
    song_image_url = track_json["album"]["images"][0]["url"]
    preview_url = track_json["preview_url"]
    return (song_name, song_artist, song_image_url, preview_url)

