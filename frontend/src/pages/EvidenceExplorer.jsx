import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, AlertTriangle, ChevronRight, Filter } from 'lucide-react';
import { listInvestigations, getInvestigation } from '../services/api';
import AnomalyCard from '../components/AnomalyCard';

export default function EvidenceExplorer() {
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState([]);
  const [allAnomalies, setAllAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const { investigations: invs } = await listInvestigations();
        setInvestigations(invs);
        
        const anomalies = [];
        for (const inv of invs.slice(0, 10)) {
          try {
            const data = await getInvestigation(inv.investigation_id);
            data.anomalies.forEach(a => {
              anomalies.push({
                ...a,
                investigation_id: inv.investigation_id,
                investigation_title: inv.title,
                documents: data.documents,
                is_demo: inv.is_demo,
              });
            });
          } catch {}
        }
        setAllAnomalies(anomalies);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const filtered = allAnomalies.filter(a => {
    if (filter !== 'all' && a.severity !== filter) return false;
    if (search && !a.description.toLowerCase().includes(search.toLowerCase()) &&
        !a.field_name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="p-6 space-y-5">
      <div>
        <h1 className="page-title">Evidence Explorer</h1>
        <p className="page-subtitle">Browse all detected anomalies across investigations</p>
      </div>

      {/* Filters */}
      <div className="glass-card p-4 flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2 flex-1 min-w-48">
          <Filter className="w-4 h-4 text-slate-400" />
          <input
            className="input-field py-1.5"
            placeholder="Search anomalies..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          {['all', 'critical', 'high', 'medium', 'low'].map(sev => (
            <button
              key={sev}
              onClick={() => setFilter(sev)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all capitalize ${
                filter === sev
                  ? 'bg-cyan-primary text-navy-200'
                  : 'bg-white/5 text-slate-400 hover:text-white'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: 'Total Anomalies', value: allAnomalies.length, color: 'text-white' },
          { label: 'Critical', value: allAnomalies.filter(a => a.severity === 'critical').length, color: 'text-red-400' },
          { label: 'High', value: allAnomalies.filter(a => a.severity === 'high').length, color: 'text-orange-400' },
          { label: 'Medium', value: allAnomalies.filter(a => a.severity === 'medium').length, color: 'text-yellow-400' },
        ].map(s => (
          <div key={s.label} className="glass-card p-4">
            <div className="text-xs text-slate-400">{s.label}</div>
            <div className={`text-2xl font-bold mt-1 ${s.color}`}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Anomaly List */}
      {loading ? (
        <div className="text-center py-12 text-slate-500">Loading evidence...</div>
      ) : filtered.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <BookOpen className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No anomalies found</p>
          {allAnomalies.length === 0 && (
            <p className="text-slate-500 text-sm mt-1">Start investigations to see evidence here</p>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filtered.map(a => (
            <div key={`${a.investigation_id}-${a.anomaly_id}`}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs text-slate-500">Investigation:</span>
                <button 
                  onClick={() => navigate(`/investigation/${a.investigation_id}`)}
                  className="text-xs text-cyan-primary hover:underline font-mono"
                >
                  {a.investigation_id}
                </button>
                <span className="text-xs text-slate-500">— {a.investigation_title}</span>
                {a.is_demo && <span className="text-xs text-yellow-400">[DEMO]</span>}
              </div>
              <AnomalyCard anomaly={a} documents={a.documents || []} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

