import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Custom React hook to manage Web Speech API (SpeechSynthesis) state and execution.
 * Resolves browser default-voice fallback bugs using the Voice Preservation Protocol.
 */
export const useDakaiAudioPlayer = (initialLang = 'en') => {
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [targetLanguage, setTargetLanguage] = useState(initialLang);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  // Keep references to selectedVoice and targetLanguage to avoid closures issues in callbacks
  const selectedVoiceRef = useRef(selectedVoice);
  const targetLanguageRef = useRef(targetLanguage);

  useEffect(() => {
    selectedVoiceRef.current = selectedVoice;
  }, [selectedVoice]);

  useEffect(() => {
    targetLanguageRef.current = targetLanguage;
  }, [targetLanguage]);

  /**
   * Load voices asynchronously.
   */
  const loadVoices = useCallback(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    const availableVoices = window.speechSynthesis.getVoices();
    setVoices(availableVoices);

    // Auto-select a high-quality default voice matching our current target language
    const currentLang = targetLanguageRef.current || 'en';
    const matchedVoice = availableVoices.find(voice => 
      voice.lang.startsWith(currentLang) && 
      (voice.name.includes('Google') || voice.name.includes('Natural') || voice.name.includes('Premium'))
    ) || availableVoices.find(voice => voice.lang.startsWith(currentLang))
      || availableVoices.find(voice => voice.lang.startsWith('en'))
      || availableVoices[0];

    if (matchedVoice && !selectedVoiceRef.current) {
      setSelectedVoice(matchedVoice);
    }
  }, []);

  /**
   * Hook lifecycle: Listen to async voices loading events.
   */
  useEffect(() => {
    loadVoices();
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }
    return () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = null;
      }
    };
  }, [loadVoices]);

  /**
   * Stop active speech playback and clear browser queues.
   */
  const stopSpeech = useCallback(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setIsPaused(false);
  }, []);

  /**
   * Plays speech using the Voice Preservation Protocol.
   * Instantiates a clean SpeechSynthesisUtterance on every play event to avoid recycling issues.
   *
   * @param {string} text The text string to read aloud.
   * @param {string} targetLang The targeted language code parameter (e.g. 'zu').
   * @param {object} options Optional configs (speed, pitch, event handlers).
   */
  const playSpeech = useCallback((text, targetLang = targetLanguageRef.current, options = {}) => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    
    // Stop overlapping audio streams before triggering a new one
    stopSpeech();

    if (!text) return;

    // Instantiate a new utterance object every play event to bypass state recycling bugs
    const utterance = new SpeechSynthesisUtterance(text);

    // VOICE PRESERVATION PROTOCOL:
    // Step 1: Assign the target language code parameters first
    utterance.lang = targetLang;

    // Step 2: Loop through available voices to find the exact chosen voice setting
    const availableVoices = window.speechSynthesis.getVoices();
    const activeVoice = selectedVoiceRef.current;
    
    const matchedVoice = availableVoices.find(v => v.name === activeVoice?.name) || 
                         availableVoices.find(v => v.lang.startsWith(targetLang));

    // Step 3: Manually overwrite the voice property AFTER setting the language.
    // Setting this after language code forces the browser to respect the selection
    // rather than falling back to native OS defaults.
    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    // Apply pitch and speed parameters
    utterance.rate = options.speed ?? 1.0;
    utterance.pitch = options.pitch ?? 1.0;

    // Attach lifecycle triggers
    utterance.onstart = () => {
      setIsSpeaking(true);
      setIsPaused(false);
      if (options.onStart) options.onStart();
    };

    utterance.onend = () => {
      setIsSpeaking(true); // temporary keep true if chaining, let handler control
      setIsSpeaking(false);
      setIsPaused(false);
      if (options.onEnd) options.onEnd();
    };

    utterance.onerror = (event) => {
      // Interrupted errors are expected when stopSpeech cancels current play
      if (event.error !== 'interrupted') {
        setIsSpeaking(false);
        setIsPaused(false);
        if (options.onError) options.onError(event);
      }
    };

    window.speechSynthesis.speak(utterance);
  }, [stopSpeech]);

  const pauseSpeech = useCallback(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    window.speechSynthesis.pause();
    setIsPaused(true);
  }, []);

  const resumeSpeech = useCallback(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    window.speechSynthesis.resume();
    setIsPaused(false);
  }, []);

  return {
    voices,
    selectedVoice,
    setSelectedVoice,
    targetLanguage,
    setTargetLanguage,
    isSpeaking,
    isPaused,
    playSpeech,
    stopSpeech,
    pauseSpeech,
    resumeSpeech
  };
};

export default useDakaiAudioPlayer;
