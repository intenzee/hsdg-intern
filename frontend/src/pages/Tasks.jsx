import { useEffect, useState, useCallback } from 'react';
import { getTasks, getClients, updateTask } from '../api.js';

const STATUSES = ['Not Started', 'In Progress', 'Awaiting Client', 'Filed'];
const TASK_TYPES = ['GSTR-3B', 'GSTR-1', 'TDS', 'GST Quarterly', 'Income Tax Audit', 'ROC Annual Filing'];

const STATUS_COLORS = {
  'Not Started': 'bg-slate-100 text-slate-700',
  'In Progress': 'bg-blue-100 text-blue-700',
  'Awaiting Client': 'bg-yellow-100 text-yellow-700',
  'Filed': 'bg-green-100 text-green-700',
};

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(null); // task id being saved

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

  const clearFilters = () =>
    setFilters({ client_id: '', assignee: '', status: '', task_type: '', date_from: '', date_to: '' });

  // Unique assignees from task list
  const assignees = [...new Set(tasks.map((t) => t.assignee))].sort();

  return (
    <div>
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-2xl font-bold text-slate-800">Tasks</h1>
        <span className="text-sm text-slate-500">{tasks.length} task{tasks.length !== 1 ? 's' : ''}</span>
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
                {tasks.map((task) => {
                  const badgeClass = STATUS_COLORS[task.status] || STATUS_COLORS['Not Started'];
                  const isSaving = saving === task.id;
                  return (
                    <tr key={task.id} className="border-t hover:bg-slate-50">
                      <td className="py-2 px-3 text-slate-400">{task.id}</td>
                      <td className="py-2 px-3 font-medium text-slate-800">{task.client?.name ?? '—'}</td>
                      <td className="py-2 px-3 text-slate-600">{task.task_type}</td>
                      <td className="py-2 px-3 text-slate-600">{task.period_label}</td>
                      <td className="py-2 px-3 text-slate-600">{task.due_date}</td>
                      <td className="py-2 px-3 text-slate-600">{task.assignee}</td>
                      <td className="py-2 px-3">
                        <select
                          value={task.status}
                          onChange={(e) => handleStatusChange(task, e.target.value)}
                          disabled={isSaving}
                          className={`text-xs font-semibold px-2 py-0.5 rounded-full border-0 cursor-pointer ${badgeClass} disabled:opacity-50`}
                        >
                          {STATUSES.map((s) => (
                            <option key={s} value={s}>{s}</option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
