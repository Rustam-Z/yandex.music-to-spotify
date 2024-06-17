import json
import os

import requests
from decouple import config

from config import SPOTIFY_AUTH_API_HOST, SPOTIFY_API_HOST
from utils.helpers import HttpClient
from utils.logger import logger
from utils.utils import clean_string


class SpotifyAPI:
    HTTP_HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(self, host: str):
        self._http_client = HttpClient(host)
        self._http_client.remove_all_headers()
        self._http_client.update_headers(self.HTTP_HEADERS)

    def authenticate(self, *, token: str) -> "SpotifyAPI":
        headers = {"Authorization": f"Bearer {token}"}
        self._http_client.update_headers(headers)
        return self

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
        data = json.dumps(
            {
                "name": f"Playlist #{os.urandom(25).hex()}",
                "public": True,
            }
        )
        response = self._http_client.make_request("POST", url, data=data)
        return response

    def get_playlists(self, user_id: str):
        url = self._http_client.build_url(f"users/{user_id}/playlists")
        response = self._http_client.make_request("GET", url)
        return response

    def search_track(self, track: str, artist: str, limit: int = 1):
        url = self._http_client.build_url("search")
        response = self._http_client.make_request(
            "GET",
            url,
            params={
                "q": f"track: {track} artist:{artist}",
                "type": "track",
                "limit": limit,
            },
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
        try:
            response = self.api.get_user_id()
            return response.data.get("id")
        except Exception as e:
            logger.error(f"Error occurred while fetching user ID: {e}")

    def create_playlist(self):
        try:
            response = self.api.create_playlist(user_id=self.user_id)
            return response.data.get("id")
        except Exception as e:
            logger.error(f"Error occurred while creating playlist: {e}")

    def get_track_uri(self, track_name: str, artist: str):
        try:
            response = self.api.search_track(track=track_name, artist=artist, limit=10)
            spotify_track = self.get_matching_track(
                response.data.get("tracks"), track_name, artist
            )

            if not spotify_track:
                return

            return spotify_track.get("uri")
        except Exception as e:
            logger.error(f"Error occurred while searching track: {e}")

    def add_tracks_to_playlist(self, playlist_id: str, uris: list):
        try:
            response = self.api.add_tracks_to_playlist(
                playlist_id=playlist_id, uris=uris
            )
            return response
        except Exception as e:
            logger.error(f"Error occurred while adding tracks to playlist: {e}")

    @staticmethod
    def get_matching_track(tracks: dict, track_name: str, artist: str):
        for spotify_track in tracks.get("items"):
            search_track_name = spotify_track["name"]
            search_artist = spotify_track["artists"][0]["name"]

            normalized_track_name = set(clean_string(track_name).split())
            normalized_search_track_name = set(clean_string(search_track_name).split())
            normalized_artist = set(clean_string(artist).split())
            normalized_search_artist = set(clean_string(search_artist).split())

            if not normalized_track_name.isdisjoint(
                normalized_search_track_name
            ) and not normalized_artist.isdisjoint(normalized_search_artist):
                return spotify_track

        return None


if __name__ == "__main__":
    _spotify_api = SpotifyAPI(host=SPOTIFY_API_HOST).authenticate(
        token=config("SPOTIFY_TOKEN")
    )
    _spotify_client = SpotifyClient(api=_spotify_api)
    _track_uri = _spotify_client.get_track_uri(
        track_name="Believer", artist="Imagine Dragons"
    )
    print(_track_uri)
