import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GitBranch, ChevronRight, AlertTriangle } from 'lucide-react';
import { listInvestigations, getInvestigation } from '../services/api';
import ComparisonTable from '../components/ComparisonTable';
import RelationshipGraph from '../components/RelationshipGraph';

export default function CrossDocumentIntelligence() {
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState([]);
  const [selected, setSelected] = useState(null);
  const [invData, setInvData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState('comparison');

  useEffect(() => {
    listInvestigations().then(d => setInvestigations(d.investigations || []));
  }, []);

  const handleSelect = async (inv) => {
    setSelected(inv);
    setLoading(true);
    try {
      const data = await getInvestigation(inv.investigation_id);
      setInvData(data);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-5">
      <div>
        <h1 className="page-title">Cross-Document Intelligence</h1>
        <p className="page-subtitle">Analyze relationships and inconsistencies across multiple documents</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
        {/* Investigation Selector */}
        <div className="glass-card p-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Select Investigation</h3>
          <div className="space-y-1">
            {investigations.map(inv => (
              <button
                key={inv.id}
                onClick={() => handleSelect(inv)}
                className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-all ${
                  selected?.id === inv.id 
                    ? 'bg-cyan-primary/15 border border-cyan-primary/30 text-white' 
                    : 'text-slate-400 hover:bg-white/5 hover:text-white'
                }`}
              >
                <div className="font-medium truncate">{inv.title}</div>
                <div className="text-xs text-slate-500 mt-0.5 flex items-center gap-1">
                  <span>{inv.document_count} docs</span>
                  {inv.anomaly_count > 0 && (
                    <span className="text-red-400">· {inv.anomaly_count} anomalies</span>
                  )}
                  {inv.is_demo && <span className="text-yellow-400">[DEMO]</span>}
                </div>
              </button>
            ))}
            {investigations.length === 0 && (
              <div className="text-xs text-slate-500 text-center py-4">
                No investigations yet.<br/>
                <button onClick={() => navigate('/investigation/new')} className="text-cyan-primary hover:underline mt-1">
                  Start one →
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-4">
          {!selected ? (
            <div className="glass-card p-12 text-center">
              <GitBranch className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400">Select an investigation to view cross-document analysis</p>
            </div>
          ) : loading ? (
            <div className="glass-card p-12 text-center">
              <div className="spinner mx-auto mb-3" />
              <p className="text-slate-400">Loading analysis...</p>
            </div>
          ) : invData ? (
            <>
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-white">{invData.title}</h2>
                  {invData.is_demo && <span className="demo-banner text-xs mt-1 inline-flex">⚠️ DEMO DATA</span>}
                </div>
                <button onClick={() => navigate(`/investigation/${invData.investigation_id}`)} className="btn-secondary text-xs">
                  Full Investigation <ChevronRight className="w-3 h-3" />
                </button>
              </div>

              {invData.anomalies.length > 0 && (
                <div className="glass-card p-4 border-red-500/20 bg-red-500/5">
                  <div className="flex items-center gap-2 text-red-400 text-sm font-medium mb-2">
                    <AlertTriangle className="w-4 h-4" />
                    {invData.anomalies.length} Anomaly(ies) Detected
                  </div>
                  <div className="space-y-1">
                    {invData.anomalies.map(a => (
                      <div key={a.anomaly_id} className="text-xs text-slate-400">
                        • <span className="text-red-300 font-medium">{a.field_name}:</span> {a.description}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex border-b border-white/10">
                {['comparison', 'graph'].map(t => (
                  <button
                    key={t}
                    onClick={() => setTab(t)}
                    className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-all capitalize ${
                      tab === t ? 'border-cyan-primary text-cyan-primary' : 'border-transparent text-slate-400 hover:text-white'
                    }`}
                  >
                    {t === 'comparison' ? 'Field Comparison Table' : 'Relationship Graph'}
                  </button>
                ))}
              </div>

              {tab === 'comparison' ? (
                <div className="glass-card p-5">
                  <ComparisonTable rows={invData.comparison_table || []} documents={invData.documents} />
                </div>
              ) : (
                <div className="glass-card p-5">
                  <div style={{ height: 500 }}>
                    <RelationshipGraph 
                      nodes={invData.graph_data?.nodes || []}
                      edges={invData.graph_data?.edges || []}
                    />
                  </div>
                </div>
              )}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}

