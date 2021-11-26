"""
Input: Gets as the link of the playlist from Yandex Music
like (https://music.yandex.com/users/zokirovrustam202@gmail.com/playlists/3).
Then using the web scrapper, get all song names from the playlist.

Output: Data is saved in CSV  (FOR Prototype #1, use Kafka soon, if we want the synchronization,
between the accounts.)

NOTEs:
10K problem solved, input playlist can have only 10K, so output will also have 10K.

# ONLY Works with 100 songs, because scrapping loads only 100 songs
"""
import requests
from bs4 import BeautifulSoup
import json
import csv
import os
from threading import Thread


class Scrapper:
    user_id = "314vqpqyrdpvs5uyer22bbusxcoq"
    counter = 0
    token = "BQACxRP4AtgWSDj0Dpn0gAcUG0adiOEm5HeDKWrn2NJGBeqidBJXEuh76UK64ChtFwUYbf4mJdSYt4vkCnGne3DyK6x19CBx4AemAZ-EIhJw1HhstcsSjvtCjtq_1Glil7kgu5eGisPXLDSOGBG3KNPuQIkJBrOfMW4TGDq1jVxVt7xOqohP9qbROXy1mpFHWf8w2k_v2WI8UIqS62PZeAuVrlc352Ne"
    number_of_songs = 0
    uris = []

    def __init__(self, playlist_url: str):
        self.playlist_url = playlist_url

    def get_page_content(self):
        page = requests.get(self.playlist_url)
        return page

    def get_playlist_songs(self):
        page = self.get_page_content()
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all("div", class_="d-track__overflowable-column")

        # Remove data.csv before appending to it
        file = 'data.csv'
        if os.path.exists(file) and os.path.isfile(file):
            os.remove(file)

        # Kafka
        for result in results:
            title_element = result.find("div", class_="d-track__name").text.strip()
            author_element = result.find("span", class_="d-track__artists").text.strip()
            self.number_of_songs += 1

            with open(file, 'a') as f:
                writer = csv.writer(f)
                writer.writerow([title_element, author_element])
        # print(self.number_of_songs)

    def create_spotify_playlist(self):
        endpoint_url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"
        request_body = json.dumps({
            "name": f"Playlist #{self.playlist_url}",
            "description": "Welcome to playlist generated with programming code!",
            "public": True
        })
        response = requests.post(url=endpoint_url, data=request_body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {self.token}"})

        playlist_id = response.json()['id']
        url = response.json()['external_urls']['spotify']  # Spotify playlist URL

        return playlist_id, url

    def get_songs_uri(self):
        endpoint_url = f"https://api.spotify.com/v1/search"

        with open("data.csv", 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                track = row[0]
                artist = row[1]
                response = requests.get(
                    endpoint_url,
                    headers={"Content-Type": "application/json",
                             "Authorization": f"Bearer {self.token}"},
                    params={'q': track, 'type': 'track', 'limit': 1})

                json_response = response.json()
                print(json_response)  # if 404 error, then The access token expired
                arr = json_response["tracks"]["items"]
                for item in arr:
                    uri = item['uri']
                    self.uris.append(uri)

        # print(self.uris)  # Need to be done Kafka, start using the content of list, even appending is not finished

    def add_tracks_to_playlist(self):
        playlist_info = self.create_spotify_playlist()

        spotify_playlist_id, spotify_playlist_url = playlist_info[0], playlist_info[1]
        print(spotify_playlist_id, spotify_playlist_url, self.uris)

        endpoint_url = f"https://api.spotify.com/v1/playlists/{spotify_playlist_id}/tracks"

        request_body = json.dumps({
            "uris": self.uris
        })
        response = requests.post(url=endpoint_url, data=request_body, headers={"Content-Type": "application/json",
                                                                               "Authorization": f"Bearer {self.token}"})

        print(response.status_code)
        print(f'Your playlist is ready at {spotify_playlist_url}')


if __name__ == '__main__':
    playlist_url_big = "https://music.yandex.com/users/asadbek1khasanov@gmail.com/playlists/3"
    playlist_url = "https://music.yandex.com/users/asadbek1khasanov@gmail.com/playlists/1001"

    scrapper = Scrapper(playlist_url_big)
    scrapper.get_playlist_songs()
    scrapper.get_songs_uri()
    scrapper.add_tracks_to_playlist()
    #     Thread(target = func1).start()
    #     Thread(target = func2).start()

