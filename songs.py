"""
This module provides functionality for searching songs and downloading them and their lyrics from YouTube and Genius.
"""

from typing import List
import warnings

from dotenv import dotenv_values
from lyricsgenius import Genius
from yt_dlp import YoutubeDL


warnings.simplefilter(action="ignore", category=FutureWarning)
ACCESS_TOKEN = dotenv_values()["GENIUS_CLIENT_ACCESS_TOKEN"]
_genius = Genius(ACCESS_TOKEN)
_genius.verbose = False
_genius.remove_section_headers = True
_genius.skip_non_songs = False

_genius.excluded_terms = ["(Remix)", "(Live)"]


def search_song(fuzzy_song_name: str) -> List[str]:
    """
    This function searches for songs on Genius using a fuzzy song name.

    Args:
        fuzzy_song_name (str): The name of the song to search for, which can be a partial or fuzzy match.

    Returns:
        List[str]: A list of song titles that match the search query.
    """

    return [
        record["result"]["full_title"].replace("\xa0", " ")
        for record in _genius.search_songs(fuzzy_song_name)["hits"]
        if record["type"] == "song"
    ]


def get_song_lyrics(song_name: str) -> str | None:
    """
    This function retrieves the lyrics of a song from Genius.

    Args:
        song_name (str): The name of the song for which to retrieve the lyrics.

    Returns:
        str | None: The lyrics of the song if found, otherwise None.
    """

    song = _genius.search_song(song_name)
    return "\n".join(song.lyrics.split("\n")[1:]) if song else None


def download_song(song_name: str) -> str:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "data/temp",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }

    search_query = f"ytsearch:{song_name}"

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([search_query])

    return "data/temp.mp3"


def select_song() -> str:
    """
    This function allows the user to select a song from a list of songs.

    Returns:
        str: The name of the selected song.
    """

    song_name = input("Enter the name of the song: ")
    songs = search_song(song_name)

    print("0. Exit")
    for i, song in enumerate(songs):
        print(f"{i + 1}. {song}")

    index = int(input("Select a song by number: "))

    while index < 0 or index >= len(songs):
        print("Invalid selection. Please try again.")
        index = int(input("Select a song by number: "))

    if index == 0:
        print("Exiting...")
        exit()

    return songs[index - 1]
