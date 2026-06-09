import React from 'react';

const WaveformIndicator = ({ isActive = false, barCount = 5 }) => {
  return (
    <div className="flex items-end gap-[3px] h-5">
      {Array.from({ length: barCount }).map((_, i) => (
        <div
          key={i}
          className={`w-[3px] rounded-full transition-all duration-300 ${
            isActive
              ? 'bg-gradient-to-t from-indigo-500 to-cyan-400 animate-waveform'
              : 'bg-white/10 h-1'
          }`}
          style={isActive ? {
            animationDelay: `${i * 0.12}s`,
            animationDuration: `${0.6 + Math.random() * 0.4}s`,
          } : {}}
        />
      ))}
    </div>
  );
};

export default WaveformIndicator;
