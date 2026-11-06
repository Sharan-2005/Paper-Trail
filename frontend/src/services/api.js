import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

// ─── Health ────────────────────────────────────────────────────────
export const checkHealth = () => api.get('/health').then(r => r.data);

// ─── Investigations ────────────────────────────────────────────────
export const getStats = () => api.get('/investigations/stats').then(r => r.data);
export const listInvestigations = (skip = 0, limit = 50) =>
  api.get('/investigations/', { params: { skip, limit } }).then(r => r.data);
export const getInvestigation = (id) =>
  api.get(`/investigations/${id}`).then(r => r.data);
export const deleteInvestigation = (id) =>
  api.delete(`/investigations/${id}`).then(r => r.data);

export const createInvestigation = async (title, description, files) => {
  const formData = new FormData();
  formData.append('title', title);
  formData.append('description', description || '');
  files.forEach((file) => formData.append('files', file));
  
  const response = await api.post('/investigations/create', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

// ─── Documents ─────────────────────────────────────────────────────
export const getDocument = (id) =>
  api.get(`/documents/${id}`).then(r => r.data);
export const updateDocumentFields = (id, fields) =>
  api.patch(`/documents/${id}/fields`, fields).then(r => r.data);

// ─── Forensics ─────────────────────────────────────────────────────
export const getForensicResults = (docId) =>
  api.get(`/forensics/${docId}`).then(r => r.data);
export const runForensics = (docId) =>
  api.post(`/forensics/${docId}/analyze`).then(r => r.data);

// ─── Reports ───────────────────────────────────────────────────────
export const generateReport = (investigationId) =>
  api.post(`/reports/${investigationId}/generate`).then(r => r.data);
export const getDownloadUrl = (investigationId, filename) =>
  `${API_BASE}/reports/${investigationId}/download/${filename}`;

// ─── Demo ──────────────────────────────────────────────────────────
export const launchDemo = () => api.post('/demo/launch').then(r => r.data);
export const getDemo = () => api.get('/demo/').then(r => r.data);

// ─── Settings ──────────────────────────────────────────────────────
export const getSettings = () => api.get('/settings/').then(r => r.data);

export default api;

