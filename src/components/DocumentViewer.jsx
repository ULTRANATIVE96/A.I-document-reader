import React, { useEffect, useRef } from 'react';

const DocumentViewer = ({
  sentences = [],
  currentSentenceIndex = -1,
  onSentenceClick,
  isTranslated = false,
  translatedLangName = '',
  onResetTranslation,
}) => {
  const containerRef = useRef(null);

  // Auto-scroll active sentence
  useEffect(() => {
    if (currentSentenceIndex >= 0) {
      const el = document.getElementById(`fluid-sentence-${currentSentenceIndex}`);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [currentSentenceIndex]);

  // Group sentences by paragraph
  const paragraphs = {};
  sentences.forEach((s, i) => {
    const pIdx = s.paragraphIndex ?? 0;
    if (!paragraphs[pIdx]) paragraphs[pIdx] = [];
    paragraphs[pIdx].push({ ...s, flatIdx: i });
  });

  return (
    <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">
            Document Viewer
          </span>
        </div>
        {isTranslated && (
          <button
            onClick={onResetTranslation}
            className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-1"
          >
            <span>↩</span> {translatedLangName} — Reset
          </button>
        )}
      </div>

      {/* Scrollable text area */}
      <div ref={containerRef} className="flex-1 overflow-y-auto custom-scrollbar p-6 md:p-8">
        <div className="max-w-2xl mx-auto space-y-5">
          {Object.keys(paragraphs).map((pIdx) => (
            <p key={pIdx} className="leading-[2] tracking-wide">
              {paragraphs[pIdx].map((s) => {
                const isActive = s.flatIdx === currentSentenceIndex;
                return (
                  <span
                    key={s.flatIdx}
                    id={`fluid-sentence-${s.flatIdx}`}
                    onClick={() => onSentenceClick?.(s.flatIdx)}
                    className={`
                      fluid-sentence cursor-pointer rounded-md px-1 py-0.5
                      transition-all duration-500 ease-out select-none
                      ${isActive
                        ? 'fluid-highlight text-white font-semibold'
                        : 'text-slate-300 hover:text-white hover:bg-white/5'
                      }
                    `}
                    style={isActive ? {
                      willChange: 'transform, opacity',
                    } : undefined}
                  >
                    {s.text}{' '}
                  </span>
                );
              })}
            </p>
          ))}

          {sentences.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p className="text-slate-500 text-sm font-medium">No document loaded</p>
              <p className="text-slate-600 text-xs mt-1">Upload a PDF, DOCX, TXT, or image to begin</p>
            </div>
          )}
        </div>
      </div>

      {/* Footer hint */}
      {sentences.length > 0 && (
        <div className="px-5 py-2 border-t border-white/5 text-center">
          <span className="text-[10px] text-slate-600 font-medium">
            Click any sentence to jump • {sentences.length} sentences
          </span>
        </div>
      )}
    </div>
  );
};

export default DocumentViewer;
