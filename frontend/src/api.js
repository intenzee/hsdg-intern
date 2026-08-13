/**
 * Centralized API helper.
 * All requests go through here so we only need to change VITE_API_URL in one place.
 */
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const getDashboard = () => request('/tasks/dashboard');

// ── Tasks ─────────────────────────────────────────────────────────────────────
export const getTasks = (params = {}) => {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') qs.append(k, v);
  });
  const query = qs.toString() ? `?${qs.toString()}` : '';
  return request(`/tasks${query}`);
};

export const createTask = (data) =>
  request('/tasks', { method: 'POST', body: JSON.stringify(data) });

export const updateTask = (id, data) =>
  request(`/tasks/${id}`, { method: 'PUT', body: JSON.stringify(data) });

// ── Documents ─────────────────────────────────────────────────────────────────
export const getTaskDocuments = (taskId) =>
  request(`/tasks/${taskId}/documents`);

export const updateDocument = (docId, isReceived) =>
  request(`/documents/${docId}`, {
    method: 'PATCH',
    body: JSON.stringify({ is_received: isReceived }),
  });

export const createDocument = (taskId, documentName) =>
  request(`/tasks/${taskId}/documents`, {
    method: 'POST',
    body: JSON.stringify({ document_name: documentName, is_received: false }),
  });

// ── Clients ───────────────────────────────────────────────────────────────────
export const getClients = () => request('/clients?limit=200');

export const createClient = (data) =>
  request('/clients', { method: 'POST', body: JSON.stringify(data) });

export const updateClient = (id, data) =>
  request(`/clients/${id}`, { method: 'PUT', body: JSON.stringify(data) });

export const deleteClient = (id) =>
  request(`/clients/${id}`, { method: 'DELETE' });

// ── Task Generation ───────────────────────────────────────────────────────────
export const generateTasks = (year, month) =>
  request('/tasks/generate', {
    method: 'POST',
    body: JSON.stringify({ year: Number(year), month: Number(month) }),
  });
