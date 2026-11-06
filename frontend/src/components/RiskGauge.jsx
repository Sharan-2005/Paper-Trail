import React from 'react';
import { Shield, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { clsx } from 'clsx';

export default function RiskGauge({ score, level, factors = [], detailed = false }) {
  const getRiskColor = (lvl) => {
    switch (lvl) {
      case 'critical': return '#EF4444';
      case 'high': return '#F97316';
      case 'moderate': return '#F59E0B';
      case 'low': return '#22C55E';
      default: return '#64748B';
    }
  };

  const color = getRiskColor(level);
  const normalizedScore = Math.min(100, Math.max(0, Math.round(score)));

  // SVG arc calculation
  const radius = 70;
  const circumference = Math.PI * radius; // semicircle
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  return (
    <div className="glass-card p-5">
      <div className="section-header">
        <Shield className="w-5 h-5 text-cyan-primary" />
        Preliminary Risk Assessment
      </div>

      {/* Gauge */}
      <div className="flex flex-col items-center justify-center my-4">
        <div className="relative w-48 h-28 flex items-end justify-center">
          <svg className="w-48 h-28 overflow-visible" viewBox="0 0 160 90">
            {/* Background Arc */}
            <path
              d="M 10 80 A 70 70 0 0 1 150 80"
              fill="none"
              stroke="rgba(255,255,255,0.1)"
              strokeWidth="12"
              strokeLinecap="round"
            />
            {/* Value Arc */}
            <path
              d="M 10 80 A 70 70 0 0 1 150 80"
              fill="none"
              stroke={color}
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
            />
          </svg>

          {/* Center text */}
          <div className="absolute bottom-0 text-center">
            <div className="text-3xl font-bold text-white leading-none">{normalizedScore}</div>
            <div className="text-xs text-slate-400 mt-1">/ 100</div>
          </div>
        </div>

        {/* Level Badge */}
        <div 
          className="mt-3 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider"
          style={{ 
            background: `${color}20`, 
            color: color, 
            border: `1px solid ${color}40` 
          }}
        >
          {level || 'LOW'} RISK
        </div>
      </div>

      {/* Factors Breakdown */}
      {factors.length > 0 && (
        <div className="mt-4 border-t border-white/8 pt-3 space-y-2">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Contributing Factors
          </div>
          {factors.map((factor, i) => (
            <div key={i} className="flex items-center justify-between text-xs">
              <span className="text-slate-300">{factor.field}</span>
              <span className="font-mono text-slate-400">+{factor.points} pts</span>
            </div>
          ))}
        </div>
      )}

      {/* Disclaimer */}
      <div className="mt-4 p-2.5 rounded-lg bg-white/3 border border-white/5 flex items-start gap-2">
        <Info className="w-3.5 h-3.5 text-slate-500 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-slate-500 leading-relaxed">
          Preliminary investigation indicator only. Not proof of fraud. 
          All findings require manual verification.
        </p>
      </div>
    </div>
  );
}

