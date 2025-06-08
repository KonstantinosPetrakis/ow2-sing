from typing import Tuple, List

from forcealign.forcealign import Word
from forcealign import ForceAlign
from pydub import AudioSegment
import nltk

from models import Quote

nltk.download("averaged_perceptron_tagger_eng", quiet=True)


def _find_word_index(substring: str, tokens: List[str]) -> Tuple[int, int]:
    """
    This function finds the index of a substring in a list of tokens.

    Args:
        substring (str): The substring to find in the list of tokens.
        tokens (List[str]): The list of tokens to search within.

    Returns:
        Tuple[int, int]: The index of the substring in the list of tokens, or -1 if not found and the length of the substring as token count.
    """

    tokens = [token.lower() for token in tokens]
    tokenized_substring = substring.lower().replace("'", "").split()
    substring_token_length = len(tokenized_substring)

    for i in range(len(tokens) - substring_token_length + 1):
        if tokens[i : i + substring_token_length] == tokenized_substring:
            return i, substring_token_length
    return -1, substring_token_length


def align_words(audio_path: str, complete_text: str) -> List[Word]:
    """
    This function aligns the words in a transcript with the corresponding audio timestamps

    Args:
        audio_path (str): The path to the audio file.
        complete_text (str): The complete transcript of the audio.

    Returns:
        List[Word]: A list of Word objects containing the word, start time, and end time.
    """

    align = ForceAlign(audio_file=audio_path, transcript=complete_text)
    return align.inference()


def align_text(audio_path: str, complete_text: str, wanted_part: str) -> AudioSegment:
    """
    This function aligns a specific part of the text with the corresponding audio timestamps.

    Args:
        audio_path (str): The path to the audio file.
        complete_text (str): The complete transcript of the audio.
        wanted_part (str): The specific part of the text to align.

    Returns:
        AudioSegment: An AudioSegment object containing the audio segment corresponding to the wanted part of the text.
    """

    words = align_words(audio_path, complete_text)
    word_index, wanted_word_count = _find_word_index(
        wanted_part, [w.word for w in words]
    )

    first_word = words[word_index]
    last_word = words[word_index + wanted_word_count - 1]

    audio = AudioSegment.from_file(audio_path)
    return audio[first_word.time_start * 1000 : last_word.time_end * 1000]


def align_texts_timestamps(
    audio_path: str, complete_text: str, texts_to_align: List[str]
) -> List[Tuple[float, float]]:
    """
    This function aligns multiple texts with the corresponding audio timestamps.

    Args:
        audio_path (str): The path to the audio file.
        complete_text (str): The complete transcript of the audio.
        texts_to_align (List[str]): A list of texts to align with the audio.

    Returns:
        List[Tuple[float, float]]: A list of tuples containing the start and end timestamps of the aligned texts
    """

    words = align_words(audio_path, complete_text)
    words_tokenized = [w.word for w in words]

    timestamps = []
    last_word_index = 0
    for text in texts_to_align:
        index_offset, wanted_words_count = _find_word_index(
            text, words_tokenized[last_word_index:]
        )
        word_index = last_word_index + index_offset
        last_word_index = word_index + wanted_words_count - 1
        first_word = words[word_index]
        last_word = words[last_word_index]

        timestamps.append((first_word.time_start * 1000, last_word.time_end * 1000))

    return timestamps


def align_quote(quote: Quote, wanted_part: str) -> AudioSegment:
    """
    This function aligns a specific part of a quote with the corresponding audio timestamps.

    Args:
        quote (Quote): The quote object containing the audio path and text.
        wanted_part (str): The specific part of the quote text to align.

    Returns:
        AudioSegment: An AudioSegment object containing the audio segment corresponding to the wanted part of the quote.
    """

    return align_text(quote.audio_path, quote.text, wanted_part)
