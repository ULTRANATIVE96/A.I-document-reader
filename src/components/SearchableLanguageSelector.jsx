import React, { useState, useRef, useEffect } from 'react';
import { Languages, Search, ChevronDown, Check } from 'lucide-react';

export const SA_LANGUAGES = [
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

const getAccentRegion = (langCode) => {
  const parts = langCode.split('-');
  if (parts.length < 2) return langCode;
  const region = parts[1].toUpperCase();
  const regions = {
    'US': 'United States',
    'GB': 'United Kingdom',
    'ZA': 'South Africa',
    'AU': 'Australia',
    'CA': 'Canada',
    'IN': 'India',
    'NZ': 'New Zealand',
    'IE': 'Ireland'
  };
  return regions[region] || region;
};

const SearchableLanguageSelector = ({ 
  targetLang, 
  selectedVoice, 
  voices = [], 
  onChange, 
  compact = false 
}) => {
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

  const englishVoices = voices.filter(v => 
    v.lang.toLowerCase().startsWith('en')
  );

  const options = [
    ...SA_LANGUAGES.map(lang => ({
      id: lang.code,
      name: lang.name,
      type: 'language',
      code: lang.code
    })),
    ...englishVoices.map(v => ({
      id: `voice-${v.name}`,
      name: `English (${getAccentRegion(v.lang)}) - ${v.name}`,
      type: 'voice',
      voice: v,
      code: 'en'
    }))
  ];

  const filteredOptions = options.filter(opt =>
    opt.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Check if an option is currently selected
  const isSelected = (opt) => {
    if (opt.type === 'language') {
      return targetLang === opt.code && targetLang !== 'en';
    } else {
      return targetLang === 'en' && selectedVoice?.name === opt.voice?.name;
    }
  };

  // Determine current active selection name
  let currentSelectionName = 'Select Language';
  const activeOpt = options.find(isSelected);
  if (activeOpt) {
    currentSelectionName = activeOpt.name;
  }

  const handleSelect = (opt) => {
    if (opt.type === 'language') {
      onChange({ targetLang: opt.code, selectedVoice: null });
    } else {
      onChange({ targetLang: 'en', selectedVoice: opt.voice });
    }
    setIsOpen(false);
  };

  if (compact) {
    return (
      <div className="relative" ref={dropdownRef}>
        <button
          type="button"
          onClick={() => {
            setIsOpen(!isOpen);
            setSearchQuery('');
          }}
          className="glass px-4 py-2 rounded-2xl border border-white/5 text-[11px] font-semibold text-slate-300 hover:bg-white/5 hover:text-white transition-all duration-300 flex items-center gap-2 cursor-pointer max-w-[280px]"
        >
          <Languages size={14} className="text-indigo-400 shrink-0" />
          <span className="truncate">{currentSelectionName}</span>
          <ChevronDown size={12} className={`text-slate-400 transition-transform duration-300 shrink-0 ${isOpen ? 'rotate-180' : ''}`} />
        </button>

        {isOpen && (
          <div className="absolute right-0 z-50 w-72 mt-2 bg-slate-950 border border-white/10 rounded-xl shadow-2xl p-2 space-y-1.5 animate-in fade-in slide-in-from-top-1 duration-150">
            <div className="relative flex items-center">
              <Search size={12} className="absolute left-2.5 text-slate-500" />
              <input
                type="text"
                placeholder="Search language or accent..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg pl-8 pr-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500/50 transition-colors"
                autoFocus
              />
            </div>

            <div className="max-h-56 overflow-y-auto custom-scrollbar space-y-0.5">
              {filteredOptions.length > 0 ? (
                filteredOptions.map(opt => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => handleSelect(opt)}
                    className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-between transition-colors ${
                      isSelected(opt)
                        ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                        : 'text-slate-300 hover:bg-white/5 hover:text-white'
                    }`}
                  >
                    <span className="truncate pr-2">{opt.name}</span>
                    {isSelected(opt) && <Check size={10} className="text-indigo-400 shrink-0" />}
                  </button>
                ))
              ) : (
                <div className="text-[9px] text-slate-500 text-center py-2.5 font-semibold">
                  No languages or accents found
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="relative mb-3" ref={dropdownRef}>
      <label className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1 block">
        Language & Accent
      </label>
      <button
        type="button"
        onClick={() => {
          setIsOpen(!isOpen);
          setSearchQuery('');
        }}
        className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-slate-200 font-medium flex items-center justify-between hover:bg-white/10 hover:border-white/20 transition-all cursor-pointer shadow-inner"
      >
        <span className="flex items-center gap-2 truncate">
          <Languages size={14} className="text-indigo-400" />
          <span className="truncate">{currentSelectionName}</span>
        </span>
        <ChevronDown size={14} className={`text-slate-400 transition-transform duration-300 shrink-0 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-1.5 bg-slate-950 border border-white/10 rounded-xl shadow-2xl p-2 space-y-1.5 animate-in fade-in slide-in-from-top-1 duration-150">
          <div className="relative flex items-center">
            <Search size={12} className="absolute left-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search language or accent..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg pl-8 pr-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500/50 transition-colors"
              autoFocus
            />
          </div>

          <div className="max-h-56 overflow-y-auto custom-scrollbar space-y-0.5">
            {filteredOptions.length > 0 ? (
              filteredOptions.map(opt => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => handleSelect(opt)}
                  className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-between transition-colors ${
                    isSelected(opt)
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                      : 'text-slate-300 hover:bg-white/5 hover:text-white'
                  }`}
                >
                  <span className="truncate pr-2">{opt.name}</span>
                  {isSelected(opt) && <Check size={10} className="text-indigo-400 shrink-0" />}
                </button>
              ))
            ) : (
              <div className="text-[9px] text-slate-500 text-center py-2.5 font-semibold">
                No languages or accents found
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchableLanguageSelector;
