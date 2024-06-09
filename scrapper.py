import csv
import json
import os
from typing import Optional

import requests
from bs4 import BeautifulSoup
from decouple import config


class YandexMusicHandler:
    def __init__(self, playlist_url: str):
        self.playlist_url = playlist_url

    def get_playlist_songs(self):
        ...

    def save_playlist_into_file(self, file=".data.csv") -> str:
        if os.path.exists(file) and os.path.isfile(file):
            os.remove(file)

        html_page = self._get_page_content()
        html_parser = BeautifulSoup(html_page.content, "html.parser")
        results = html_parser.find_all("div", class_="d-track__overflowable-column")

        number_of_songs = 0
        for result in results:
            title_element = result.find("div", class_="d-track__name").text.strip()
            author_element = result.find("span", class_="d-track__artists").text.strip()
            number_of_songs += 1

            with open(file, "a") as f:
                writer = csv.writer(f)
                writer.writerow([title_element, author_element])

        return f"Number of processed songs: {number_of_songs}. File: {file}"

    def _get_page_content(self):
        page = requests.get(self.playlist_url)
        return page


class SpotifyHandler:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        api_host: Optional[str] = "https://api.spotify.com/v1",
    ):
        self.api_host = api_host
        self.client_id = client_id
        self.client_secret = client_secret
        self.uris = []

        # TMP
        self.token = config("SPOTIFY_TOKEN")
        self.user_id = config("SPOTIFY_USER_ID")

    def get_access_token(self):
        ...

    def get_user_id(self):
        ...

    def create_playlist(self):
        endpoint_url = f"{self.api_host}/users/{self.user_id}/playlists"
        request_body = {
            "name": f"Playlist #{os.urandom(25).hex()}",
            "public": True,
        }
        response = requests.post(
            url=endpoint_url,
            json=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
        )

        playlist_id = response.json()["id"]
        url = response.json()["external_urls"]["spotify"]  # Spotify playlist URL

        return playlist_id, url

    def search_songs(self):
        endpoint_url = f"https://api.spotify.com/v1/search"

        with open("data.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                track = row[0]
                artist = row[1]
                response = requests.get(
                    endpoint_url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.token}",
                    },
                    params={"q": track, "type": "track", "limit": 1},
                )

                json_response = response.json()
                print(json_response)  # if 404 error, then The access token expired
                arr = json_response["tracks"]["items"]
                for item in arr:
                    uri = item["uri"]
                    self.uris.append(uri)

        # print(self.uris)  # Need to be done Kafka, start using the content of list, even appending is not finished

    def add_songs_to_playlist(self):
        playlist_info = self.create_playlist()

        spotify_playlist_id, spotify_playlist_url = playlist_info[0], playlist_info[1]
        print(spotify_playlist_id, spotify_playlist_url, self.uris)

        endpoint_url = (
            f"https://api.spotify.com/v1/playlists/{spotify_playlist_id}/tracks"
        )

        request_body = json.dumps({"uris": self.uris})
        response = requests.post(
            url=endpoint_url,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
        )

        print(response.status_code)
        print(f"Your playlist is ready at {spotify_playlist_url}")


if __name__ == "__main__":
    _playlist_url = "https://music.yandex.com/users/zokirovrustam202@gmail.com/playlists/3"
    yandex_music = YandexMusicHandler(_playlist_url)
    yandex_music.save_playlist_into_file()

    # scrapper = Scrapper(_playlist_url)
    # scrapper.get_playlist_songs()
    # scrapper.get_songs_uri()
    # scrapper.add_tracks_to_playlist()
