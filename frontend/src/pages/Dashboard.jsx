import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FileSearch, AlertTriangle, Shield, Files, TrendingUp, 
  Clock, ChevronRight, Play, RefreshCw, Activity, Zap
} from 'lucide-react';
import { AreaChart, Area, PieChart, Pie, Cell, Tooltip, ResponsiveContainer, XAxis, YAxis } from 'recharts';
import { getStats, listInvestigations, launchDemo } from '../services/api';
import { clsx } from 'clsx';

const RISK_COLORS = {
  critical: '#EF4444',
  high: '#F97316',
  moderate: '#F59E0B',
  low: '#22C55E',
};

const RISK_LABELS = {
  critical: 'Critical',
  high: 'High',
  moderate: 'Moderate',
  low: 'Low',
};

function StatCard({ icon: Icon, label, value, change, color = 'cyan' }) {
  const colorMap = {
    cyan: 'text-cyan-primary',
    red: 'text-red-400',
    green: 'text-green-400',
    yellow: 'text-yellow-400',
    purple: 'text-purple-400',
  };

  return (
    <div className="stat-card">
      <div className="flex items-center justify-between">
        <div className={clsx('p-2 rounded-lg', 
          color === 'cyan' ? 'bg-cyan-primary/10' :
          color === 'red' ? 'bg-red-500/10' :
          color === 'green' ? 'bg-green-500/10' :
          color === 'yellow' ? 'bg-yellow-500/10' : 'bg-purple-500/10'
        )}>
          <Icon className={clsx('w-5 h-5', colorMap[color])} />
        </div>
        {change !== undefined && (
          <span className={clsx('text-xs font-medium', change >= 0 ? 'text-green-400' : 'text-red-400')}>
            {change >= 0 ? '+' : ''}{change}%
          </span>
        )}
      </div>
      <div>
        <div className="text-2xl font-bold text-white">{value ?? '—'}</div>
        <div className="text-xs text-slate-400 mt-0.5">{label}</div>
      </div>
    </div>
  );
}

function RiskBadge({ level }) {
  if (!level) return null;
  const cls = {
    critical: 'badge-critical',
    high: 'badge-high',
    moderate: 'badge-moderate',
    low: 'badge-low',
  };
  return <span className={cls[level] || 'badge-low'}>{level?.toUpperCase()}</span>;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [investigations, setInvestigations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [demoLoading, setDemoLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [statsData, invData] = await Promise.all([
        getStats(),
        listInvestigations(0, 10),
      ]);
      setStats(statsData);
      setInvestigations(invData.investigations || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleLaunchDemo = async () => {
    setDemoLoading(true);
    try {
      const result = await launchDemo();
      navigate(`/investigation/${result.investigation_id}`);
    } catch (err) {
      alert('Failed to launch demo: ' + err.message);
    } finally {
      setDemoLoading(false);
    }
  };

  const riskDistribution = stats ? [
    { name: 'Critical', value: stats.risk_distribution?.critical || 0, color: '#EF4444' },
    { name: 'High', value: stats.risk_distribution?.high || 0, color: '#F97316' },
    { name: 'Moderate', value: stats.risk_distribution?.moderate || 0, color: '#F59E0B' },
    { name: 'Low', value: stats.risk_distribution?.low || 0, color: '#22C55E' },
  ].filter(d => d.value > 0) : [];

  const activityData = investigations.slice(0, 7).reverse().map((inv, i) => ({
    name: `D${i+1}`,
    anomalies: inv.anomaly_count || 0,
    documents: inv.document_count || 0,
  }));

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Forensics Command Center</h1>
          <p className="page-subtitle">PaperTrail — Document Forensics & Intelligence Platform</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="btn-secondary" disabled={loading}>
            <RefreshCw className={clsx('w-4 h-4', loading && 'animate-spin')} />
            Refresh
          </button>
          <button onClick={handleLaunchDemo} className="btn-primary" disabled={demoLoading}>
            {demoLoading ? <span className="spinner" /> : <Play className="w-4 h-4" />}
            Launch Demo Investigation
          </button>
          <button onClick={() => navigate('/investigation/new')} className="btn-primary">
            <FileSearch className="w-4 h-4" />
            New Investigation
          </button>
        </div>
      </div>

      {error && (
        <div className="glass-card p-4 border-red-500/30 bg-red-500/5">
          <div className="flex items-center gap-2 text-red-400">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-sm">{error}</span>
            <span className="text-xs text-slate-500 ml-2">— Make sure the backend is running on port 8000</span>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          icon={Files} 
          label="Total Documents Analyzed" 
          value={loading ? '...' : stats?.total_documents ?? 0} 
          color="cyan"
        />
        <StatCard 
          icon={Activity} 
          label="Total Investigations" 
          value={loading ? '...' : stats?.total_investigations ?? 0}
          color="purple"
        />
        <StatCard 
          icon={AlertTriangle} 
          label="Anomalies Identified" 
          value={loading ? '...' : stats?.total_anomalies ?? 0}
          color="red"
        />
        <StatCard 
          icon={Shield} 
          label="Requiring Review" 
          value={loading ? '...' : stats?.documents_requiring_review ?? 0}
          color="yellow"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Activity Chart */}
        <div className="glass-card p-5 col-span-2">
          <div className="section-header">
            <TrendingUp className="w-5 h-5 text-cyan-primary" />
            Document Processing Activity
          </div>
          {activityData.length > 0 ? (
            <ResponsiveContainer width="100%" height={160}>
              <AreaChart data={activityData}>
                <defs>
                  <linearGradient id="cyanGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#45D6E8" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#45D6E8" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="redGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip 
                  contentStyle={{ background: '#1a2d42', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
                />
                <Area type="monotone" dataKey="documents" stroke="#45D6E8" fill="url(#cyanGrad)" strokeWidth={2} />
                <Area type="monotone" dataKey="anomalies" stroke="#EF4444" fill="url(#redGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-40 flex items-center justify-center text-slate-500 text-sm">
              No investigation activity yet. Start your first investigation.
            </div>
          )}
        </div>

        {/* Risk Distribution */}
        <div className="glass-card p-5">
          <div className="section-header">
            <Shield className="w-5 h-5 text-cyan-primary" />
            Risk Distribution
          </div>
          {riskDistribution.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={120}>
                <PieChart>
                  <Pie data={riskDistribution} cx="50%" cy="50%" innerRadius={35} outerRadius={55} dataKey="value">
                    {riskDistribution.map((entry, index) => (
                      <Cell key={index} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#1a2d42', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-1 mt-2">
                {riskDistribution.map(d => (
                  <div key={d.name} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full" style={{ background: d.color }} />
                      <span className="text-slate-400">{d.name}</span>
                    </div>
                    <span className="text-white font-medium">{d.value}</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="h-32 flex items-center justify-center text-slate-500 text-sm text-center">
              No investigations yet
            </div>
          )}
        </div>
      </div>

      {/* Recent Investigations */}
      <div className="glass-card p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="section-header mb-0">
            <Clock className="w-5 h-5 text-cyan-primary" />
            Recent Investigations
          </div>
          <button onClick={() => navigate('/history')} className="btn-secondary text-xs py-1.5 px-3">
            View All <ChevronRight className="w-3 h-3" />
          </button>
        </div>

        {loading ? (
          <div className="text-center py-8 text-slate-500">Loading...</div>
        ) : investigations.length === 0 ? (
          <div className="text-center py-12">
            <FileSearch className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400 text-sm">No investigations yet</p>
            <p className="text-slate-500 text-xs mt-1">Start by launching the demo or creating a new investigation</p>
            <div className="flex items-center gap-3 justify-center mt-4">
              <button onClick={handleLaunchDemo} className="btn-primary text-xs" disabled={demoLoading}>
                <Play className="w-3 h-3" /> Launch Demo
              </button>
              <button onClick={() => navigate('/investigation/new')} className="btn-secondary text-xs">
                New Investigation
              </button>
            </div>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Investigation ID</th>
                  <th>Title</th>
                  <th>Documents</th>
                  <th>Anomalies</th>
                  <th>Risk Level</th>
                  <th>Risk Score</th>
                  <th>Date</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {investigations.map((inv) => (
                  <tr key={inv.id} 
                    className="cursor-pointer"
                    onClick={() => navigate(`/investigation/${inv.investigation_id}`)}
                  >
                    <td>
                      <span className="font-mono text-xs text-cyan-primary">{inv.investigation_id}</span>
                      {inv.is_demo && <span className="ml-2 text-xs text-yellow-400 font-medium">[DEMO]</span>}
                    </td>
                    <td className="text-white font-medium">{inv.title}</td>
                    <td>{inv.document_count || 0}</td>
                    <td>
                      {inv.anomaly_count > 0 ? (
                        <span className="text-red-400 font-medium">{inv.anomaly_count}</span>
                      ) : (
                        <span className="text-green-400">0</span>
                      )}
                    </td>
                    <td><RiskBadge level={inv.risk_level} /></td>
                    <td>
                      {inv.risk_score !== null && inv.risk_score !== undefined ? (
                        <div className="flex items-center gap-2">
                          <div className="risk-bar w-16">
                            <div 
                              className="h-full rounded-full" 
                              style={{ 
                                width: `${inv.risk_score}%`,
                                background: RISK_COLORS[inv.risk_level] || '#64748B',
                              }} 
                            />
                          </div>
                          <span className="text-xs text-slate-400">{Math.round(inv.risk_score)}</span>
                        </div>
                      ) : '—'}
                    </td>
                    <td className="text-slate-500 text-xs">
                      {new Date(inv.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <ChevronRight className="w-4 h-4 text-slate-500" />
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

