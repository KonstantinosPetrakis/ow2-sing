"""
This module is responsible for separating the instrumental and vocal parts of a song.
"""

import logging
from utils import suppress_all_output

logging.getLogger("spleeter").disabled = True

with suppress_all_output():
    from spleeter.separator import Separator


def separate_audio(audio_path: str):
    separator = Separator("spleeter:2stems")

    with suppress_all_output():
        separator.separate_to_file(
            audio_path, "data", codec="mp3", filename_format="{instrument}.{codec}"
        )
