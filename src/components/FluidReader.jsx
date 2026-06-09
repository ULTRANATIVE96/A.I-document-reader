import React from 'react';
import { X } from 'lucide-react';
import DocumentViewer from './DocumentViewer';
import AccentConsole from './AccentConsole';

const FluidReader = ({
  // Visibility
  isOpen,
  onClose,
  // Document
  sentences,
  currentSentenceIndex,
  onSentenceClick,
  isTranslated,
  translatedLangName,
  onResetTranslation,
  // Accent Console props
  targetLang, onTargetLangChange,
  dialect, onDialectChange,
  speed, onSpeedChange,
  pitch, onPitchChange,
  clarity, onClarityChange,
  formality, onFormalityChange,
  voices, selectedVoice, onVoiceChange,
  isPlaying, onPlayPause, onStop, isSpeaking,
  onTranslate, isProcessing,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-slate-950/[0.98] backdrop-blur-2xl reader-enter">
      {/* Top bar */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-white/5 bg-black/40">
        <div className="flex items-center gap-3">
          <div className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse" />
          <span className="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-400">
            DACAI Fluid Reader
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-400 hover:text-white transition-all active:scale-90"
        >
          <X size={18} />
        </button>
      </div>

      {/* Split screen */}
      <div className="flex-1 flex flex-col lg:flex-row min-h-0 overflow-hidden">
        {/* Left: Document Viewer (60%) */}
        <div className="flex-1 lg:flex-[6] flex flex-col min-h-0 border-r border-white/5">
          <DocumentViewer
            sentences={sentences}
            currentSentenceIndex={currentSentenceIndex}
            onSentenceClick={onSentenceClick}
            isTranslated={isTranslated}
            translatedLangName={translatedLangName}
            onResetTranslation={onResetTranslation}
          />
        </div>

        {/* Right: Accent Console (40%) */}
        <div className="lg:flex-[4] flex flex-col min-h-0 bg-black/20 max-h-[40vh] lg:max-h-none">
          <AccentConsole
            targetLang={targetLang}
            onTargetLangChange={onTargetLangChange}
            dialect={dialect}
            onDialectChange={onDialectChange}
            speed={speed}
            onSpeedChange={onSpeedChange}
            pitch={pitch}
            onPitchChange={onPitchChange}
            clarity={clarity}
            onClarityChange={onClarityChange}
            formality={formality}
            onFormalityChange={onFormalityChange}
            voices={voices}
            selectedVoice={selectedVoice}
            onVoiceChange={onVoiceChange}
            isPlaying={isPlaying}
            onPlayPause={onPlayPause}
            onStop={onStop}
            isSpeaking={isSpeaking}
            onTranslate={onTranslate}
            isProcessing={isProcessing}
          />
        </div>
      </div>
    </div>
  );
};

export default FluidReader;
