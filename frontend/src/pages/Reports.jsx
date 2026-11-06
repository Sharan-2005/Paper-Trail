import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Download, Loader2, ChevronRight } from 'lucide-react';
import { listInvestigations, generateReport } from '../services/api';

export default function Reports() {
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState({});

  useEffect(() => {
    listInvestigations().then(d => {
      setInvestigations(d.investigations || []);
      setLoading(false);
    });
  }, []);

  const handleGenerate = async (invId) => {
    setGenerating(prev => ({ ...prev, [invId]: true }));
    try {
      const result = await generateReport(invId);
      window.open(`http://localhost:8000${result.download_url}`, '_blank');
    } catch (err) {
      alert('Report generation failed: ' + err.message);
    } finally {
      setGenerating(prev => ({ ...prev, [invId]: false }));
    }
  };

  const getRiskClass = (level) => ({
    critical: 'text-red-400',
    high: 'text-orange-400',
    moderate: 'text-yellow-400',
    low: 'text-green-400',
  }[level] || 'text-slate-400');

  return (
    <div className="p-6 space-y-5">
      <div>
        <h1 className="page-title">Investigation Reports</h1>
        <p className="page-subtitle">Generate and download professional PDF investigation dossiers</p>
      </div>

      <div className="glass-card p-5">
        <h3 className="section-header">
          <FileText className="w-5 h-5 text-cyan-primary" />
          Available Investigations
        </h3>

        {loading ? (
          <div className="text-center py-8 text-slate-500">Loading...</div>
        ) : investigations.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            No investigations available.
            <button onClick={() => navigate('/investigation/new')} className="block mx-auto mt-2 text-cyan-primary hover:underline text-sm">
              Create one →
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Investigation</th>
                  <th>Title</th>
                  <th>Documents</th>
                  <th>Anomalies</th>
                  <th>Risk Level</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {investigations.map(inv => (
                  <tr key={inv.id}>
                    <td>
                      <span className="font-mono text-xs text-cyan-primary">{inv.investigation_id}</span>
                      {inv.is_demo && <span className="ml-1 text-xs text-yellow-400">[DEMO]</span>}
                    </td>
                    <td className="text-white">{inv.title}</td>
                    <td>{inv.document_count}</td>
                    <td className={inv.anomaly_count > 0 ? 'text-red-400 font-medium' : 'text-green-400'}>
                      {inv.anomaly_count}
                    </td>
                    <td>
                      <span className={`font-medium text-xs uppercase ${getRiskClass(inv.risk_level)}`}>
                        {inv.risk_level || '—'}
                      </span>
                    </td>
                    <td className="text-xs text-slate-500">{new Date(inv.created_at).toLocaleDateString()}</td>
                    <td>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => navigate(`/investigation/${inv.investigation_id}`)}
                          className="btn-secondary text-xs py-1 px-2.5"
                        >
                          <ChevronRight className="w-3 h-3" /> View
                        </button>
                        <button
                          onClick={() => handleGenerate(inv.investigation_id)}
                          disabled={generating[inv.investigation_id]}
                          className="btn-primary text-xs py-1 px-2.5"
                        >
                          {generating[inv.investigation_id] 
                            ? <Loader2 className="w-3 h-3 animate-spin" /> 
                            : <Download className="w-3 h-3" />
                          }
                          PDF
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="glass-card p-4 border-cyan-primary/15">
        <h3 className="text-sm font-semibold text-white mb-2">Report Contents</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs text-slate-400">
          {[
            'PaperTrail Branding',
            'Investigation ID & Date',
            'Document Overview',
            'Extracted Information',
            'Cross-Document Comparison',
            'Contextual Discrepancies',
            'Visual Forensic Observations',
            'Anomaly Details & Evidence',
            'Risk Score & Explanation',
            'Manual Verification Guidance',
            'System Limitations',
            'Supporting Evidence References',
          ].map(item => (
            <div key={item} className="flex items-center gap-1.5">
              <div className="w-1 h-1 rounded-full bg-cyan-primary" />
              {item}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

