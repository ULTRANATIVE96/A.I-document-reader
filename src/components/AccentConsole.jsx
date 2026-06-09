import React, { useState, useRef, useEffect } from 'react';
import { Volume2, Play, Pause, Square, Languages } from 'lucide-react';
import PhoneticSlider from './PhoneticSlider';
import WaveformIndicator from './WaveformIndicator';
import SearchableLanguageSelector from './SearchableLanguageSelector';

const DIALECT_MAP = {
  ts: [
    { value: 'malamulele', label: 'Malamulele' },
    { value: 'bushbuckridge', label: 'Bushbuckridge' },
    { value: 'giyani', label: 'Giyani' },
  ],
  zu: [
    { value: 'kwazulu-natal', label: 'KwaZulu-Natal' },
    { value: 'gauteng-urban', label: 'Gauteng Urban' },
  ],
  xh: [
    { value: 'eastern-cape', label: 'Eastern Cape' },
    { value: 'western-cape', label: 'Western Cape' },
  ],
  ve: [
    { value: 'venda', label: 'Venda' },
    { value: 'limpopo', label: 'Limpopo' },
  ],
  nso: [
    { value: 'polokwane', label: 'Polokwane' },
    { value: 'sekhukhune', label: 'Sekhukhune' },
  ],
};

const AccentConsole = ({
  // Language & Dialect
  targetLang, onTargetLangChange,
  dialect, onDialectChange,
  // Audio controls
  speed, onSpeedChange,
  pitch, onPitchChange,
  clarity, onClarityChange,
  formality, onFormalityChange,
  // Voice
  voices, selectedVoice, onVoiceChange,
  // Playback
  isPlaying, onPlayPause, onStop, isSpeaking,
  // Translation
  onTranslate, isProcessing,
}) => {
  const currentDialects = DIALECT_MAP[targetLang] || [];

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3 border-b border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">
            Phonetic Console
          </span>
        </div>
        <WaveformIndicator isActive={isSpeaking} />
      </div>

      {/* Scrollable controls */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-5 space-y-6">

        {/* ── Language & Dialect ── */}
        <section>
          <h4 className="text-[10px] font-black uppercase tracking-[0.15em] text-indigo-400 mb-3 flex items-center gap-2">
            <Languages size={12} /> Language & Region
          </h4>
          <div className="space-y-3">
            <SearchableLanguageSelector
              targetLang={targetLang}
              selectedVoice={selectedVoice}
              voices={voices}
              onChange={({ targetLang: lang, selectedVoice: voice }) => {
                onTargetLangChange(lang);
                if (voice) {
                  onVoiceChange(voice.name);
                }
              }}
            />

            {currentDialects.length > 0 && (
              <div>
                <label className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1 block">Regional Dialect</label>
                <select
                  value={dialect || ''}
                  onChange={(e) => onDialectChange(e.target.value || null)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-slate-200 font-medium focus:outline-none focus:border-indigo-500/50 transition-colors cursor-pointer"
                >
                  <option value="" className="bg-slate-900">Standard</option>
                  {currentDialects.map(d => (
                    <option key={d.value} value={d.value} className="bg-slate-900">{d.label}</option>
                  ))}
                </select>
              </div>
            )}

            <button
              onClick={onTranslate}
              disabled={isProcessing}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-4 py-3 rounded-xl font-bold text-xs uppercase tracking-wider hover:from-indigo-500 hover:to-purple-500 transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-600/20"
            >
              {isProcessing ? 'Translating…' : 'Translate Document'}
            </button>
          </div>
        </section>

        <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

        {/* ── Voice & Playback ── */}
        <section>
          <h4 className="text-[10px] font-black uppercase tracking-[0.15em] text-indigo-400 mb-3 flex items-center gap-2">
            <Volume2 size={12} /> Voice & Playback
          </h4>
          <div className="space-y-3">
            {/* Transport */}
            <div className="flex gap-2">
              <button
                onClick={onPlayPause}
                className="flex-1 flex items-center justify-center gap-2 bg-indigo-600 text-white py-3 rounded-xl font-bold text-xs hover:bg-indigo-500 transition-all active:scale-[0.97]"
              >
                {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                {isPlaying ? 'Pause' : 'Play'}
              </button>
              <button
                onClick={onStop}
                className="px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-rose-400 hover:bg-rose-500/10 transition-all active:scale-[0.97]"
              >
                <Square size={16} />
              </button>
            </div>
          </div>
        </section>

        <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

        {/* ── Phonetic Tuning ── */}
        <section>
          <h4 className="text-[10px] font-black uppercase tracking-[0.15em] text-indigo-400 mb-4">
            ⚡ Phonetic Tuning
          </h4>
          <div className="space-y-5">
            <PhoneticSlider
              label="Reading Speed"
              value={speed}
              min={0.3}
              max={2.5}
              step={0.1}
              onChange={onSpeedChange}
              unit="x"
              gradient="from-cyan-500 to-blue-500"
            />
            <PhoneticSlider
              label="Pitch"
              value={pitch}
              min={0.5}
              max={2.0}
              step={0.1}
              onChange={onPitchChange}
              unit="x"
              gradient="from-amber-500 to-orange-500"
            />
            <PhoneticSlider
              label="Articulation Clarity"
              value={clarity}
              min={0}
              max={1}
              step={0.01}
              onChange={onClarityChange}
              gradient="from-emerald-500 to-teal-500"
            />
          </div>
        </section>

        <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

        {/* ── Formality ── */}
        <section>
          <h4 className="text-[10px] font-black uppercase tracking-[0.15em] text-indigo-400 mb-3">
            🎭 Translation Depth
          </h4>
          <PhoneticSlider
            label="Formal ↔ Colloquial"
            value={formality}
            min={0}
            max={1}
            step={0.01}
            onChange={onFormalityChange}
            gradient="from-rose-500 to-pink-500"
          />
          <div className="flex justify-between mt-2">
            <span className="text-[9px] text-slate-600 font-bold uppercase">Colloquial</span>
            <span className="text-[9px] text-slate-600 font-bold uppercase">Formal</span>
          </div>
        </section>
      </div>
    </div>
  );
};

export default AccentConsole;
