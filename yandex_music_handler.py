import os
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from utils.helpers import BasePage
from utils.logger import logger


class YandexMusicClient(BasePage):
    """
    Example usage:
        _url = "https://music.yandex.ru/users/zokirovrustam202/playlists/3"
        _driver = webdriver.Chrome()

        _scraper = YandexMusicHandler(_driver, _url)
        tracks = _scraper.get_tracks_and_artists()
        print(tracks)
        print(len(tracks))

        _driver.quit()
    """

    locators = {
        "close_button": (By.CLASS_NAME, "pay-promo-close-btn"),
        "track_name": (By.CLASS_NAME, "d-track__name"),
        "track_artist": (By.CLASS_NAME, "d-track__artists"),
        "playlist_image": (By.CLASS_NAME, "playlist-cover__img"),
    }

    def __init__(self, driver, url):
        super().__init__(driver)
        self.url = url

    def get_tracks_and_artists(self, use_cache=False) -> list:
        """
        Get the tracks and artists list from the page.
        """

        if use_cache and os.path.exists(".tracks.csv"):
            with open(".tracks.csv", "r") as f:
                tracks = f.readlines()
                return [track.split("|||") for track in tracks]

        self.open_page(self.url)
        self._close_promo_banner()
        tracks = self._parse_tracks_and_artists_with_scroll()

        # Save to csv file and use ||| as separator.
        with open(".tracks.csv", "w") as f:
            f.write(
                "\n".join(
                    [
                        f"{track.replace('\n', '')}|||{artist.replace('\n', '')}"
                        for track, artist in tracks
                    ]
                )
            )

        return tracks

    def _parse_tracks_and_artists_with_scroll(self, scroll_amount: int = 1500) -> list:
        """
        Get ALL the tracks and artists list using scrolling.
        """
        scroll_pause_time = 0.2
        current_scroll_position = 0

        tracks_and_artists = set()
        while current_scroll_position <= self.driver.execute_script(
            "return document.body.scrollHeight"
        ):
            self.driver.execute_script(
                f"window.scrollTo(0, {current_scroll_position});"
            )
            current_scroll_position += scroll_amount
            time.sleep(scroll_pause_time)

            current_data = self._parse_tracks_and_artists()
            tracks_and_artists.update(current_data)

        return list(tracks_and_artists)

    def _close_promo_banner(self) -> None:
        try:
            close_button = self.driver.find_element(*self.locators["close_button"])
            close_button.click()
            self._wait_until_playlist_image_loads()
        except NoSuchElementException:
            logger.warning("Promo banner not found or already closed.")

    def _parse_tracks_and_artists(self) -> set:
        """
        Get the tracks and artists from the page in current scroll position.
        To fetch the list of all tracks and artists scrape() function should be used.
        """
        track_elements = self.driver.find_elements(*self.locators["track_name"])
        artist_elements = self.driver.find_elements(*self.locators["track_artist"])
        tracks = [track.text for track in track_elements]
        artists = [artist.text for artist in artist_elements]
        return set(zip(tracks, artists))

    def _wait_until_playlist_image_loads(self, timeout: int = 10):
        """
        Wait until the playlist image is loaded. Use explicit wait.
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.locators["playlist_image"])
            )
            return element
        except TimeoutException:
            logger.warning("Timeout: Playlist image not found.")


class YandexMusicClientHandler:
    def __init__(self, driver, url):
        self.driver = driver
        self.url = url

    def __enter__(self):
        return YandexMusicClient(self.driver, self.url)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()


if __name__ == "__main__":
    _url = "https://music.yandex.ru/users/zokirovrustam202/playlists/3"
    _driver = webdriver.Chrome()

    with YandexMusicClientHandler(_driver, _url) as _scraper:
        _tracks = _scraper.get_tracks_and_artists(use_cache=False)
        print(_tracks)
        print(len(_tracks))
