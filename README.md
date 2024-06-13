# Yandex.Music to Spotify
Easily move Yandex Music playlist songs to Spotify. 

## How to use?
- Create app on Spotify and get the client id and client secret.
- Create `.env` file. Copy the content from `.env.example` and update the values.
  - To get Spotify Access Token, follow the instructions here https://developer.spotify.com/dashboard/login.

## How it works?
- The script reads the Yandex Music playlist via parsing track name and artist name using Selenium.
- Then, a Spotify playlist is created, then script searches the track on Spotify and adds it to the Spotify playlist.

## Limitations
- After playlist is moved from Yandex Music to Spotify, songs are not synchronized. If you add new songs to Yandex Music playlist, you will have to run the script again to move the new songs to Spotify.
- The Yandex Music songs that don't exist in Spotify will not be added to the Spotify playlist.

## Todo
- Create a web app to make script more interactive.
