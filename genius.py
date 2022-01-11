import os
import requests

def get_lyrics_link(song_name):
    """
    Given a song name, query Genius using the search API and return a link to the top
    result.
    """
    genius_response = requests.get(
		"https://api.genius.com/search",
		headers={"Authorization": f"Bearer {os.getenv('GENIUS_AUTH_TOKEN')}"},
		params={"q": song_name}
	)
    genius_response_json = genius_response.json()
    genius_url = genius_response_json["response"]["hits"][0]["result"]["url"]
    return genius_url