import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { listInvestigations, getInvestigation, runForensics } from '../services/api';

export default function VisualForensics() {
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState([]);
  const [selected, setSelected] = useState(null);
  const [invData, setInvData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState({});
  const [forensicResults, setForensicResults] = useState({});

  useEffect(() => {
    listInvestigations().then(d => setInvestigations(d.investigations || []));
  }, []);

  const handleSelect = async (inv) => {
    setSelected(inv);
    setLoading(true);
    try {
      const data = await getInvestigation(inv.investigation_id);
      setInvData(data);
    } catch (err) { alert(err.message); }
    finally { setLoading(false); }
  };

  const handleRunForensics = async (docId) => {
    setAnalyzing(prev => ({ ...prev, [docId]: true }));
    try {
      const result = await runForensics(docId);
      setForensicResults(prev => ({ ...prev, [docId]: result.forensic_results }));
    } catch (err) {
      alert('Forensics failed: ' + err.message);
    } finally {
      setAnalyzing(prev => ({ ...prev, [docId]: false }));
    }
  };

  const getSeverityBadge = (val) => {
    if (val) return <span className="text-xs text-red-400 bg-red-500/10 px-1.5 py-0.5 rounded">⚠ Anomaly</span>;
    return <span className="text-xs text-green-400 bg-green-500/10 px-1.5 py-0.5 rounded">✓ Normal</span>;
  };

  return (
    <div className="p-6 space-y-5">
      <div>
        <h1 className="page-title">Visual Document Forensics</h1>
        <p className="page-subtitle">Preliminary image forensic analysis — ELA, metadata inspection, compression analysis</p>
      </div>

      <div className="glass-card p-4 border-cyan-primary/20 bg-cyan-primary/5">
        <div className="flex items-start gap-2">
          <Info className="w-4 h-4 text-cyan-primary flex-shrink-0 mt-0.5" />
          <div className="text-xs text-slate-300">
            <span className="font-semibold text-cyan-primary">Important Disclaimer: </span>
            Visual forensic analysis provides preliminary observations only. ELA, compression analysis, and 
            brightness checks are heuristic tools and cannot conclusively prove document manipulation. 
            All findings require manual verification by qualified forensic examiners. 
            Visual forensics is available for image documents (JPG, JPEG, PNG) only.
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
        <div className="glass-card p-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Select Investigation</h3>
          <div className="space-y-1">
            {investigations.map(inv => (
              <button key={inv.id} onClick={() => handleSelect(inv)}
                className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-all ${
                  selected?.id === inv.id ? 'bg-cyan-primary/15 border border-cyan-primary/30 text-white' : 'text-slate-400 hover:bg-white/5 hover:text-white'
                }`}>
                <div className="font-medium truncate">{inv.title}</div>
                <div className="text-xs text-slate-500">{inv.document_count} docs</div>
              </button>
            ))}
          </div>
        </div>

        <div className="lg:col-span-3 space-y-4">
          {!selected ? (
            <div className="glass-card p-12 text-center">
              <Eye className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400">Select an investigation to run visual forensics</p>
            </div>
          ) : loading ? (
            <div className="glass-card p-12 text-center"><div className="spinner mx-auto" /></div>
          ) : invData ? (
            invData.documents.map(doc => {
              const isImage = ['jpg', 'jpeg', 'png'].includes(doc.file_type?.toLowerCase());
              const result = forensicResults[doc.document_id];
              const existingForensics = doc.forensic_results;

              return (
                <div key={doc.document_id} className="glass-card p-5">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-white font-medium">{doc.filename}</h3>
                      <div className="text-xs text-slate-500 mt-0.5">
                        {doc.file_type?.toUpperCase()} · {doc.document_type?.replace(/_/g, ' ')}
                      </div>
                    </div>
                    {isImage && (
                      <button
                        onClick={() => handleRunForensics(doc.document_id)}
                        disabled={analyzing[doc.document_id]}
                        className="btn-primary text-xs py-1.5 px-3"
                      >
                        {analyzing[doc.document_id] ? <span className="spinner" /> : <Eye className="w-3.5 h-3.5" />}
                        Run Analysis
                      </button>
                    )}
                  </div>

                  {!isImage && (
                    <div className="text-sm text-slate-500 italic">
                      PDF documents: individual page images extracted during OCR processing. 
                      Upload image files directly for detailed visual forensics.
                    </div>
                  )}

                  {isImage && !result && existingForensics?.length === 0 && (
                    <div className="text-sm text-slate-500">
                      Click "Run Analysis" to perform visual forensic checks on this image.
                    </div>
                  )}

                  {/* Show existing forensics from processing */}
                  {existingForensics?.length > 0 && !result && (
                    <div className="space-y-2">
                      {existingForensics.map((fr, i) => (
                        <div key={i} className={`p-3 rounded-lg text-sm ${
                          fr.severity === 'warning' ? 'bg-yellow-500/10 border border-yellow-500/20' : 'bg-green-500/10 border border-green-500/20'
                        }`}>
                          <div className="font-medium">{fr.result_type}: {fr.finding}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Show fresh forensics results */}
                  {result && (
                    <div className="space-y-3">
                      <div className={`p-3 rounded-lg ${
                        result.summary?.overall_assessment === 'significant_anomaly' ? 'bg-red-500/10 border border-red-500/20' :
                        result.summary?.overall_assessment === 'moderate_anomaly' ? 'bg-yellow-500/10 border border-yellow-500/20' :
                        result.summary?.overall_assessment === 'minor_anomaly' ? 'bg-orange-500/10 border border-orange-500/20' :
                        'bg-green-500/10 border border-green-500/20'
                      }`}>
                        <div className="text-sm font-medium text-white mb-1">
                          Overall Assessment: {result.summary?.overall_assessment?.replace(/_/g, ' ').toUpperCase()}
                        </div>
                        <div className="text-xs text-slate-400">
                          {result.summary?.total_checks} checks performed · {result.summary?.suspicious_findings} potential anomaly(ies) noted
                        </div>
                      </div>

                      {result.checks && Object.entries(result.checks).map(([checkName, checkData]) => {
                        if (!checkData || typeof checkData !== 'object' || !checkData.available) return null;
                        return (
                          <div key={checkName} className="glass-card p-3">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm font-medium text-white capitalize">
                                {checkName.replace(/_/g, ' ')}
                              </span>
                              {getSeverityBadge(checkData.potentially_suspicious)}
                            </div>
                            {checkData.interpretation && (
                              <p className="text-xs text-slate-400">{checkData.interpretation}</p>
                            )}
                            {checkData.editing_software_detected?.length > 0 && (
                              <div className="text-xs text-yellow-400 mt-1">
                                ⚠ Editing software detected: {checkData.editing_software_detected.join(', ')}
                              </div>
                            )}
                            {checkData.ela_image_url && (
                              <div className="mt-2">
                                <div className="text-xs text-slate-500 mb-1">ELA Visualization:</div>
                                <img 
                                  src={`http://localhost:8000${checkData.ela_image_url}`} 
                                  alt="ELA Result" 
                                  className="max-w-full rounded-lg border border-white/10"
                                  style={{ maxHeight: 200 }}
                                />
                              </div>
                            )}
                          </div>
                        );
                      })}

                      {result.disclaimer && (
                        <div className="text-xs text-slate-500 italic border-t border-white/5 pt-2">
                          {result.disclaimer}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          ) : null}
        </div>
      </div>
    </div>
  );
}

