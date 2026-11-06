import React from 'react';
import { CheckCircle2, AlertTriangle, MinusCircle, HelpCircle } from 'lucide-react';
import { clsx } from 'clsx';

export default function ComparisonTable({ rows, documents }) {
  if (!rows || rows.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500 text-sm">
        No comparison data available
      </div>
    );
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'match':
        return (
          <span className="flex items-center gap-1 badge-match">
            <CheckCircle2 className="w-3 h-3 text-green-400" /> Match
          </span>
        );
      case 'conflict':
        return (
          <span className="flex items-center gap-1 badge-conflict">
            <AlertTriangle className="w-3 h-3 text-red-400" /> Conflict
          </span>
        );
      case 'missing':
        return (
          <span className="flex items-center gap-1 badge-missing">
            <MinusCircle className="w-3 h-3 text-yellow-400" /> Missing
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-xs text-slate-400">
            <HelpCircle className="w-3 h-3 text-slate-500" /> Single
          </span>
        );
    }
  };

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th className="w-48">Field</th>
            {documents.map((doc, i) => (
              <th key={doc.document_id}>
                <div className="font-semibold text-slate-300">
                  {doc.filename.length > 20 ? doc.filename.slice(0, 20) + '…' : doc.filename}
                </div>
                <div className="text-xs text-slate-500 font-normal">
                  {doc.document_type?.replace(/_/g, ' ') || `Doc ${i + 1}`}
                </div>
              </th>
            ))}
            <th className="w-28 text-center">Status</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr 
              key={row.field_key}
              className={clsx({
                'bg-red-500/5': row.status === 'conflict',
                'bg-green-500/5': row.status === 'match',
              })}
            >
              <td className="font-medium text-white text-xs">{row.field}</td>
              {documents.map((doc) => {
                const val = row.values?.[doc.document_id];
                const isConflict = row.status === 'conflict';
                
                return (
                  <td key={doc.document_id} className="text-xs">
                    {val ? (
                      <span className={clsx(
                        'px-2 py-0.5 rounded text-xs inline-block max-w-xs truncate',
                        isConflict 
                          ? 'bg-red-500/10 text-red-300 border border-red-500/20 font-medium' 
                          : 'text-slate-300'
                      )}>
                        {val}
                      </span>
                    ) : (
                      <span className="text-slate-600 italic">—</span>
                    )}
                  </td>
                );
              })}
              <td className="text-center">{getStatusBadge(row.status)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

