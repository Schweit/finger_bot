import os
import json
import pickle
import time
from datetime import datetime
from collections import deque

class PlaylistEngine:

    fileName = "playlist_1_7_2022.pickle"
    users = []
    queue = []

    def __init__(self):
        try:
            self.users = pickle.load(open(self.filename, "rb"))
        except (OSError, IOError) as e:
            pickle.dump(self.users, open(self.filename, "wb"))

    def save(self):
        pickle.dump(self.users, self.fileName) 

    def load(self):
        self.users = open(self.fileName, "wb")

    def playlist(self, user, playlistName, song, delete):
        user = self._checkUser(user)
        # if not song and delete:
        #     self._deletePlaylist(user, playlistName)

        # creates a playlist if one doesnt exist
        playlist = self._checkPlaylist(user, playlistName)
        if song and not delete:
            self._addSong(playlist, song)    
        if song and delete:
            self._deleteSong(playlist, song)
        if not song and not delete:
            self._addPlaylist(user, playlist)
        self.save()
       
    # def showPlaylist(self, user):


    # def randomPlay(self, size):

    # def startPlaylist(self, user, playlist, sortType):

    def _checkUser(self, user):
        for u in self.users:
            if u['user'] == user:
                return u
        return self._addUser(user)

    def _addUser(self, user):
        user = self.users.append({
            "user": user,
            "date_time": datetime.utcnow(),
            "active": True,
            "playlists": []
        })
        return user

    def _checkPlaylist(self, user, playListName, song = None):
        for p in self._checkUser(user)['play_lists']:
            if p['name'] == playListName:
                return p
        return self._addPlaylist(user, playListName, song)

    def _addPlaylist(self, user, playlistName, song = None):
        user = self._checkUser(user)
        playlist = user['playlists'].append({
            "name": playlistName,
            "songs": [],
            "date_time_created": datetime.utcnow(),
            "date_time_lastPlayed": None,
            "play_count": 0
        })
        if song:
             self._addSong(playlist, song)
        return playlist

    def _checkSong(self, playlist, song):
        for s in playlist['songs']:
            if s['url'] == song['url']:
                return
        playlist.append(self._addSong(self, song))

    def _addSong(self, song):
        song = {
            "name": song[0],
            "url": song[1],
            "date_time_added": datetime.utcnow(),
            "date_time_lastPlayed": None,
            "play_count": 0
        }

    def _deleteSong(playlist, song):
        del playlist['songs'][song]

    # def _deletePlaylist(user, playlistName):
        # for p in user['playlists']:
        #     if p['name'] == playlistName:
        #         del user['playlists'].remove(p)

    # def _showUsers():


    # def _listToDiscordString(list):
    #     return ""