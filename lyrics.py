import configparser
import os
import re

import requests
import html.parser
from bs4 import BeautifulSoup
from lxml import etree

def getAccessToken():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['Client_Access_Token']['token']

token = getAccessToken()


def searchMusicArtist(name):
    api_url = "https://api.genius.com/search?q={}".format(name)
    headers = {"authorization": token}
    r = requests.get(api_url, headers=headers)
    return r.json()


def getArtistID(name):
    r = searchMusicArtist(name)
    id = r["response"]["hits"][0]["result"]["primary_artist"]["id"]
    return id


def getTopTenSongs(name):
    id = getArtistID(name)
    api_url = "https://api.genius.com/artists/{}/songs".format(id)
    headers = {"authorization": token}
    params = {
        "sort": "popularity",
        "per_page": 10
    }
    r = requests.get(api_url, headers=headers, params=params)
    return r.json()


def getLyricsArray(name):
    r = getTopTenSongs(name)
    songs = r["response"]["songs"]
    lyrics_array = []
    for song in songs:
        lyrics_array.append(song["url"])
    return lyrics_array

def scrapeLyricText(link):
    try:
        song_lyrics = []
        page = requests.get(link)
        html = BeautifulSoup(page.text, 'html.parser')
        lyrics = html.find('div', class_='lyrics').get_text()
        # remove identifiers like chorus, verse, etc
        lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
        # remove empty lines
        lyrics = os.linesep.join([s for s in lyrics.splitlines() if s])
        song_lyrics.append(lyrics)
        return song_lyrics
    except AttributeError:
        return scrapeLyricText(link)

def printLyrics(name):
    song_lyrics = []
    links = getLyricsArray(name)
    for link in links:
        lyrics = scrapeLyricText(link)
        song_lyrics.append(lyrics)
    return song_lyrics


