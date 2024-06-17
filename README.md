# Yandex.Music to Spotify
Easily move Yandex Music playlist songs to Spotify playlist.

## How to use?
- Pre-requisites:
  - Have a public Yandex Music playlist.
  - Have a Spotify account.
- Create `.env` file. Copy the content from `.env.example` and update the values.
  - Spotify token: to get it inspect the Spotify page, and get Authorization header in Network Tab, remove "Bearer" word.
- How to run the script? Put the URL of the Yandex Music playlist in the command below in `--url` parameter.
  ```
  python script_name.py --url "https://music.yandex.com/users/<PLAYLIST>"
  ```

## How it works?
- The script reads the Yandex Music playlist via parsing track name and artist name using Selenium.
- Then, a Spotify playlist is created, script searches the track on Spotify and adds it to the Spotify playlist. 
- If some songs, cannot be found in Spotify, you will see in console output as `NOT FOUND`.

## Limitations
- Spotify token must be manually updated. What they describe https://developer.spotify.com/documentation/web-api/tutorials/getting-started#request-an-access-token is not working.
- The Yandex Music songs that don't exist in Spotify will not be added to the Spotify playlist.
- After playlist is moved from Yandex Music to Spotify, songs are not synchronized. If you add new songs to Yandex Music playlist, you will have to run the script again to move the new songs to Spotify.
