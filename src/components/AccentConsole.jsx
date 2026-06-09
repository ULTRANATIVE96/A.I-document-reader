import React, { useState, useRef, useEffect } from 'react';
import { Volume2, Play, Pause, Square, Languages, Search, ChevronDown, Check } from 'lucide-react';
import PhoneticSlider from './PhoneticSlider';
import WaveformIndicator from './WaveformIndicator';

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
  { name: 'isiNdebele', code: 'nr' },
];

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

const SearchableLanguageSelector = ({ selectedCode, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredLanguages = SA_LANGUAGES.filter(lang =>
    lang.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const currentLang = SA_LANGUAGES.find(l => l.code === selectedCode) || SA_LANGUAGES[0];

  return (
    <div className="relative mb-3" ref={dropdownRef}>
      <label className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1 block">
        Target Language
      </label>
      <button
        type="button"
        onClick={() => {
          setIsOpen(!isOpen);
          setSearchQuery('');
        }}
        className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-slate-200 font-medium flex items-center justify-between hover:bg-white/10 hover:border-white/20 transition-all cursor-pointer shadow-inner"
      >
        <span className="flex items-center gap-2">
          <Languages size={14} className="text-indigo-400" />
          {currentLang.name}
        </span>
        <ChevronDown size={14} className={`text-slate-400 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-1.5 bg-slate-950 border border-white/10 rounded-xl shadow-2xl p-2 space-y-1.5 animate-in fade-in slide-in-from-top-1 duration-150">
          <div className="relative flex items-center">
            <Search size={12} className="absolute left-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search language..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg pl-8 pr-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500/50 transition-colors"
              autoFocus
            />
          </div>

          <div className="max-h-40 overflow-y-auto custom-scrollbar space-y-0.5">
            {filteredLanguages.length > 0 ? (
              filteredLanguages.map(lang => (
                <button
                  key={lang.code}
                  type="button"
                  onClick={() => {
                    onChange(lang.code);
                    setIsOpen(false);
                  }}
                  className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-between transition-colors ${
                    lang.code === selectedCode
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                      : 'text-slate-300 hover:bg-white/5 hover:text-white'
                  }`}
                >
                  {lang.name}
                  {lang.code === selectedCode && <Check size={10} className="text-indigo-400" />}
                </button>
              ))
            ) : (
              <div className="text-[9px] text-slate-500 text-center py-2.5 font-semibold">
                No languages found
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
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
              selectedCode={targetLang}
              onChange={onTargetLangChange}
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
            <div>
              <label className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1 block">Voice Engine</label>
              <select
                value={selectedVoice?.name || ''}
                onChange={(e) => onVoiceChange(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-slate-200 font-medium focus:outline-none focus:border-indigo-500/50 transition-colors cursor-pointer"
              >
                {voices.map((v, i) => (
                  <option key={i} value={v.name} className="bg-slate-900">{v.name}</option>
                ))}
              </select>
            </div>

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
