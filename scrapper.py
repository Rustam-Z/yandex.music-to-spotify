import argparse
import concurrent.futures

from selenium import webdriver

from config import SPOTIFY_API_HOST, SPOTIFY_TOKEN
from spotify_handler import SpotifyAPI, SpotifyClient
from utils.logger import logger
from yandex_music_handler import YandexMusicClientHandler


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scrape tracks from Yandex Music and add them to a Spotify playlist."
    )
    parser.add_argument(
        "--url", type=str, required=True, help="URL of the Yandex Music playlist"
    )
    return parser.parse_args()


def add_track_to_spotify(track, spotify_client, playlist_id):
    track_name, artist = track
    track_uri = spotify_client.get_track_uri(
        track_name=track_name,
        artist=artist,
        search_query_type=3
    )

    if not track_uri:
        logger.error(f"NOT FOUND: '{track_name}' by '{artist}' not found on Spotify.")
        return False

    spotify_client.add_tracks_to_playlist(playlist_id=playlist_id, uris=[track_uri])
    logger.info(f"SUCCESS: '{track_name}' by '{artist}' added to Spotify playlist.")
    return True


def main(url: str):
    with YandexMusicClientHandler(webdriver.Chrome(), url) as _scraper:
        tracks = _scraper.get_tracks_and_artists(use_cache=True)
        logger.info(f"Number of tracks: {len(tracks)}")
        logger.info(f"Tracks: {tracks}")

    _spotify_api = SpotifyAPI(host=SPOTIFY_API_HOST).authenticate(token=SPOTIFY_TOKEN)
    _spotify_client = SpotifyClient(api=_spotify_api)
    spotify_playlist_id = _spotify_client.create_playlist()
    logger.info(f"Spotify playlist ID: {spotify_playlist_id}")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(
            executor.map(
                add_track_to_spotify,
                tracks,
                [_spotify_client] * len(tracks),
                [spotify_playlist_id] * len(tracks),
            )
        )

    success = sum(results)
    failed = len(results) - success

    logger.info(f"Total tracks added: {success}")
    logger.info(f"Total tracks failed: {failed}")


if __name__ == "__main__":
    args = parse_args()
    main(args.url)
