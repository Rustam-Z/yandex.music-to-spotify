# Yandex.Music to Spotify
Easily move Yandex Music playlist songs to Spotify. 

## How to use?
- Have a public Yandex Music playlist.
- Create `.env` file. Copy the content from `.env.example` and update the values.
  - To get Spotify token, inspect the page, and get Authorization header in Network Tab.
- Update playlist URl in `scrapper.py` and run `python scrapper.py`.

## How it works?
- The script reads the Yandex Music playlist via parsing track name and artist name using Selenium.
- Then, a Spotify playlist is created, script searches the track on Spotify and adds it to the Spotify playlist.

## Limitations
- Spotify token must be manually updated. What they describe https://developer.spotify.com/documentation/web-api/tutorials/getting-started#request-an-access-token is not working.
- The Yandex Music songs that don't exist in Spotify will not be added to the Spotify playlist.
- After playlist is moved from Yandex Music to Spotify, songs are not synchronized. If you add new songs to Yandex Music playlist, you will have to run the script again to move the new songs to Spotify.
