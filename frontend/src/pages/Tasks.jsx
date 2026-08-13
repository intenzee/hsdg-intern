import { useEffect, useState, useCallback } from 'react';
import { getTasks, getClients, updateTask, createTask, getTaskDocuments, updateDocument, createDocument } from '../api.js';

const STATUSES = ['Not Started', 'In Progress', 'Awaiting Client', 'Filed'];
const TASK_TYPES = ['GSTR-3B', 'GSTR-1', 'TDS', 'GST Quarterly', 'Income Tax Audit', 'ROC Annual Filing'];
const ASSIGNEES = ['Vikram Singh', 'Anjali Mehta', 'Rahul Verma', 'Deepika Nair', 'Arjun Desai', 'Kavya Iyer'];

const STATUS_COLORS = {
  'Not Started': 'bg-slate-100 text-slate-700',
  'In Progress': 'bg-blue-100 text-blue-700',
  'Awaiting Client': 'bg-yellow-100 text-yellow-700',
  'Filed': 'bg-green-100 text-green-700',
};

function TaskModal({ clients, onClose, onCreated }) {
  const [form, setForm] = useState({
    client_id: clients[0]?.id || '',
    task_type: 'GSTR-3B',
    period_label: 'Aug 2026',
    due_date: new Date().toISOString().split('T')[0],
    assignee: ASSIGNEES[0],
    status: 'Not Started',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const newTask = await createTask({
        ...form,
        client_id: Number(form.client_id),
      });
      onCreated(newTask);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
        <div className="flex justify-between items-center px-6 py-4 border-b">
          <h2 className="font-semibold text-slate-800">Add New Task</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 text-xl">×</button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-xs text-slate-500 mb-1">Client *</label>
            <select
              required
              className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm"
              value={form.client_id}
              onChange={(e) => setForm({ ...form, client_id: e.target.value })}
            >
              {clients.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-slate-500 mb-1">Task Type *</label>
              <select
                className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm"
                value={form.task_type}
                onChange={(e) => setForm({ ...form, task_type: e.target.value })}
              >
                {TASK_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-500 mb-1">Period Label *</label>
              <input
                type="text"
                required
                className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm"
                value={form.period_label}
                onChange={(e) => setForm({ ...form, period_label: e.target.value })}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-slate-500 mb-1">Due Date *</label>
              <input
                type="date"
                required
                className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm"
                value={form.due_date}
                onChange={(e) => setForm({ ...form, due_date: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs text-slate-500 mb-1">Assignee *</label>
              <select
                className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm"
                value={form.assignee}
                onChange={(e) => setForm({ ...form, assignee: e.target.value })}
              >
                {ASSIGNEES.map((a) => <option key={a} value={a}>{a}</option>)}
              </select>
            </div>
          </div>

          {error && <p className="text-red-600 text-sm bg-red-50 px-3 py-2 rounded">{error}</p>}

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={saving}
              className="bg-slate-800 text-white text-sm px-5 py-2 rounded hover:bg-slate-700 disabled:opacity-50 transition"
            >
              {saving ? 'Creating…' : 'Create Task'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="text-sm px-5 py-2 rounded border border-slate-300 hover:bg-slate-50 transition"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function TaskRow({ task, clients, onStatusChange, isSaving }) {
  const [expanded, setExpanded] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [newDocName, setNewDocName] = useState('');
  const [addingDoc, setAddingDoc] = useState(false);

  const loadDocs = useCallback(async () => {
    setLoadingDocs(true);
    try {
      const docs = await getTaskDocuments(task.id);
      setDocuments(docs);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingDocs(false);
    }
  }, [task.id]);

  useEffect(() => {
    if (expanded) {
      loadDocs();
    }
  }, [expanded, loadDocs]);

  const handleToggleDoc = async (docId, currentVal) => {
    try {
      const updated = await updateDocument(docId, !currentVal);
      setDocuments((prev) => prev.map((d) => (d.id === docId ? updated : d)));
    } catch (e) {
      alert(`Failed to update document: ${e.message}`);
    }
  };

  const handleAddDoc = async (e) => {
    e.preventDefault();
    if (!newDocName.trim()) return;
    setAddingDoc(true);
    try {
      const created = await createDocument(task.id, newDocName.trim());
      setDocuments((prev) => [...prev, created]);
      setNewDocName('');
    } catch (e) {
      alert(`Failed to add document: ${e.message}`);
    } finally {
      setAddingDoc(false);
    }
  };

  const badgeClass = STATUS_COLORS[task.status] || STATUS_COLORS['Not Started'];
  const receivedCount = documents.filter((d) => d.is_received).length;

  return (
    <>
      <tr className="border-t hover:bg-slate-50 transition-colors">
        <td className="py-2 px-3 text-slate-400">
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-slate-400 hover:text-slate-700 font-semibold px-1"
            title="Toggle documents checklist"
          >
            {expanded ? '▼' : '▶'} {task.id}
          </button>
        </td>
        <td className="py-2 px-3 font-medium text-slate-800">{task.client?.name ?? '—'}</td>
        <td className="py-2 px-3 text-slate-600">{task.task_type}</td>
        <td className="py-2 px-3 text-slate-600">{task.period_label}</td>
        <td className="py-2 px-3 text-slate-600">{task.due_date}</td>
        <td className="py-2 px-3 text-slate-600">{task.assignee}</td>
        <td className="py-2 px-3">
          <select
            value={task.status}
            onChange={(e) => onStatusChange(task, e.target.value)}
            disabled={isSaving}
            className={`text-xs font-semibold px-2 py-0.5 rounded-full border-0 cursor-pointer ${badgeClass} disabled:opacity-50`}
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </td>
      </tr>

      {/* Expanded Document Checklist Drawer */}
      {expanded && (
        <tr className="bg-slate-50/70 border-b">
          <td colSpan={7} className="px-6 py-3">
            <div className="bg-white rounded-lg p-4 border border-slate-200 shadow-inner">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  📄 Document Checklist ({receivedCount}/{documents.length} received)
                </h4>
                <span className="text-xs text-slate-400">Task #{task.id}</span>
              </div>

              {loadingDocs ? (
                <p className="text-xs text-slate-400 py-2">Loading documents…</p>
              ) : documents.length === 0 ? (
                <p className="text-xs text-slate-400 py-1 italic">No documents attached.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-3">
                  {documents.map((doc) => (
                    <label
                      key={doc.id}
                      className={`flex items-center gap-2 text-xs p-2 rounded border cursor-pointer transition ${
                        doc.is_received
                          ? 'bg-green-50/50 border-green-200 text-green-800'
                          : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={doc.is_received}
                        onChange={() => handleToggleDoc(doc.id, doc.is_received)}
                        className="rounded text-green-600 focus:ring-green-500"
                      />
                      <span className={doc.is_received ? 'line-through text-slate-500' : 'font-medium'}>
                        {doc.document_name}
                      </span>
                      <span className="ml-auto text-[10px] uppercase font-bold">
                        {doc.is_received ? '✓ Received' : '⏳ Pending'}
                      </span>
                    </label>
                  ))}
                </div>
              )}

              {/* Quick Add Document */}
              <form onSubmit={handleAddDoc} className="flex gap-2 items-center pt-2 border-t border-slate-100">
                <input
                  type="text"
                  placeholder="Add document item (e.g. Sales Invoice)"
                  value={newDocName}
                  onChange={(e) => setNewDocName(e.target.value)}
                  className="text-xs border border-slate-300 rounded px-2 py-1 flex-1 focus:outline-none focus:ring-1 focus:ring-slate-400"
                />
                <button
                  type="submit"
                  disabled={addingDoc || !newDocName.trim()}
                  className="bg-slate-700 text-white text-xs px-3 py-1 rounded hover:bg-slate-800 disabled:opacity-50 transition"
                >
                  {addingDoc ? 'Adding…' : '+ Add Document'}
                </button>
              </form>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // Filters
  const [filters, setFilters] = useState({
    client_id: '',
    assignee: '',
    status: '',
    task_type: '',
    date_from: '',
    date_to: '',
  });

  const loadTasks = useCallback(() => {
    setLoading(true);
    setError(null);
    getTasks(filters)
      .then(setTasks)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [filters]);

  useEffect(() => {
    getClients().then(setClients).catch(console.error);
  }, []);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleStatusChange = async (task, newStatus) => {
    setSaving(task.id);
    try {
      await updateTask(task.id, { status: newStatus });
      setTasks((prev) =>
        prev.map((t) => (t.id === task.id ? { ...t, status: newStatus } : t))
      );
    } catch (e) {
      alert(`Failed to update: ${e.message}`);
    } finally {
      setSaving(null);
    }
  };

  const handleTaskCreated = (newTask) => {
    setShowModal(false);
    loadTasks();
  };

  const clearFilters = () =>
    setFilters({ client_id: '', assignee: '', status: '', task_type: '', date_from: '', date_to: '' });

  const assignees = [...new Set(tasks.map((t) => t.assignee))].sort();

  return (
    <div>
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Tasks</h1>
          <p className="text-xs text-slate-500 mt-0.5">Click ▶ on any row to view & toggle task document checklists</p>
        </div>
        <div className="flex gap-3 items-center">
          <span className="text-sm text-slate-500">{tasks.length} task{tasks.length !== 1 ? 's' : ''}</span>
          <button
            onClick={() => setShowModal(true)}
            className="bg-slate-800 text-white text-sm px-4 py-2 rounded hover:bg-slate-700 transition"
          >
            + Add Task
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-5">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <div>
            <label className="block text-xs text-slate-500 mb-1">Client</label>
            <select
              className="w-full border border-slate-300 rounded px-2 py-1.5 text-sm"
              value={filters.client_id}
              onChange={(e) => handleFilterChange('client_id', e.target.value)}
            >
              <option value="">All clients</option>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs text-slate-500 mb-1">Status</label>
            <select
              className="w-full border border-slate-300 rounded px-2 py-1.5 text-sm"
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <option value="">All statuses</option>
              {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-xs text-slate-500 mb-1">Task Type</label>
            <select
              className="w-full border border-slate-300 rounded px-2 py-1.5 text-sm"
              value={filters.task_type}
              onChange={(e) => handleFilterChange('task_type', e.target.value)}
            >
              <option value="">All types</option>
              {TASK_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-xs text-slate-500 mb-1">Assignee</label>
            <select
              className="w-full border border-slate-300 rounded px-2 py-1.5 text-sm"
              value={filters.assignee}
              onChange={(e) => handleFilterChange('assignee', e.target.value)}
            >
              <option value="">All assignees</option>
              {assignees.map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-xs text-slate-500 mb-1">Due From</label>
            <input
              type="date"
              className="w-full border border-slate-300 rounded px-2 py-1.5 text-sm"
              value={filters.date_from}
              onChange={(e) => handleFilterChange('date_from', e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs text-slate-500 mb-1">Due To</label>
            <input
              type="date"
              className="w-full border border-slate-300 rounded px-2 py-1.5 text-sm"
              value={filters.date_to}
              onChange={(e) => handleFilterChange('date_to', e.target.value)}
            />
          </div>
        </div>
        <button
          onClick={clearFilters}
          className="mt-3 text-xs text-slate-400 hover:text-slate-600 underline"
        >
          Clear filters
        </button>
      </div>

      {/* Task table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <p className="text-slate-500 py-8 text-center">Loading…</p>
        ) : error ? (
          <p className="text-red-600 py-8 text-center">Error: {error}</p>
        ) : tasks.length === 0 ? (
          <p className="text-slate-400 py-8 text-center">No tasks match the current filters.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-50">
                <tr>
                  {['#', 'Client', 'Type', 'Period', 'Due Date', 'Assignee', 'Status'].map((h) => (
                    <th key={h} className="py-2 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tasks.map((task) => (
                  <TaskRow
                    key={task.id}
                    task={task}
                    clients={clients}
                    onStatusChange={handleStatusChange}
                    isSaving={saving === task.id}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <TaskModal
          clients={clients}
          onClose={() => setShowModal(false)}
          onCreated={handleTaskCreated}
        />
      )}
    </div>
  );
}
