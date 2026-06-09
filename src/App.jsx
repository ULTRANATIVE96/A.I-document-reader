import React, { useState, useEffect, useRef } from 'react';
import {
  Bot,
  Settings,
  Volume2,
  Sparkles,
} from 'lucide-react';
import Tesseract from 'tesseract.js';
import * as pdfjsLib from 'pdfjs-dist';
import mammoth from 'mammoth';

// Modular components
import ChatPanel from './components/ChatPanel';
import FluidReader from './components/FluidReader';
import useDakaiAudioPlayer from './hooks/useDakaiAudioPlayer';

pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.js`;

const SA_LANGUAGES = [
  { name: 'isiZulu', code: 'zu' },
  { name: 'isiXhosa', code: 'xh' },
  { name: 'Afrikaans', code: 'af' },
  { name: 'Sesotho', code: 'st' },
  { name: 'Setswana', code: 'tn' },
  { name: 'Sepedi', code: 'nso' },
  { name: 'Xitsonga', code: 'ts' },
  { name: 'SiSwati', code: 'ss' },
  { name: 'Tshivenda', code: 've' },
  { name: 'isiNdebele', code: 'nr' }
];

// Generate a stable session ID for this browser tab
const SESSION_ID = (() => {
  let id = sessionStorage.getItem('dacai_session_id');
  if (!id) {
    id = 'sess_' + Math.random().toString(36).slice(2) + Date.now().toString(36);
    sessionStorage.setItem('dacai_session_id', id);
  }
  return id;
})();

const App = () => {
  // ── Chat state ──
  const [messages, setMessages] = useState([
    { sender: 'ai', text: 'Welcome to dacai (pronounced "tha-KAI"). I\'m your AI study partner by dac-technologies. Upload a document or ask me anything — including math!' }
  ]);
  const [userInput, setUserInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  // ── Document state ──
  const [extractedText, setExtractedText] = useState('');
  const [translatedText, setTranslatedText] = useState('');

  // ── Accent console state ──
  const [targetLang, setTargetLang] = useState('zu');
  const [dialect, setDialect] = useState(null);
  const [readingSpeed, setReadingSpeed] = useState(1.0);
  const [pitch, setPitch] = useState(1.0);
  const [clarity, setClarity] = useState(0.5);
  const [formality, setFormality] = useState(0.5);

  // ── Audio / TTS Hook ──
  const {
    voices,
    selectedVoice,
    setSelectedVoice,
    isSpeaking,
    setTargetLanguage,
    playSpeech,
    stopSpeech
  } = useDakaiAudioPlayer(targetLang);

  // ── Reader state ──
  const [showReader, setShowReader] = useState(false);
  const [readingSentences, setReadingSentences] = useState([]);
  const [currentSentenceIndex, setCurrentSentenceIndex] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);

  // ── Misc state ──
  const [isListening, setIsListening] = useState(false);

  // ── Synchronization refs ──
  const sentencesRef = useRef(readingSentences);
  const indexRef = useRef(currentSentenceIndex);
  const speedRef = useRef(readingSpeed);
  const pitchRef = useRef(pitch);
  const isPlayingRef = useRef(isPlaying);
  const selectedVoiceRef = useRef(selectedVoice);
  const recognitionRef = useRef(null);

  useEffect(() => { sentencesRef.current = readingSentences; }, [readingSentences]);
  useEffect(() => { indexRef.current = currentSentenceIndex; }, [currentSentenceIndex]);
  useEffect(() => { speedRef.current = readingSpeed; }, [readingSpeed]);
  useEffect(() => { pitchRef.current = pitch; }, [pitch]);
  useEffect(() => { isPlayingRef.current = isPlaying; }, [isPlaying]);
  useEffect(() => { selectedVoiceRef.current = selectedVoice; }, [selectedVoice]);

  // ── Sync target language with TTS Hook ──
  useEffect(() => {
    setTargetLanguage(targetLang);
  }, [targetLang, setTargetLanguage]);

  // ── Sentence parsing ──
  const getFlatSentences = (text) => {
    if (!text) return [];
    const paragraphs = text.split(/\n+/);
    const flat = [];
    paragraphs.forEach((p, pIdx) => {
      const sentences = p.match(/[^.!?]+[.!?]+(?=\s|$)/g) || [p];
      sentences.forEach((s) => {
        const trimmed = s.trim();
        if (trimmed) {
          flat.push({ text: trimmed, paragraphIndex: pIdx });
        }
      });
    });
    return flat;
  };

  // ── TTS: speak single sentence (chained) ──
  const speakSentence = (index, list = sentencesRef.current, speed = speedRef.current) => {
    if (index < 0 || index >= list.length) {
      setIsPlaying(false);
      setCurrentSentenceIndex(-1);
      stopSpeech();
      return;
    }

    setCurrentSentenceIndex(index);
    setIsPlaying(true);

    playSpeech(list[index].text, targetLang, {
      speed: speed,
      pitch: pitchRef.current,
      onEnd: () => {
        if (isPlayingRef.current && indexRef.current === index) {
          speakSentence(index + 1, list, speed);
        }
      },
      onError: (e) => {
        console.error("SpeechSynthesis error:", e);
        if (isPlayingRef.current && indexRef.current === index) {
          setIsPlaying(false);
        }
      }
    });
  };

  // ── Reader transport controls ──
  const handlePlayPauseReader = () => {
    if (isPlaying) {
      stopSpeech();
      setIsPlaying(false);
    } else {
      const idx = currentSentenceIndex >= 0 ? currentSentenceIndex : 0;
      speakSentence(idx);
    }
  };

  const handleStopReader = () => {
    stopSpeech();
    setIsPlaying(false);
    setCurrentSentenceIndex(-1);
  };

  const handleSpeedChange = (speed) => {
    setReadingSpeed(speed);
    if (isPlayingRef.current && indexRef.current >= 0) {
      speakSentence(indexRef.current, sentencesRef.current, speed);
    }
  };

  const handleVoiceChange = (voiceName) => {
    const voice = voices.find(v => v.name === voiceName);
    setSelectedVoice(voice);
    if (isPlayingRef.current && indexRef.current >= 0) {
      setTimeout(() => {
        speakSentence(indexRef.current, sentencesRef.current, speedRef.current);
      }, 50);
    }
  };

  // ── Chat ──
  const handleSendMessage = async (textToSend = null) => {
    const text = textToSend !== null ? textToSend : userInput;
    if (!text || !text.trim()) return;
    if (textToSend === null) {
      setUserInput('');
    }
    setMessages(prev => [...prev, { sender: 'user', text }]);
    setIsProcessing(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, context: extractedText, session_id: SESSION_ID })
      });
      if (!response.ok) throw new Error('Backend offline');
      const data = await response.json();
      setMessages(prev => [...prev, { sender: 'ai', text: data.response || "..." }]);
      speak(data.response);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'ai', text: "⚠️ Server connection failed. Make sure to run 'npm run server'." }]);
    } finally {
      setIsProcessing(false);
    }
  };

  // ── File upload ──
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const ext = file.name.split('.').pop().toLowerCase();
    setIsProcessing(true);
    setExtractedText('Extracting knowledge...');
    setTranslatedText('');

    const onTextExtracted = (text) => {
      setExtractedText(text);
      const flat = getFlatSentences(text);
      setReadingSentences(flat);
      setShowReader(true);
      setTimeout(() => speakSentence(0, flat), 100);
    };

    try {
      if (['png', 'jpg', 'jpeg'].includes(ext)) {
        const { data: { text: ocrText } } = await Tesseract.recognize(file, 'eng');
        onTextExtracted(ocrText.trim());
      } else if (ext === 'pdf') {
        const reader = new FileReader();
        reader.onload = async () => {
          try {
            const typedarray = new Uint8Array(reader.result);
            const pdf = await pdfjsLib.getDocument(typedarray).promise;
            let pdfText = '';
            for (let i = 1; i <= pdf.numPages; i++) {
              const page = await pdf.getPage(i);
              const content = await page.getTextContent();
              pdfText += content.items.map(item => item.str).join(' ') + '\n';
            }
            onTextExtracted(pdfText.trim());
          } catch (err) { setExtractedText("PDF Error: " + err.message); }
          finally { setIsProcessing(false); }
        };
        reader.readAsArrayBuffer(file);
        return;
      } else if (ext === 'docx') {
        const reader = new FileReader();
        reader.onload = async () => {
          try {
            const result = await mammoth.extractRawText({ arrayBuffer: reader.result });
            onTextExtracted(result.value.trim());
          } catch (err) { setExtractedText("DOCX Error: " + err.message); }
          finally { setIsProcessing(false); }
        };
        reader.readAsArrayBuffer(file);
        return;
      } else if (ext === 'txt') {
        const reader = new FileReader();
        reader.onload = () => {
          onTextExtracted(reader.result.trim());
          setIsProcessing(false);
        };
        reader.readAsText(file);
        return;
      }
    } catch (err) { setExtractedText("Error: " + err.message); }
    finally { if (!['pdf', 'docx', 'txt'].includes(ext)) setIsProcessing(false); }
  };

  // ── Translation (enriched endpoint) ──
  const handleTranslate = async () => {
    if (!extractedText) return;
    setIsProcessing(true);
    try {
      // Try enriched endpoint first, fall back to plain
      let data;
      try {
        const response = await fetch('http://127.0.0.1:5000/translate-enriched', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: extractedText,
            target: targetLang,
            dialect: dialect,
            formality: formality,
          })
        });
        if (response.ok) {
          data = await response.json();
          data.translatedText = data.enriched_text || data.translatedText;
        }
      } catch (e) { /* fall through */ }

      // Fallback to basic translate
      if (!data?.translatedText) {
        const response = await fetch('http://127.0.0.1:5000/translate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: extractedText, target: targetLang })
        });
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || `HTTP error ${response.status}`);
        }
        data = await response.json();
      }

      if (!data.translatedText) {
        throw new Error("Translation backend returned empty results");
      }
      setTranslatedText(data.translatedText);
      const flat = getFlatSentences(data.translatedText);
      setReadingSentences(flat);
      setTimeout(() => speakSentence(0, flat), 100);
    } catch (err) {
      console.error("Translation error:", err);
      alert("Translation failed: " + err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleResetTranslation = () => {
    setTranslatedText('');
    const flat = getFlatSentences(extractedText);
    setReadingSentences(flat);
    setTimeout(() => speakSentence(0, flat), 100);
  };

  // ── Inline TTS (for chat) ──
  const speak = (text) => {
    if (!text) return;
    playSpeech(text, 'en', { speed: 0.95 });
  };

  // ── Reader toggle ──
  const handleOpenReader = () => {
    if (!showReader) {
      const textToUse = translatedText || extractedText;
      if (textToUse) {
        const flat = getFlatSentences(textToUse);
        setReadingSentences(flat);
      }
      setShowReader(true);
    } else {
      handleStopReader();
      setShowReader(false);
    }
  };

  // ── Dictation ──
  const handleDictate = () => {
    // If we're already listening, click to stop recording and send immediately
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      return;
    }

    const sr = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!sr) return alert("Speech recognition not supported in this browser.");
    
    const rec = new sr();
    rec.continuous = true;
    rec.interimResults = true;
    recognitionRef.current = rec;
    let accumulatedTranscript = '';

    rec.onstart = () => {
      setIsListening(true);
    };

    rec.onresult = (e) => {
      let interimTranscript = '';
      let finalTranscript = '';
      for (let i = e.resultIndex; i < e.results.length; ++i) {
        if (e.results[i].isFinal) {
          finalTranscript += e.results[i][0].transcript;
        } else {
          interimTranscript += e.results[i][0].transcript;
        }
      }
      if (finalTranscript) {
        accumulatedTranscript += (accumulatedTranscript ? ' ' : '') + finalTranscript;
      }
      setUserInput(accumulatedTranscript + (interimTranscript ? ' ' + interimTranscript : ''));
    };

    rec.onend = () => {
      setIsListening(false);
      recognitionRef.current = null;
      if (accumulatedTranscript.trim()) {
        setUserInput('');
        handleSendMessage(accumulatedTranscript);
      }
    };

    rec.start();
  };

  // ── Render ──
  return (
    <div className="flex flex-col h-screen safe-p-top safe-p-bottom overflow-hidden relative">
      {/* Dynamic Background */}
      <div className="mesh-bg" />

      {/* Header */}
      <header className="px-6 py-5 flex justify-between items-center z-30">
        <div className="flex items-center gap-4 group cursor-pointer">
          <div className="p-3 bg-indigo-600 rounded-2xl shadow-[0_0_20px_rgba(99,102,241,0.4)] group-hover:scale-110 transition-transform duration-300">
            <Bot size={24} className="text-white" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold tracking-tight text-white flex items-center gap-2">
              dacai <Sparkles size={16} className="text-yellow-400 animate-pulse" />
            </h1>
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-widest">Active Intelligence</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-3 glass px-4 py-2 rounded-2xl border border-white/5">
            <Volume2 size={16} className="text-indigo-400" />
            <select
              className="bg-transparent text-[11px] font-semibold focus:outline-none text-slate-300 max-w-[150px]"
              value={selectedVoice?.name || ''}
              onChange={(e) => setSelectedVoice(voices.find(v => v.name === e.target.value))}
            >
              {voices.map((v, i) => <option key={i} value={v.name} className="bg-slate-900">{v.name}</option>)}
            </select>
          </div>
          <button className="p-2.5 glass rounded-2xl hover:bg-white/10 text-slate-400 transition-colors">
            <Settings size={20} />
          </button>
        </div>
      </header>

      {/* Chat Panel — messages + input */}
      <ChatPanel
        messages={messages}
        userInput={userInput}
        onUserInputChange={setUserInput}
        onSendMessage={handleSendMessage}
        isProcessing={isProcessing}
        onFileUpload={handleFileUpload}
        onOpenReader={handleOpenReader}
        showReader={showReader}
        onSpeakLast={() => speak(messages[messages.length - 1]?.text)}
        isListening={isListening}
        onDictate={handleDictate}
        isSpeaking={isSpeaking}
      />

      {/* Fluid Reader — split-screen overlay */}
      <FluidReader
        isOpen={showReader}
        onClose={() => { handleStopReader(); setShowReader(false); }}
        // Document
        sentences={readingSentences}
        currentSentenceIndex={currentSentenceIndex}
        onSentenceClick={(idx) => speakSentence(idx)}
        isTranslated={!!translatedText}
        translatedLangName={SA_LANGUAGES.find(l => l.code === targetLang)?.name || ''}
        onResetTranslation={handleResetTranslation}
        // Accent console
        targetLang={targetLang}
        onTargetLangChange={(lang) => { setTargetLang(lang); setDialect(null); }}
        dialect={dialect}
        onDialectChange={setDialect}
        speed={readingSpeed}
        onSpeedChange={handleSpeedChange}
        pitch={pitch}
        onPitchChange={setPitch}
        clarity={clarity}
        onClarityChange={setClarity}
        formality={formality}
        onFormalityChange={setFormality}
        voices={voices}
        selectedVoice={selectedVoice}
        onVoiceChange={handleVoiceChange}
        isPlaying={isPlaying}
        onPlayPause={handlePlayPauseReader}
        onStop={handleStopReader}
        isSpeaking={isSpeaking}
        onTranslate={handleTranslate}
        isProcessing={isProcessing}
      />
    </div>
  );
};

export default App;
