from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def open_page(self, url):
        self.driver.get(url)


class YandexMusicHandler(BasePage):
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
            close_button = self.driver.find_element(By.CLASS_NAME, "pay-promo-close-btn")
            close_button.click()
            time.sleep(2)  # TODO: Replace with wait until content is loaded in next step.
        except NoSuchElementException:
            print("Promo banner not found or already closed.")

    def _parse_tracks_and_artists(self):
        """
        Get the tracks and artists from the page in current scroll position.
        To fetch the list of all tracks and artists scrape() function should be used.
        """
        track_elements = self.driver.find_elements(By.CLASS_NAME, "d-track__name")
        artist_elements = self.driver.find_elements(By.CLASS_NAME, "d-track__artists")
        tracks = [track.text for track in track_elements]
        artists = [artist.text for artist in artist_elements]
        return set(zip(tracks, artists))


if __name__ == "__main__":
    _url = "https://music.yandex.ru/users/zokirovrustam202/playlists/3"
    _driver = webdriver.Chrome()

    _scraper = YandexMusicHandler(_driver, _url)
    tracks = _scraper.get_tracks_and_artists()
    print(tracks)
    print(len(tracks))

    _driver.quit()
