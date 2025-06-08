from contextlib import contextmanager
import os

from pydub import AudioSegment
import numpy as np
import librosa


@contextmanager
def suppress_all_output():
    """
    Context manager to suppress all stdout and stderr output.
    """

    # Open null device
    with open(os.devnull, "w") as devnull:
        # Save original file descriptors
        old_stdout = os.dup(1)
        old_stderr = os.dup(2)

        # Redirect stdout and stderr to devnull
        os.dup2(devnull.fileno(), 1)
        os.dup2(devnull.fileno(), 2)

        try:
            yield
        finally:
            # Restore original file descriptors
            os.dup2(old_stdout, 1)
            os.dup2(old_stderr, 2)
            os.close(old_stdout)
            os.close(old_stderr)


def stretch_audio_segment(
    original: AudioSegment, target_duration_ms: int
) -> AudioSegment:
    """
    Time‐stretches a pydub AudioSegment to match a given target duration (in ms),
    preserving its original pitch via librosa. Returns a new AudioSegment
    whose length is (approximately) target_duration_ms.

    Args:
        original: The input AudioSegment to stretch.
        target_duration_ms: The desired final duration in milliseconds.

    Returns:
        A new AudioSegment of length ~ target_duration_ms, pitch‐preserved.
    """

    # 1) Compute original duration and librosa rate
    original_duration_ms = len(original)
    rate = original_duration_ms / target_duration_ms
    #    If rate > 1, librosa will produce a shorter result.
    #    If rate < 1, librosa will produce a longer result.

    # 2) Extract raw samples from the AudioSegment
    samples = np.array(original.get_array_of_samples())
    channels = original.channels
    sample_width_bytes = original.sample_width  # e.g. 2 for 16‐bit PCM
    sr = original.frame_rate

    # 3) Reshape and normalize to float32 in [−1.0, +1.0]
    if channels > 1:
        # Convert 1D interleaved to shape (channels, n_frames)
        samples = samples.reshape((-1, channels)).T
    else:
        # Mono → shape (1, n_frames)
        samples = samples[np.newaxis, :]

    max_int_value = float(2 ** (8 * sample_width_bytes - 1))
    samples_float = samples.astype(np.float32) / max_int_value

    # 4) Stretch each channel with librosa
    stretched_channels = []
    for ch in range(channels):
        y = samples_float[ch]
        y_stretched = librosa.effects.time_stretch(y, rate=rate)
        stretched_channels.append(y_stretched)

    # 5) Stack back into shape (n_frames_new, channels)
    stretched_arr = np.stack(stretched_channels, axis=1)  # (n_frames_new, channels)

    # 6) Convert float32 back to int (same bit depth), then to raw bytes
    stretched_int = np.clip(
        stretched_arr * max_int_value, -max_int_value, max_int_value - 1
    ).astype(f"int{8 * sample_width_bytes}")

    if channels > 1:
        # Interleave stereo channels back into a single 1D byte string
        stretched_interleaved = stretched_int.flatten().tobytes()
    else:
        # Mono: take the first (only) column
        stretched_interleaved = stretched_int[:, 0].tobytes()

    # 7) Build a new AudioSegment from the stretched raw data
    stretched_segment = AudioSegment(
        data=stretched_interleaved,
        sample_width=sample_width_bytes,
        frame_rate=sr,
        channels=channels,
    )

    return stretched_segment
