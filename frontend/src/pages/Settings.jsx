import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Check, X, AlertCircle } from 'lucide-react';
import { getSettings, checkHealth } from '../services/api';

function StatusRow({ label, value, ok }) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-white/5">
      <span className="text-sm text-slate-300">{label}</span>
      <div className="flex items-center gap-2">
        {ok ? (
          <span className="flex items-center gap-1 text-xs text-green-400">
            <Check className="w-3.5 h-3.5" /> Available
          </span>
        ) : (
          <span className="flex items-center gap-1 text-xs text-red-400">
            <X className="w-3.5 h-3.5" /> Not Available
          </span>
        )}
        {value && <span className="text-xs text-slate-500 font-mono">{value}</span>}
      </div>
    </div>
  );
}

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getSettings(), checkHealth()]).then(([s, h]) => {
      setSettings(s);
      setHealth(h);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 space-y-5 max-w-3xl">
      <div>
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">System configuration and status</p>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-500">Loading...</div>
      ) : (
        <>
          {/* System Status */}
          <div className="glass-card p-5">
            <h3 className="section-header">
              <SettingsIcon className="w-5 h-5 text-cyan-primary" />
              System Component Status
            </h3>
            {health && (
              <div>
                <StatusRow label="FastAPI Backend" value="localhost:8000" ok={true} />
                <StatusRow label="Tesseract OCR" value={health.ocr_available ? 'Installed' : 'Not found'} ok={health.ocr_available} />
                <StatusRow label="OpenCV (Computer Vision)" ok={health.vision_available} />
                <StatusRow label="Gemini AI Integration" ok={health.gemini_available} 
                  value={health.gemini_available ? 'API Key configured' : 'Using rule-based fallback'} />
                <StatusRow label="SQLite Database" ok={true} value="papertrail.db" />
                <StatusRow label="PyMuPDF (PDF Processing)" ok={true} />
              </div>
            )}
          </div>

          {/* Configuration */}
          {settings && (
            <div className="glass-card p-5">
              <h3 className="section-header">
                <SettingsIcon className="w-5 h-5 text-cyan-primary" />
                Configuration
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between py-2 border-b border-white/5">
                  <span className="text-slate-400">Max File Size</span>
                  <span className="text-white">{settings.max_file_size_mb} MB</span>
                </div>
                <div className="flex justify-between py-2 border-b border-white/5">
                  <span className="text-slate-400">Supported Formats</span>
                  <span className="text-white">{settings.supported_formats?.join(', ')}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-white/5">
                  <span className="text-slate-400">AI Explanation Source</span>
                  <span className={settings.gemini_configured ? 'text-cyan-primary' : 'text-yellow-400'}>
                    {settings.gemini_configured ? 'Gemini AI' : 'Rule-based fallback'}
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-white/5">
                  <span className="text-slate-400">Tesseract Path</span>
                  <span className="font-mono text-xs text-slate-300 max-w-64 truncate">{settings.tesseract_path}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-slate-400">Version</span>
                  <span className="text-white">{settings.version}</span>
                </div>
              </div>
            </div>
          )}

          {/* Gemini Setup */}
          {settings && !settings.gemini_configured && (
            <div className="glass-card p-5 border-yellow-500/20">
              <div className="flex items-start gap-2 mb-3">
                <AlertCircle className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
                <h3 className="text-sm font-semibold text-yellow-400">Configure Gemini AI (Optional)</h3>
              </div>
              <p className="text-sm text-slate-400 mb-3">
                PaperTrail works without Gemini AI using the built-in rule-based explanation engine. 
                To enable AI-powered explanations, add your Gemini API key to the .env file.
              </p>
              <div className="bg-black/30 rounded-lg p-3 font-mono text-xs text-green-400">
                # In papertrail/.env<br/>
                GEMINI_API_KEY=your_key_here
              </div>
              <p className="text-xs text-slate-500 mt-2">
                Restart the backend server after updating .env
              </p>
            </div>
          )}

          {/* Tesseract Setup */}
          {settings && !settings.tesseract_available && (
            <div className="glass-card p-5 border-orange-500/20">
              <div className="flex items-start gap-2 mb-3">
                <AlertCircle className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
                <h3 className="text-sm font-semibold text-orange-400">Install Tesseract OCR</h3>
              </div>
              <p className="text-sm text-slate-400 mb-3">
                Tesseract OCR is required for image-based text extraction. 
                Text-based PDFs still work without it.
              </p>
              <div className="bg-black/30 rounded-lg p-3 font-mono text-xs text-green-400 space-y-1">
                <div># Windows: Download installer from</div>
                <div className="text-cyan-primary">https://github.com/UB-Mannheim/tesseract/wiki</div>
                <div className="mt-2"># Then set path in .env:</div>
                <div>TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe</div>
              </div>
            </div>
          )}

          {/* System Limitations */}
          <div className="glass-card p-5">
            <h3 className="section-header">
              <AlertCircle className="w-5 h-5 text-yellow-400" />
              System Limitations
            </h3>
            <div className="space-y-2 text-sm text-slate-400">
              {[
                'OCR accuracy depends on document scan quality. Low-resolution images may yield incomplete extraction.',
                'ELA and visual forensic checks are heuristic tools and cannot conclusively prove manipulation.',
                'Risk scores are preliminary investigation indicators only — not proof of fraud.',
                'The system does not access external databases or verify documents against government records.',
                'AI explanations are supplementary observations, not definitive forensic conclusions.',
                'All findings require manual verification by qualified investigators.',
              ].map((lim, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-yellow-400 mt-0.5">•</span>
                  {lim}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

