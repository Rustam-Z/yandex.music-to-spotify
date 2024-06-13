from decouple import config

SPOTIFY_API_HOST = "https://api.spotify.com/v1"
SPOTIFY_AUTH_API_HOST = "https://accounts.spotify.com/api/token"
SPOTIFY_TOKEN = config("SPOTIFY_TOKEN")
