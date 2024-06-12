from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time


class YandexMusicScraper:
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Chrome()
        self.tracks_and_artists = set()

    def open_page(self):
        self.driver.get(self.url)

    def close_promo_banner(self):
        try:
            close_button = self.driver.find_element(By.CLASS_NAME, "pay-promo-close-btn")
            close_button.click()
            time.sleep(2)
        except NoSuchElementException:
            print("Promo banner not found or already closed.")

    def get_tracks_and_artists(self):
        track_elements = self.driver.find_elements(By.CLASS_NAME, "d-track__name")
        artist_elements = self.driver.find_elements(By.CLASS_NAME, "d-track__artists")
        tracks = [track.text for track in track_elements]
        artists = [artist.text for artist in artist_elements]
        return set(zip(tracks, artists))

    def scrape(self):
        self.open_page()
        self.close_promo_banner()

        scroll_pause_time = 0.1
        scroll_amount = 1000
        current_scroll_position = 0

        while current_scroll_position <= self.driver.execute_script("return document.body.scrollHeight"):
            self.driver.execute_script(f"window.scrollTo(0, {current_scroll_position});")
            current_scroll_position += scroll_amount
            time.sleep(scroll_pause_time)
            current_data = self.get_tracks_and_artists()
            self.tracks_and_artists.update(current_data)

        self.driver.quit()

    def print_results(self):

        for track, artist in self.tracks_and_artists:
            print(f"Track: {track}, Artist: {artist}")

        print(f"Total number of songs: {len(self.tracks_and_artists)}")


if __name__ == "__main__":
    url = "https://music.yandex.ru/users/zokirovrustam202/playlists/3"
    scraper = YandexMusicScraper(url)
    scraper.scrape()
    scraper.print_results()
