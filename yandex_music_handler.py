import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from helpers import BasePage
from logger import logger


class YandexMusicHandler(BasePage):
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

    def get_tracks_and_artists(self) -> set[tuple]:
        """
        Get the tracks and artists list from the page.
        """
        self.open_page(self.url)
        self._close_promo_banner()
        tracks = self._parse_tracks_and_artists_with_scroll()
        return tracks

    def _parse_tracks_and_artists_with_scroll(self) -> set:
        """
        Get ALL the tracks and artists list using scrolling.
        """
        scroll_pause_time = 0.1
        scroll_amount = 1000
        current_scroll_position = 0

        tracks_and_artists = set()
        while current_scroll_position <= self.driver.execute_script("return document.body.scrollHeight"):
            self.driver.execute_script(f"window.scrollTo(0, {current_scroll_position});")
            current_scroll_position += scroll_amount
            time.sleep(scroll_pause_time)

            current_data = self._parse_tracks_and_artists()
            tracks_and_artists.update(current_data)

        return tracks_and_artists

    def _close_promo_banner(self):
        try:
            close_button = self.driver.find_element(*self.locators["close_button"])
            close_button.click()
            self._wait_until_playlist_image_loads()
        except NoSuchElementException:
            logger.warning("Promo banner not found or already closed.")

    def _parse_tracks_and_artists(self):
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


if __name__ == "__main__":
    _url = "https://music.yandex.ru/users/zokirovrustam202/playlists/3"
    _driver = webdriver.Chrome()

    _scraper = YandexMusicHandler(_driver, _url)
    _tracks = _scraper.get_tracks_and_artists()
    print(_tracks)
    print(len(_tracks))

    _driver.quit()
