import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook to sync audio playback timestamps with text highlighting.
 * Accepts word-level timestamps and returns the current active indices.
 */
const useAudioSync = (timestamps = [], isPlaying = false, speed = 1.0) => {
  const [currentWordIndex, setCurrentWordIndex] = useState(-1);
  const [currentSentenceIndex, setCurrentSentenceIndex] = useState(-1);
  const [elapsedTime, setElapsedTime] = useState(0);
  const startTimeRef = useRef(null);
  const rafRef = useRef(null);
  const pausedAtRef = useRef(0);

  const tick = useCallback(() => {
    if (!startTimeRef.current || !timestamps.length) return;

    const now = performance.now();
    const elapsed = pausedAtRef.current + (now - startTimeRef.current) / 1000;
    setElapsedTime(elapsed);

    // Find current word by timestamp
    let wordIdx = -1;
    let sentIdx = -1;
    for (let i = 0; i < timestamps.length; i++) {
      if (elapsed >= timestamps[i].start_time && elapsed <= timestamps[i].end_time) {
        wordIdx = i;
        sentIdx = timestamps[i].sentence_index ?? 0;
        break;
      }
      // If between words, keep last word highlighted
      if (elapsed > timestamps[i].end_time && (i + 1 >= timestamps.length || elapsed < timestamps[i + 1].start_time)) {
        wordIdx = i;
        sentIdx = timestamps[i].sentence_index ?? 0;
      }
    }

    setCurrentWordIndex(wordIdx);
    setCurrentSentenceIndex(sentIdx);

    // Check if playback is done
    const totalDuration = timestamps[timestamps.length - 1]?.end_time ?? 0;
    if (elapsed < totalDuration) {
      rafRef.current = requestAnimationFrame(tick);
    }
  }, [timestamps]);

  useEffect(() => {
    if (isPlaying && timestamps.length > 0) {
      startTimeRef.current = performance.now();
      rafRef.current = requestAnimationFrame(tick);
    } else {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
      }
      if (!isPlaying) {
        pausedAtRef.current = elapsedTime;
        startTimeRef.current = null;
      }
    }

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [isPlaying, timestamps, tick]);

  const reset = useCallback(() => {
    setCurrentWordIndex(-1);
    setCurrentSentenceIndex(-1);
    setElapsedTime(0);
    pausedAtRef.current = 0;
    startTimeRef.current = null;
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
  }, []);

  const seekToWord = useCallback((index) => {
    if (index >= 0 && index < timestamps.length) {
      pausedAtRef.current = timestamps[index].start_time;
      setElapsedTime(timestamps[index].start_time);
      setCurrentWordIndex(index);
      setCurrentSentenceIndex(timestamps[index].sentence_index ?? 0);
      if (isPlaying) {
        startTimeRef.current = performance.now();
      }
    }
  }, [timestamps, isPlaying]);

  return {
    currentWordIndex,
    currentSentenceIndex,
    elapsedTime,
    reset,
    seekToWord,
  };
};

export default useAudioSync;
