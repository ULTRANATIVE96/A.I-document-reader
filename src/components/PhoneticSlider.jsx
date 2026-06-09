import React from 'react';

const PhoneticSlider = ({ label, value, min = 0, max = 1, step = 0.01, onChange, unit = '', icon, gradient = 'from-indigo-500 to-purple-500' }) => {
  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div className="group">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {icon && <span className="text-indigo-400">{icon}</span>}
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-slate-300 transition-colors">
            {label}
          </span>
        </div>
        <span className="text-[12px] font-black text-indigo-300 tabular-nums">
          {typeof value === 'number' ? value.toFixed(step < 0.1 ? 2 : 1) : value}{unit}
        </span>
      </div>

      <div className="relative h-8 flex items-center">
        {/* Track background */}
        <div className="absolute inset-x-0 h-1.5 rounded-full bg-white/5 overflow-hidden">
          {/* Filled portion */}
          <div
            className={`h-full rounded-full bg-gradient-to-r ${gradient} transition-all duration-150 ease-out`}
            style={{ width: `${percentage}%` }}
          />
        </div>

        {/* Native range input (invisible but functional) */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="accent-slider absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
        />

        {/* Custom thumb */}
        <div
          className="absolute top-1/2 -translate-y-1/2 pointer-events-none transition-all duration-150 ease-out"
          style={{ left: `calc(${percentage}% - 8px)` }}
        >
          <div className={`w-4 h-4 rounded-full bg-gradient-to-br ${gradient} shadow-lg shadow-indigo-500/30 ring-2 ring-white/20 group-hover:ring-white/40 group-hover:scale-125 transition-all duration-200`} />
        </div>
      </div>
    </div>
  );
};

export default PhoneticSlider;
