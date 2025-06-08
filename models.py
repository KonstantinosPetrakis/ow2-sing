"""
This module contains common data models used in the application.
"""

from dataclasses import dataclass
from typing import List

from pydub import AudioSegment


@dataclass
class Quote:
    id: str
    character: str
    character_picture: str
    text: str
    audio_url: str
    audio_path: str


@dataclass
class Match:
    quote: Quote
    quote_segment: str
    audio_segment: AudioSegment | None = None
