from pydub import AudioSegment

from songs import download_song, get_song_lyrics, select_song
from align import align_texts_timestamps
from utils import stretch_audio_segment
from matcher import find_quote_matches
from separator import separate_audio
from quotes import get_all_quotes


song = select_song()
lyrics = get_song_lyrics(song)

download_song(song)
print("Downloaded song.")

separate_audio("data/temp.mp3")
print("Separated audio into vocals and accompaniment.")

matches = find_quote_matches(lyrics, get_all_quotes())
print(f"Found {len(matches)} matches that make up a sequence.")

timed_lyrics = align_texts_timestamps(
    "data/vocals.mp3", lyrics, [match.quote_segment for match in matches]
)
print(f"Aligned lyrics with timestamps.")

start_time = timed_lyrics[0][0]
end_time = timed_lyrics[-1][1]
padding = 2000
segment_start = max(0, start_time - padding)
segment_end = end_time + padding

accompaniment_audio = AudioSegment.from_file("data/accompaniment.mp3")
accompaniment_audio = accompaniment_audio[segment_start:segment_end] - 15

output: AudioSegment = accompaniment_audio

with open("data/debug.txt", "w") as f:
    for i in range(len(timed_lyrics)):
        start_ms, end_ms = timed_lyrics[i]
        target_duration = end_ms - start_ms

        scaled_audio_segment = stretch_audio_segment(
            matches[i].audio_segment, target_duration
        )

        relative_start = start_ms - segment_start
        output = output.overlay(scaled_audio_segment, position=relative_start)

        f.write(
            f"{matches[i].quote.character}: {matches[i].quote_segment} @{relative_start}\n"
        )

output.export("data/output.mp3", format="mp3")
