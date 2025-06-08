"""
This module fetches and processes Overwatch character quotes from the Overwatch Fandom wiki.
"""

from urllib.parse import unquote
from typing import List
from io import BytesIO
import json
import re
import os

from pydub import AudioSegment
import requests as req
import bs4 as bs

from models import Quote


def _get_pages() -> List[str]:
    """
    Fetches the pages containing Overwatch character quotes.

    Returns:
        List[str]: A list of URLs to the pages containing character quotes.
    """

    res = req.get("https://overwatch.fandom.com/wiki/Category:Quotations")
    soup = bs.BeautifulSoup(res.text, "html.parser")
    links = soup.select(".mw-category-group a")

    return [
        f"https://overwatch.fandom.com{link.get('href')}"
        for link in links
        if not any(
            black_word in link.text
            for black_word in [
                "Overwatch 1",
                "Antarctic",
                "Athena",
                "Echo",
                "Busan",
                "Cosmic Crisis",
                "HAL-Fred Glitchbot",
                "Horizon Lunar Colony",
                "Junkenstein's Revenge",
                "Luna",
                "Lúcioball",
                "Midtown",
                "New Junk City",
                "Numbani",
                "Paris",
                "Samoa",
                "Retribution",
                "Skin-Specific",
                "Stadium Announcer",
                "Storm Rising",
                "Training bot",
                "TS-1",
                "Uprising",
                "Volskaya Industries",
                "Wrath of the Bride",
                "sandbox",
            ]
        )
        and link.get("href").endswith("Quotes")
    ]


def _download_audio(id: str, url: str) -> str:
    """
    Downloads an audio file from a given URL and saves it as an MP3 file.

    Args:
        id (str): A unique identifier for the audio file, used to create a filename.
        url (str): The URL of the audio file to be downloaded.

    Returns:
        str: The path where the MP3 file is saved.
    """

    res = req.get(url)
    ogg_audio = AudioSegment.from_ogg(BytesIO(res.content))

    os.makedirs("data/audios", exist_ok=True)
    path = f"data/audios/{id}.mp3"
    ogg_audio.export(path, format="mp3")
    return path


def _download_character_image(character_name: str) -> str:
    """
    Downloads the image of a given Overwatch character.

    Args:
        character_name (str): The name of the Overwatch character whose image is to be downloaded.

    Returns:
        str: The path to the downloaded image file.
    """

    res = req.get(f"https://overwatch.fandom.com/wiki/{character_name}")
    soup = bs.BeautifulSoup(res.text, "html.parser")

    image_tag = soup.select_one(".infoboxtable img")

    # Some pages, used data-src instead of src
    image_url = (
        image_tag.get("src")
        if not image_tag.get("src").startswith("data:image")
        else image_tag.get("data-src")
    )

    res = req.get(image_url)

    os.makedirs("data/images", exist_ok=True)
    path = f"data/images/{character_name}.png"
    with open(path, "wb") as file:
        file.write(res.content)

    return path


def _get_quotes(url: str) -> List[Quote]:
    """
    Fetches quotes from a given Overwatch character quotes page.

    Args:
        url (str): The URL of the Overwatch character quotes page.

    Returns:
        List[Quote]: A list of Quote objects containing the character's quotes and other details.
    """

    res = req.get(url)
    soup = bs.BeautifulSoup(res.text, "html.parser")

    character_name = soup.select_one(".mw-page-title-main").text.split("/")[0].strip()
    character_picture = _download_character_image(character_name)

    audio_urls = [
        audio_tag.get("src")
        for audio_tag in soup.select("audio source")
        if character_name in audio_tag.get("src")
    ]

    quotes = []

    for audio_url in audio_urls:
        try:
            quote_text = unquote(audio_url).split("/")[-3]
            quote_text = re.sub(r"\(.*?\)", "", quote_text)
            quote_text = (
                quote_text.split("-_")[1].replace(".ogg", "").replace("_", " ").strip()
            )

            if not quote_text:
                continue

            id = f"{character_name}{len(quotes) + 1}"

            quotes.append(
                Quote(
                    id=id,
                    character=character_name,
                    character_picture=character_picture,
                    text=quote_text,
                    audio_url=audio_url,
                    audio_path=_download_audio(id, audio_url),
                )
            )
        except Exception as e:
            print(f"Error processing quote for {character_name}: {e}")
            print("Continuing with the next quote...")

    return quotes


def get_all_quotes() -> List[Quote]:
    """
    Fetches all Overwatch character quotes, either from a local cache or by scraping the web.

    Returns:
        List[Quote]: A list of all Overwatch character quotes.
    """

    if os.path.exists("data/quotes.json"):
        with open("data/quotes.json", "r") as file:
            return [Quote(**data) for data in json.load(file)]

    quotes = [quote for page in _get_pages() for quote in _get_quotes(page)]

    with open("data/quotes.json", "w") as file:
        json.dump([quote.__dict__ for quote in quotes], file, indent=4)
