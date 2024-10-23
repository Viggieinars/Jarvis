import spotipy
from spotipy.oauth2 import SpotifyOAuth
from speech import Speech
from ellab import ElevenLabsController
import os
import random
import speech_recognition as sr

class SpotifyController:
    def __init__(self, name, fancy_voice):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                                                            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
                                                            redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
                                                            scope="user-library-read,user-modify-playback-state,user-read-playback-state"))
        self.speech = Speech(name)
        self.name = name
        self.ellab = ElevenLabsController(name)
        self.fancy_voice = fancy_voice

    def play_music(self, song_name, artist_name):
        self._speak('Playing music on Spotify.')
        search_query = f"{song_name} {artist_name}".strip()
        self.search_and_play(search_query)

    def shuffle_liked_songs(self):
        results = self.sp.current_user_saved_tracks(limit=50)
        if not results['items']:
            self._speak('No liked songs found.')
            return

        liked_tracks = [item['track']['uri'] for item in results['items']]
        random.shuffle(liked_tracks)

        devices = self.sp.devices()
        if not devices['devices']:
            self._speak('No active Spotify devices found. Please start playing Spotify on one of your devices and try again.')
            return

        active_device_id = devices['devices'][0]['id']

        try:
            self.sp.start_playback(device_id=active_device_id, uris=liked_tracks)
            self._speak('Shuffling and playing your liked songs.')
        except spotipy.exceptions.SpotifyException as e:
            self._speak('Failed to start playback on the active device.')
            print(e)

    def search_and_play(self, search_query):
        devices = self.sp.devices()
        if not devices['devices']:
            self._speak('No active Spotify devices found. Please start playing Spotify on one of your devices and try again.')
            return

        active_device_id = devices['devices'][0]['id']

        results = self.sp.search(q=search_query, type='track,album,playlist', limit=1)

        if results['albums']['items']:
            item = results['albums']['items'][0]
            try:
                self.sp.start_playback(device_id=active_device_id, context_uri=item['uri'])
                self._speak(f'Playing {item["name"]} by {item["artists"][0]["name"]}')
            except spotipy.exceptions.SpotifyException as e:
                self._speak('Failed to start playback on the active device.')
                print(e)
            return
        elif results['tracks']['items']:
            item = results['tracks']['items'][0]
            try:
                self.sp.start_playback(device_id=active_device_id, uris=[item['uri']])
                self._speak(f'Playing track {item["name"]} by {item["artists"][0]["name"]}')
            except spotipy.exceptions.SpotifyException as e:
                self._speak('Failed to start playback on the active device.')
                print(e)
            return
        elif results['playlists']['items']:
            item = results['playlists']['items'][0]
            try:
                self.sp.start_playback(device_id=active_device_id, context_uri=item['uri'])
                self._speak(f'Playing playlist {item["name"]}')
            except spotipy.exceptions.SpotifyException as e:
                self._speak('Failed to start playback on the active device.')
                print(e)
            return

        self._speak('I could not find the song, playlist, or album you requested.')

    def pause_music(self):
        self._speak('Pausing music on Spotify.')

        devices = self.sp.devices()
        if not devices['devices']:
            self._speak('No active Spotify devices found. Please start playing Spotify on one of your devices and try again.')
            return

        active_device_id = devices['devices'][0]['id']

        try:
            self.sp.pause_playback(device_id=active_device_id)
            self._speak('Music paused.')
        except spotipy.exceptions.SpotifyException as e:
            self._speak('Failed to pause playback on the active device.')
            print(e)

    def _speak(self, text):
        if not self.fancy_voice:
            self.speech.speak(text)
        else:
            self.ellab.speak(text)
