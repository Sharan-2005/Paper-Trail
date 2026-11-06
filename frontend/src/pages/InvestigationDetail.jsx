import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, FileText, AlertTriangle, Shield, Download, 
  RefreshCw, ChevronDown, ChevronUp, Eye, BookOpen,
  GitBranch, Loader2, CheckCircle, XCircle, Info,
  Edit2, Save, X
} from 'lucide-react';
import { clsx } from 'clsx';
import { getInvestigation, generateReport, updateDocumentFields } from '../services/api';
import RelationshipGraph from '../components/RelationshipGraph';
import ComparisonTable from '../components/ComparisonTable';
import AnomalyCard from '../components/AnomalyCard';
import RiskGauge from '../components/RiskGauge';

function RiskBadge({ level }) {
  const cls = {
    critical: 'badge-critical',
    high: 'badge-high',
    moderate: 'badge-moderate',
    low: 'badge-low',
  };
  return <span className={cls[level] || 'badge-low'}>{level?.toUpperCase()}</span>;
}

function DocumentCard({ doc, onFieldUpdate }) {
  const [expanded, setExpanded] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editFields, setEditFields] = useState({});
  const [saving, setSaving] = useState(false);

  const handleEdit = () => {
    setEditFields({ ...doc.extracted_fields });
    setEditing(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateDocumentFields(doc.document_id, editFields);
      onFieldUpdate?.(doc.document_id, editFields);
      setEditing(false);
    } catch (err) {
      alert('Failed to save: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const docTypeColors = {
    identity_document: 'text-blue-400 bg-blue-500/10',
    pan_document: 'text-purple-400 bg-purple-500/10',
    bank_statement: 'text-green-400 bg-green-500/10',
    salary_slip: 'text-yellow-400 bg-yellow-500/10',
    default: 'text-slate-400 bg-slate-500/10',
  };

  const fields = doc.extracted_fields || {};

  return (
    <div className="glass-card">
      {/* Document Header */}
      <div 
        className="p-4 flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-primary/10">
            <FileText className="w-4 h-4 text-cyan-primary" />
          </div>
          <div>
            <div className="text-white font-medium text-sm">{doc.filename}</div>
            <div className="flex items-center gap-2 mt-0.5">
              <span className={clsx('text-xs px-2 py-0.5 rounded-full font-medium', 
                docTypeColors[doc.document_type] || docTypeColors.default
              )}>
                {doc.document_type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Unknown'}
              </span>
              <span className="text-xs text-slate-500">{doc.page_count} page{doc.page_count > 1 ? 's' : ''}</span>
              <span className={clsx('text-xs', doc.processing_status === 'completed' ? 'text-green-400' : 'text-yellow-400')}>
                {doc.processing_status}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-mono">{doc.document_id}</span>
          {expanded ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </div>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div className="border-t border-white/8 p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Extracted Information</span>
            {Object.keys(fields).length > 0 && !editing && (
              <button onClick={handleEdit} className="btn-secondary text-xs py-1 px-2.5">
                <Edit2 className="w-3 h-3" /> Edit Fields
              </button>
            )}
            {editing && (
              <div className="flex items-center gap-2">
                <button onClick={() => setEditing(false)} className="btn-secondary text-xs py-1 px-2.5">
                  <X className="w-3 h-3" /> Cancel
                </button>
                <button onClick={handleSave} disabled={saving} className="btn-primary text-xs py-1 px-2.5">
                  {saving ? <Loader2 className="w-3 h-3 animate-spin" /> : <Save className="w-3 h-3" />}
                  Save
                </button>
              </div>
            )}
          </div>

          {Object.keys(fields).length === 0 ? (
            <div className="text-sm text-slate-500 italic">
              No fields extracted. {doc.processing_status === 'failed' ? 'Processing failed.' : 'Install Tesseract OCR for text extraction.'}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {Object.entries(editing ? editFields : fields).map(([key, value]) => (
                <div key={key} className="flex flex-col gap-0.5">
                  <label className="text-xs text-slate-500 uppercase tracking-wider">
                    {key.replace(/_/g, ' ')}
                  </label>
                  {editing ? (
                    <input
                      className="input-field py-1.5 text-xs"
                      value={editFields[key] || ''}
                      onChange={e => setEditFields(prev => ({ ...prev, [key]: e.target.value }))}
                    />
                  ) : (
                    <span className="text-sm text-white font-medium">{value}</span>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Forensic Results */}
          {doc.forensic_results?.length > 0 && (
            <div className="mt-4 border-t border-white/8 pt-4">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Visual Forensic Observations
              </div>
              {doc.forensic_results.map((fr, i) => (
                <div key={i} className={clsx('text-xs p-2 rounded-lg mb-1', 
                  fr.severity === 'warning' ? 'bg-yellow-500/10 text-yellow-400' : 'bg-green-500/10 text-green-400'
                )}>
                  {fr.finding}: {fr.details?.summary?.overall_assessment || 'Analysis complete'}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function InvestigationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [generating, setGenerating] = useState(false);
  const [reportUrl, setReportUrl] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const result = await getInvestigation(id);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      const result = await generateReport(id);
      setReportUrl(`http://localhost:8000${result.download_url}`);
      window.open(`http://localhost:8000${result.download_url}`, '_blank');
    } catch (err) {
      alert('Report generation failed: ' + err.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleFieldUpdate = (docId, newFields) => {
    setData(prev => ({
      ...prev,
      documents: prev.documents.map(d => 
        d.document_id === docId ? { ...d, extracted_fields: newFields } : d
      ),
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-cyan-primary animate-spin mx-auto mb-3" />
          <p className="text-slate-400">Loading investigation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="glass-card p-6 border-red-500/30">
          <div className="flex items-center gap-2 text-red-400 mb-2">
            <AlertTriangle className="w-5 h-5" />
            <span className="font-medium">Error loading investigation</span>
          </div>
          <p className="text-sm text-slate-400">{error}</p>
          <button onClick={() => navigate(-1)} className="btn-secondary mt-4">
            <ArrowLeft className="w-4 h-4" /> Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const TABS = [
    { id: 'overview', label: 'Overview', icon: Eye },
    { id: 'documents', label: `Documents (${data.documents.length})`, icon: FileText },
    { id: 'comparison', label: 'Cross-Document Analysis', icon: GitBranch },
    { id: 'graph', label: 'Relationship Graph', icon: GitBranch },
    { id: 'anomalies', label: `Anomalies (${data.anomalies.length})`, icon: AlertTriangle },
    { id: 'risk', label: 'Risk Assessment', icon: Shield },
  ];

  return (
    <div className="p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="btn-secondary py-2 px-3">
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white">{data.title}</h1>
              {data.is_demo && (
                <span className="demo-banner text-xs py-0.5 px-2">⚠️ DEMO DATA</span>
              )}
            </div>
            <div className="flex items-center gap-3 mt-0.5">
              <span className="text-xs font-mono text-cyan-primary">{data.investigation_id}</span>
              <span className="text-xs text-slate-500">
                {new Date(data.created_at).toLocaleString()}
              </span>
              <RiskBadge level={data.risk_level} />
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="btn-secondary">
            <RefreshCw className="w-4 h-4" />
          </button>
          <button onClick={handleGenerateReport} disabled={generating} className="btn-primary">
            {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
            Download PDF Dossier
          </button>
        </div>
      </div>

      {/* Demo banner */}
      {data.is_demo && (
        <div className="demo-banner">
          ⚠️ DEMONSTRATION MODE — All data shown is fictional and for demo purposes only. Not real documents.
        </div>
      )}

      {/* Summary */}
      {data.summary && (
        <div className="glass-card p-4 border-cyan-primary/15">
          <div className="flex items-start gap-2">
            <Info className="w-4 h-4 text-cyan-primary flex-shrink-0 mt-0.5" />
            <p className="text-sm text-slate-300">{data.summary}</p>
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: 'Documents', value: data.documents.length, icon: FileText, color: 'cyan' },
          { label: 'Anomalies', value: data.anomalies.length, icon: AlertTriangle, color: 'red' },
          { label: 'Risk Score', value: `${Math.round(data.risk_score || 0)}/100`, icon: Shield, color: data.risk_level === 'critical' ? 'red' : data.risk_level === 'high' ? 'yellow' : 'green' },
          { label: 'Risk Level', value: data.risk_level?.toUpperCase() || 'N/A', icon: BookOpen, color: 'purple' },
        ].map(stat => (
          <div key={stat.label} className="glass-card p-4">
            <div className="text-xs text-slate-400 mb-1">{stat.label}</div>
            <div className={clsx('text-2xl font-bold', {
              'text-cyan-primary': stat.color === 'cyan',
              'text-red-400': stat.color === 'red',
              'text-yellow-400': stat.color === 'yellow',
              'text-green-400': stat.color === 'green',
              'text-purple-400': stat.color === 'purple',
            })}>{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/10 overflow-x-auto">
        {TABS.map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={clsx(
                'flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 transition-all whitespace-nowrap',
                activeTab === tab.id
                  ? 'border-cyan-primary text-cyan-primary'
                  : 'border-transparent text-slate-400 hover:text-white'
              )}
            >
              <Icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div>
        {/* Overview */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <RiskGauge score={data.risk_score || 0} level={data.risk_level} factors={data.risk_assessment?.factors || []} />
            <div className="glass-card p-5">
              <h3 className="section-header">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                Key Findings
              </h3>
              {data.anomalies.length === 0 ? (
                <div className="flex items-center gap-2 text-green-400 text-sm">
                  <CheckCircle className="w-4 h-4" />
                  No anomalies detected in this investigation
                </div>
              ) : (
                <div className="space-y-2">
                  {data.anomalies.slice(0, 3).map(a => (
                    <div key={a.anomaly_id} className={clsx('p-3 rounded-lg text-sm', {
                      'bg-red-500/10 border border-red-500/20': a.severity === 'critical',
                      'bg-orange-500/10 border border-orange-500/20': a.severity === 'high',
                      'bg-yellow-500/10 border border-yellow-500/20': a.severity === 'medium',
                    })}>
                      <div className="flex items-center gap-2 mb-1">
                        <AlertTriangle className={clsx('w-3.5 h-3.5', {
                          'text-red-400': a.severity === 'critical',
                          'text-orange-400': a.severity === 'high',
                          'text-yellow-400': a.severity === 'medium',
                        })} />
                        <span className="font-medium text-white text-xs">{a.field_name} Mismatch</span>
                      </div>
                      <p className="text-xs text-slate-400">{a.description}</p>
                    </div>
                  ))}
                  {data.anomalies.length > 3 && (
                    <button onClick={() => setActiveTab('anomalies')} className="text-xs text-cyan-primary hover:underline">
                      View all {data.anomalies.length} anomalies →
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Documents */}
        {activeTab === 'documents' && (
          <div className="space-y-3">
            {data.documents.map(doc => (
              <DocumentCard key={doc.document_id} doc={doc} onFieldUpdate={handleFieldUpdate} />
            ))}
          </div>
        )}

        {/* Cross-Document Comparison */}
        {activeTab === 'comparison' && (
          <div className="glass-card p-5">
            <div className="section-header">
              <GitBranch className="w-5 h-5 text-cyan-primary" />
              Cross-Document Field Comparison
            </div>
            <ComparisonTable 
              rows={data.comparison_table || []} 
              documents={data.documents}
            />
          </div>
        )}

        {/* Relationship Graph */}
        {activeTab === 'graph' && (
          <div className="glass-card p-5">
            <div className="section-header">
              <GitBranch className="w-5 h-5 text-cyan-primary" />
              Document Relationship Graph
              <span className="text-xs text-slate-500 font-normal ml-2">
                Green = matching · Red = conflicting
              </span>
            </div>
            <div style={{ height: 500 }}>
              <RelationshipGraph 
                nodes={data.graph_data?.nodes || []}
                edges={data.graph_data?.edges || []}
              />
            </div>
          </div>
        )}

        {/* Anomalies */}
        {activeTab === 'anomalies' && (
          <div className="space-y-4">
            {data.anomalies.length === 0 ? (
              <div className="glass-card p-8 text-center">
                <CheckCircle className="w-10 h-10 text-green-400 mx-auto mb-3" />
                <p className="text-slate-300 font-medium">No anomalies detected</p>
                <p className="text-slate-500 text-sm mt-1">All cross-document comparisons are consistent</p>
              </div>
            ) : (
              data.anomalies.map(a => <AnomalyCard key={a.anomaly_id} anomaly={a} documents={data.documents} />)
            )}
          </div>
        )}

        {/* Risk Assessment */}
        {activeTab === 'risk' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <RiskGauge 
              score={data.risk_score || 0} 
              level={data.risk_level} 
              factors={data.risk_assessment?.factors || []}
              detailed 
            />
            <div className="glass-card p-5">
              <h3 className="section-header">
                <Shield className="w-5 h-5 text-cyan-primary" />
                Risk Scoring Methodology
              </h3>
              <div className="space-y-2 text-sm text-slate-400">
                {[
                  { field: 'Name Mismatch', points: 25 },
                  { field: 'Date of Birth Mismatch', points: 25 },
                  { field: 'Duplicate Document Number', points: 25 },
                  { field: 'Address Mismatch', points: 15 },
                  { field: 'Other Field Mismatches', points: 10 },
                ].map(item => (
                  <div key={item.field} className="flex justify-between items-center">
                    <span>{item.field}</span>
                    <span className="font-mono text-slate-300">{item.points} pts</span>
                  </div>
                ))}
              </div>
              <div className="border-t border-white/10 mt-3 pt-3 text-xs text-slate-500">
                Score is normalized to 100. Duplicate fields are not double-counted.
              </div>
              <div className="mt-3 p-3 bg-yellow-500/5 border border-yellow-500/20 rounded-lg">
                <div className="text-xs text-yellow-400 font-medium mb-1">⚠️ Important Disclaimer</div>
                <div className="text-xs text-slate-400">
                  Risk scores are preliminary investigation indicators only. They are not proof of fraud 
                  and require manual verification by qualified investigators before any action is taken.
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

