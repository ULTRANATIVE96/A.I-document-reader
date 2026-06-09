"""
Mock Audio Timestamp Generator
Simulates word-level timing data that a real TTS API would return.
"""
import re


def generate_word_timestamps(text, speed=1.0, pitch=1.0):
    """
    Generate mock word-level timestamps based on word length and speed.
    
    Returns: list of { word, start_time, end_time, sentence_index }
    
    Timing model:
    - Base duration per character: 60ms
    - Min word duration: 150ms
    - Pause after punctuation: 300ms
    - Speed multiplier applied inversely (faster = shorter durations)
    """
    if not text:
        return []

    words = text.split()
    timestamps = []
    current_time = 0.0
    sentence_idx = 0
    speed_factor = 1.0 / max(0.25, speed)

    BASE_MS_PER_CHAR = 60
    MIN_WORD_MS = 150
    PUNCTUATION_PAUSE_MS = 300
    COMMA_PAUSE_MS = 150
    WORD_GAP_MS = 80

    for word in words:
        clean_word = re.sub(r'[^\w]', '', word)
        if not clean_word:
            continue

        # Calculate duration based on syllable complexity
        char_count = len(clean_word)
        duration_ms = max(MIN_WORD_MS, char_count * BASE_MS_PER_CHAR)
        duration_ms *= speed_factor

        start = round(current_time, 3)
        end = round(current_time + duration_ms / 1000, 3)

        timestamps.append({
            "word": word,
            "start_time": start,
            "end_time": end,
            "sentence_index": sentence_idx,
        })

        current_time = end

        # Add pauses
        if re.search(r'[.!?]$', word):
            current_time += (PUNCTUATION_PAUSE_MS * speed_factor) / 1000
            sentence_idx += 1
        elif re.search(r'[,;:]$', word):
            current_time += (COMMA_PAUSE_MS * speed_factor) / 1000
        else:
            current_time += (WORD_GAP_MS * speed_factor) / 1000

    return timestamps


def get_total_duration(timestamps):
    """Get total audio duration from timestamps."""
    if not timestamps:
        return 0.0
    return timestamps[-1]["end_time"]
