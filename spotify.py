import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load .env variables
load_dotenv()

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

if not client_id or not client_secret:
    raise ValueError("Missing Spotify API credentials. Check your .env file!")

# Set up Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def get_spotify_songs(theme):
    results = sp.search(q=theme, limit=10, type='track')
    songs = []
    for track in results['tracks']['items']:
        song = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'external_url': track['external_urls']['spotify'],
            'image_url': track['album']['images'][0]['url']
        }
        songs.append(song)
    return songs
