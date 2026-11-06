import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { History as HistoryIcon, ChevronRight, Trash2, AlertTriangle } from 'lucide-react';
import { listInvestigations, deleteInvestigation } from '../services/api';

export default function History() {
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(null);

  const fetchData = () => {
    setLoading(true);
    listInvestigations(0, 100).then(d => {
      setInvestigations(d.investigations || []);
      setLoading(false);
    });
  };

  useEffect(() => { fetchData(); }, []);

  const handleDelete = async (invId) => {
    if (!window.confirm('Delete this investigation? This cannot be undone.')) return;
    setDeleting(invId);
    try {
      await deleteInvestigation(invId);
      fetchData();
    } catch (err) {
      alert('Delete failed: ' + err.message);
    } finally {
      setDeleting(null);
    }
  };

  const getRiskBadgeClass = (level) => ({
    critical: 'badge-critical',
    high: 'badge-high',
    moderate: 'badge-moderate',
    low: 'badge-low',
  }[level] || '');

  return (
    <div className="p-6 space-y-5">
      <div>
        <h1 className="page-title">Investigation History</h1>
        <p className="page-subtitle">Complete audit trail of all document investigations</p>
      </div>

      <div className="glass-card">
        <div className="p-4 border-b border-white/8 flex items-center justify-between">
          <div className="section-header mb-0">
            <HistoryIcon className="w-5 h-5 text-cyan-primary" />
            All Investigations ({investigations.length})
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12 text-slate-500">Loading history...</div>
        ) : investigations.length === 0 ? (
          <div className="text-center py-12">
            <HistoryIcon className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400">No investigation history</p>
            <button onClick={() => navigate('/investigation/new')} className="btn-primary mx-auto mt-4">
              Start First Investigation
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Docs</th>
                  <th>Anomalies</th>
                  <th>Risk</th>
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
                    <td className="text-white max-w-48 truncate">{inv.title}</td>
                    <td>
                      <span className={`text-xs font-medium ${
                        inv.status === 'completed' ? 'text-green-400' :
                        inv.status === 'processing' ? 'text-cyan-primary' :
                        inv.status === 'failed' ? 'text-red-400' : 'text-slate-400'
                      }`}>{inv.status}</span>
                    </td>
                    <td>{inv.document_count}</td>
                    <td className={inv.anomaly_count > 0 ? 'text-red-400' : 'text-green-400'}>
                      {inv.anomaly_count}
                    </td>
                    <td>
                      {inv.risk_level && (
                        <span className={getRiskBadgeClass(inv.risk_level)}>{inv.risk_level?.toUpperCase()}</span>
                      )}
                    </td>
                    <td className="text-xs text-slate-500">
                      {new Date(inv.created_at).toLocaleDateString()}<br/>
                      <span className="text-slate-600">{new Date(inv.created_at).toLocaleTimeString()}</span>
                    </td>
                    <td>
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => navigate(`/investigation/${inv.investigation_id}`)}
                          className="btn-secondary text-xs py-1 px-2"
                        >
                          <ChevronRight className="w-3 h-3" /> Open
                        </button>
                        {!inv.is_demo && (
                          <button
                            onClick={() => handleDelete(inv.investigation_id)}
                            disabled={deleting === inv.investigation_id}
                            className="p-1.5 rounded hover:bg-red-500/20 text-slate-500 hover:text-red-400 transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

