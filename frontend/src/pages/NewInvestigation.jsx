import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, FileText, Image, X, AlertCircle, CheckCircle, 
  ArrowRight, Loader2, FileSearch
} from 'lucide-react';
import { clsx } from 'clsx';
import { createInvestigation } from '../services/api';

const FILE_ACCEPT = {
  'application/pdf': ['.pdf'],
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
};

const MAX_SIZE = 50 * 1024 * 1024; // 50MB

function FilePreviewCard({ file, onRemove }) {
  const isPDF = file.type === 'application/pdf';
  const sizeMB = (file.size / 1024 / 1024).toFixed(2);

  return (
    <div className="glass-card p-3 flex items-center gap-3 group">
      <div className={clsx('p-2 rounded-lg flex-shrink-0', isPDF ? 'bg-red-500/15' : 'bg-blue-500/15')}>
        {isPDF 
          ? <FileText className="w-5 h-5 text-red-400" /> 
          : <Image className="w-5 h-5 text-blue-400" />
        }
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-white truncate">{file.name}</div>
        <div className="text-xs text-slate-500">{sizeMB} MB · {file.type.split('/')[1].toUpperCase()}</div>
      </div>
      <button
        onClick={() => onRemove(file)}
        className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-red-500/20"
      >
        <X className="w-4 h-4 text-red-400" />
      </button>
    </div>
  );
}

function ProcessingStep({ step, status }) {
  const icons = {
    pending: <div className="w-4 h-4 rounded-full border-2 border-slate-600" />,
    active: <Loader2 className="w-4 h-4 text-cyan-primary animate-spin" />,
    done: <CheckCircle className="w-4 h-4 text-green-400" />,
    error: <AlertCircle className="w-4 h-4 text-red-400" />,
  };

  return (
    <div className={clsx('flex items-center gap-3 text-sm', {
      'text-slate-500': status === 'pending',
      'text-cyan-primary': status === 'active',
      'text-green-400': status === 'done',
      'text-red-400': status === 'error',
    })}>
      {icons[status]}
      {step}
    </div>
  );
}

const PROCESSING_STEPS = [
  'Document Upload',
  'Document Classification',
  'OCR & Information Extraction',
  'Visual Forensic Analysis',
  'Cross-Document Correlation',
  'Anomaly Investigation',
  'Risk Assessment',
  'Investigation Complete',
];

export default function NewInvestigation() {
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [processing, setProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [error, setError] = useState(null);

  const onDrop = useCallback((accepted, rejected) => {
    if (rejected.length > 0) {
      setError(`Some files were rejected. Only PDF, PNG, JPG (max 50MB) are supported.`);
    }
    setFiles(prev => {
      const existing = new Set(prev.map(f => f.name));
      const newFiles = accepted.filter(f => !existing.has(f.name));
      return [...prev, ...newFiles];
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: FILE_ACCEPT,
    maxSize: MAX_SIZE,
    multiple: true,
  });

  const removeFile = (file) => {
    setFiles(prev => prev.filter(f => f !== file));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) { setError('Please enter an investigation title'); return; }
    if (files.length === 0) { setError('Please upload at least one document'); return; }

    setError(null);
    setProcessing(true);
    setCurrentStep(0);

    // Simulate step progression while actual processing occurs
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev >= PROCESSING_STEPS.length - 2) {
          clearInterval(stepInterval);
          return prev;
        }
        return prev + 1;
      });
    }, 1200);

    try {
      const result = await createInvestigation(title, description, files);
      clearInterval(stepInterval);
      setCurrentStep(PROCESSING_STEPS.length - 1);
      
      setTimeout(() => {
        navigate(`/investigation/${result.investigation_id}`);
      }, 800);
    } catch (err) {
      clearInterval(stepInterval);
      setError(err.message);
      setProcessing(false);
      setCurrentStep(-1);
    }
  };

  const getStepStatus = (index) => {
    if (currentStep < 0) return 'pending';
    if (index < currentStep) return 'done';
    if (index === currentStep) return 'active';
    return 'pending';
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="page-title">New Investigation</h1>
        <p className="page-subtitle">Upload documents to start a forensic cross-document analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Form */}
        <div className="lg:col-span-2 space-y-5">
          {/* Investigation Details */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wider">
              Investigation Details
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1.5">Investigation Title *</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g., Loan Application – Rahul Sharma"
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                  disabled={processing}
                />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1.5">Description (optional)</label>
                <textarea
                  className="input-field resize-none"
                  rows={3}
                  placeholder="Brief description of this investigation..."
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  disabled={processing}
                />
              </div>
            </div>
          </div>

          {/* Dropzone */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wider">
              Document Upload
            </h3>
            
            <div
              {...getRootProps()}
              className={clsx(
                'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300',
                isDragActive 
                  ? 'border-cyan-primary bg-cyan-primary/10' 
                  : 'border-white/15 hover:border-cyan-primary/40 hover:bg-white/3',
                processing && 'pointer-events-none opacity-50'
              )}
            >
              <input {...getInputProps()} />
              <Upload className={clsx('w-10 h-10 mx-auto mb-3', isDragActive ? 'text-cyan-primary' : 'text-slate-500')} />
              {isDragActive ? (
                <p className="text-cyan-primary font-medium">Drop documents here</p>
              ) : (
                <>
                  <p className="text-white font-medium mb-1">Drag & drop documents here</p>
                  <p className="text-slate-500 text-sm">or click to browse files</p>
                  <div className="flex items-center justify-center gap-3 mt-3">
                    {['PDF', 'PNG', 'JPG', 'JPEG'].map(ext => (
                      <span key={ext} className="text-xs text-slate-500 border border-white/10 px-2 py-0.5 rounded">
                        {ext}
                      </span>
                    ))}
                  </div>
                  <p className="text-xs text-slate-600 mt-2">Maximum 50MB per file</p>
                </>
              )}
            </div>

            {/* File List */}
            {files.length > 0 && (
              <div className="mt-4 space-y-2">
                <div className="text-xs text-slate-400 font-medium uppercase tracking-wider mb-2">
                  {files.length} Document{files.length > 1 ? 's' : ''} Selected
                </div>
                {files.map((file, i) => (
                  <FilePreviewCard key={i} file={file} onRemove={removeFile} />
                ))}
              </div>
            )}
          </div>

          {/* Error */}
          {error && (
            <div className="glass-card p-4 border-red-500/30 bg-red-500/5">
              <div className="flex items-center gap-2 text-red-400 text-sm">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {error}
              </div>
            </div>
          )}

          {/* Submit */}
          <button
            onClick={handleSubmit}
            disabled={processing || files.length === 0 || !title.trim()}
            className={clsx(
              'w-full py-3 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all duration-300',
              processing || files.length === 0 || !title.trim()
                ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                : 'btn-primary justify-center'
            )}
          >
            {processing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Processing Investigation...
              </>
            ) : (
              <>
                <FileSearch className="w-4 h-4" />
                Start Investigation
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

        {/* Processing Panel */}
        <div className="space-y-4">
          {/* Processing Steps */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wider">
              Processing Pipeline
            </h3>
            <div className="space-y-3">
              {PROCESSING_STEPS.map((step, i) => (
                <ProcessingStep key={step} step={step} status={getStepStatus(i)} />
              ))}
            </div>
          </div>

          {/* Information Panel */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wider">
              Supported Documents
            </h3>
            <div className="space-y-2 text-xs text-slate-400">
              {[
                'Identity Documents (Aadhaar, Passport)',
                'PAN Card / Tax Documents',
                'Bank Statements',
                'Salary Slips',
                'Application Forms',
                'Declarations & Affidavits',
                'Supporting Documents',
              ].map(doc => (
                <div key={doc} className="flex items-center gap-2">
                  <div className="w-1 h-1 rounded-full bg-cyan-primary" />
                  {doc}
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card p-4 border-cyan-primary/20 bg-cyan-primary/5">
            <div className="text-xs text-cyan-primary font-medium mb-1">💡 Pro Tip</div>
            <div className="text-xs text-slate-400">
              Upload multiple documents from the same applicant to enable Cross-Document Intelligence analysis — 
              the core innovation of PaperTrail.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

