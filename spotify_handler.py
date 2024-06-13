import csv
import json
import os
from typing import Optional

import requests
from decouple import config

from helpers import HttpClient

SPOTIFY_API_HOST = "https://api.spotify.com/v1"
SPOTIFY_AUTH_API_HOST = "https://accounts.spotify.com/api/token"


class SpotifyAPI:
    HTTP_HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(self, host: str):
        self._http_client = HttpClient(host)
        self._http_client.remove_all_headers()
        self._http_client.update_headers(self.HTTP_HEADERS)

    def authenticate(self, *, token: str) -> None:
        headers = {"Authorization": f"Bearer {token}"}
        self._http_client.update_headers(headers)

    def get_access_token(self, client_id: str, client_secret: str):
        """
        Reference: https://developer.spotify.com/documentation/web-api/tutorials/getting-started#request-an-access-token

        NOTRE! You must have valid client_id and client_secret to get the access token.
               But if you follow official Spotify documentation, it is not working.
        """
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(SPOTIFY_AUTH_API_HOST, headers=headers, data=data)
        return response

    def get_user_id(self):
        """
        Reference: https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile

        NOTE! This endpoint may return a 401 Unauthorized error. So, manually fetch the user ID, and save in .env file.
        """
        url = self._http_client.build_url("me")
        response = self._http_client.make_request("GET", url)
        return response

    def create_playlist(self, user_id: str):
        url = self._http_client.build_url(f"users/{user_id}/playlists")
        data = json.dumps({
            "name": f"Playlist #{os.urandom(25).hex()}",
            "public": True,
        })
        response = self._http_client.make_request("POST", url, data=data)
        return response

    def get_playlists(self, user_id: str):
        url = self._http_client.build_url(f"users/{user_id}/playlists")
        response = self._http_client.make_request("GET", url)
        return response

    def search_track(self, track: str, artist: str):
        url = self._http_client.build_url("search")
        response = self._http_client.make_request(
            "GET",
            url,
            params={"q": f"track%3A{track}%2520artist{artist}", "type": "track", "limit": 1}
        )
        return response

    def add_tracks_to_playlist(self, playlist_id: str, uris: list):
        url = self._http_client.build_url(f"playlists/{playlist_id}/tracks")
        data = json.dumps({"uris": uris})
        response = self._http_client.make_request("POST", url=url, data=data)
        return response


class SpotifyClient:
    def __init__(self, api: SpotifyAPI):
        self.api = api
        self.user_id = self.get_user_id()

    def get_user_id(self):
        response = self.api.get_user_id()
        return response.data.get("id")

    def create_playlist(self):
        response = self.api.create_playlist(user_id=self.user_id)
        return response.data.get("id")

    def get_track_uri(self, track: str, artist: str):
        response = self.api.search_track(track=track, artist=artist)
        return response.data.get("tracks").get("items")[0].get("uri")


if __name__ == "__main__":
    _spotify_api = SpotifyAPI(host=SPOTIFY_API_HOST)
    _spotify_api.authenticate(token=config("SPOTIFY_TOKEN"))
    _spotify_client = SpotifyClient(api=_spotify_api)
    _track_uri = _spotify_client.get_track_uri(track="Believer", artist="Imagine Dragons")
    print(_track_uri)
