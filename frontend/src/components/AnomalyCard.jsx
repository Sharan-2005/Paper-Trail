import React, { useState } from 'react';
import { 
  AlertTriangle, ChevronDown, ChevronUp, Bot, FileText, 
  HelpCircle, CheckCircle, ExternalLink, ShieldAlert
} from 'lucide-react';
import { clsx } from 'clsx';

export default function AnomalyCard({ anomaly, documents }) {
  const [expanded, setExpanded] = useState(false);

  const severityColors = {
    critical: {
      badge: 'badge-critical',
      border: 'border-red-500/30',
      bg: 'bg-red-500/5',
      icon: 'text-red-400',
    },
    high: {
      badge: 'badge-high',
      border: 'border-orange-500/30',
      bg: 'bg-orange-500/5',
      icon: 'text-orange-400',
    },
    medium: {
      badge: 'badge-moderate',
      border: 'border-yellow-500/30',
      bg: 'bg-yellow-500/5',
      icon: 'text-yellow-400',
    },
    low: {
      badge: 'badge-low',
      border: 'border-green-500/30',
      bg: 'bg-green-500/5',
      icon: 'text-green-400',
    },
  };

  const style = severityColors[anomaly.severity] || severityColors.medium;

  const getDocName = (docId) => {
    const doc = documents?.find(d => d.document_id === docId);
    return doc ? doc.filename : docId;
  };

  return (
    <div className={clsx('glass-card border', style.border, style.bg)}>
      {/* Header */}
      <div 
        className="p-4 flex items-start justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start gap-3">
          <div className={clsx('p-2 rounded-lg mt-0.5', 
            anomaly.severity === 'critical' ? 'bg-red-500/15' : 'bg-orange-500/15'
          )}>
            <AlertTriangle className={clsx('w-4 h-4', style.icon)} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-white font-medium text-sm">
                {anomaly.field_name} Discrepancy
              </span>
              <span className={style.badge}>{anomaly.severity.toUpperCase()}</span>
              <span className="text-xs font-mono text-slate-500">{anomaly.anomaly_id}</span>
            </div>
            <p className="text-xs text-slate-400 mt-1">{anomaly.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-500">+{anomaly.risk_points} pts</span>
          {expanded ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </div>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div className="border-t border-white/8 p-4 space-y-4">
          {/* Conflicting Values Comparison */}
          {anomaly.conflicting_values && Object.keys(anomaly.conflicting_values).length > 0 && (
            <div>
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Conflicting Evidence
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {Object.entries(anomaly.conflicting_values).map(([docId, value]) => (
                  <div key={docId} className="glass-card p-3 bg-black/20">
                    <div className="text-xs text-slate-500 truncate flex items-center gap-1">
                      <FileText className="w-3 h-3 text-cyan-primary" />
                      {getDocName(docId)}
                    </div>
                    <div className="text-white font-medium text-sm mt-1">"{value}"</div>
                    <div className="text-xs font-mono text-slate-600 mt-0.5">{docId}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI / Rule Explanation */}
          {anomaly.ai_explanation && (
            <div className="glass-card p-4 border-purple-500/20 bg-purple-500/5">
              <div className="flex items-center gap-2 text-purple-400 text-xs font-semibold uppercase tracking-wider mb-2">
                <Bot className="w-4 h-4" />
                Investigation Assistant Note
                <span className="text-xs text-slate-500 font-normal">
                  ({anomaly.explanation_source === 'ai' ? 'Gemini AI' : 'Rule-Based Engine'})
                </span>
              </div>
              <div className="text-xs text-slate-300 space-y-2 leading-relaxed">
                {anomaly.ai_explanation.split('\n\n').map((paragraph, i) => (
                  <p key={i}>
                    {paragraph.split('**').map((part, j) => 
                      j % 2 === 1 ? <strong key={j} className="text-white font-semibold">{part}</strong> : part
                    )}
                  </p>
                ))}
              </div>
            </div>
          )}

          {/* Verification Guidance */}
          <div className="glass-card p-3 border-cyan-primary/20 bg-cyan-primary/5">
            <div className="text-xs font-semibold text-cyan-primary mb-1 flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5" /> Recommended Next Steps
            </div>
            <ul className="text-xs text-slate-400 space-y-1 list-disc list-inside">
              <li>Request applicant to provide primary identity document to clarify discrepancy</li>
              <li>Verify details directly with the relevant issuing authority if possible</li>
              <li>Document manual verification outcome in the case file</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

