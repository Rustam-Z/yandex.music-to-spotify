from selenium import webdriver

from config import SPOTIFY_API_HOST, SPOTIFY_TOKEN
from utils.logger import logger
from spotify_handler import SpotifyAPI, SpotifyClient
from yandex_music_handler import YandexMusicClientHandler


def main():
    _url = "https://music.yandex.ru/users/<PLAYLIST>"
    _driver = webdriver.Chrome()

    with YandexMusicClientHandler(_driver, _url) as _scraper:
        tracks = _scraper.get_tracks_and_artists(use_cache=True)
        logger.info(f"Number of tracks: {len(tracks)}")
        logger.info(f"Tracks: {tracks}")

    _spotify_api = SpotifyAPI(host=SPOTIFY_API_HOST).authenticate(token=SPOTIFY_TOKEN)
    _spotify_client = SpotifyClient(api=_spotify_api)
    spotify_playlist_id = _spotify_client.create_playlist()
    logger.info(f"Spotify playlist ID: {spotify_playlist_id}")

    failed = 0
    success = 0
    for track_name, artist in tracks:
        track_uri = _spotify_client.get_track_uri(track_name=track_name, artist=artist)

        if not track_uri:
            logger.error(f"NOT FOUND: no tracks found for the query: {track_name} by {artist}")
            failed += 1
            continue

        _spotify_client.add_tracks_to_playlist(playlist_id=spotify_playlist_id, uris=[track_uri])
        logger.info(f"SUCCESS: Track {track_name} by {artist} added to Spotify playlist.")
        success += 1

    logger.info(f"Total tracks added: {success}")
    logger.info(f"Total tracks failed: {failed}")


if __name__ == "__main__":
    main()
