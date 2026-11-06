import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import Dashboard from './pages/Dashboard';
import NewInvestigation from './pages/NewInvestigation';
import InvestigationDetail from './pages/InvestigationDetail';
import CrossDocumentIntelligence from './pages/CrossDocumentIntelligence';
import VisualForensics from './pages/VisualForensics';
import EvidenceExplorer from './pages/EvidenceExplorer';
import Reports from './pages/Reports';
import History from './pages/History';
import Settings from './pages/Settings';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="investigation/new" element={<NewInvestigation />} />
          <Route path="investigation/:id" element={<InvestigationDetail />} />
          <Route path="cross-document" element={<CrossDocumentIntelligence />} />
          <Route path="visual-forensics" element={<VisualForensics />} />
          <Route path="evidence" element={<EvidenceExplorer />} />
          <Route path="reports" element={<Reports />} />
          <Route path="history" element={<History />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

