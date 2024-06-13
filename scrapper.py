from selenium import webdriver

from config import SPOTIFY_API_HOST, SPOTIFY_TOKEN
from logger import logger
from spotify_handler import SpotifyAPI, SpotifyClient
from yandex_music_handler import YandexMusicClient


def main():
    _url = "https://music.yandex.ru/users/zokirovrustam202/playlists/3"
    _driver = webdriver.Chrome()

    try:
        _yandex_music_client = YandexMusicClient(_driver, _url)
        _spotify_api = SpotifyAPI(host=SPOTIFY_API_HOST)
        _spotify_api.authenticate(token=SPOTIFY_TOKEN)
        _spotify_client = SpotifyClient(api=_spotify_api)

        tracks = _yandex_music_client.get_tracks_and_artists()
        logger.info(f"Number of tracks: {len(tracks)}")
        logger.info(f"Tracks: {tracks}")

        spotify_playlist_id = _spotify_client.create_playlist()
        logger.info(f"Spotify playlist ID: {spotify_playlist_id}")

        for track, artist in tracks:
            track_uri = _spotify_client.get_track_uri(track=track, artist=artist)
            _spotify_client.add_tracks_to_playlist(playlist_id=spotify_playlist_id, uris=[track_uri])
            logger.info(f"Track {track} by {artist} added to Spotify playlist")

    finally:
        _driver.quit()


if __name__ == "__main__":
    main()
