import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true, // Crucial for JWT HttpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  }
});

// Auth API endpoints
export const authApi = {
  register: (data: any) => api.post('/auth/register', data).then(r => r.data),
  login: (data: any) => api.post('/auth/login', data).then(r => r.data),
  logout: () => api.post('/auth/logout').then(r => r.data),
  me: () => api.get('/auth/me').then(r => r.data),
};

// Documents API endpoints
export const docApi = {
  upload: (files: File[], onProgress?: (pct: number) => void) => {
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const pct = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(pct);
        }
      }
    }).then(r => r.data);
  },
  history: (params: { search?: string; status?: string; page: number; limit: number }) => 
    api.get('/documents/history', { params }).then(r => r.data),
  details: (id: string) => api.get(`/documents/${id}`).then(r => r.data),
  status: (id: string) => api.get(`/documents/${id}/status`).then(r => r.data),
  delete: (id: string) => api.delete(`/documents/${id}`).then(r => r.data),
};

// Resume Intelligence & Matching endpoints
export const analysisApi = {
  getReport: (id: string) => api.get(`/analysis/${id}`).then(r => r.data),
  matchJob: (id: string, jobDescription: string) => 
    api.post(`/analysis/${id}/match`, { document_id: id, job_description: jobDescription }).then(r => r.data),
  exportReportUrl: (id: string) => `/api/v1/analysis/${id}/export`,
};

// Admin API endpoints
export const adminApi = {
  stats: () => api.get('/admin/stats').then(r => r.data),
  overrideCategory: (id: string, label: string) => 
    api.post('/admin/documents/override', { document_id: id, override_label: label }).then(r => r.data),
};

export default api;
