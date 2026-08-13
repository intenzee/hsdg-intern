import { useEffect, useState } from 'react';
import { getDashboard, generateTasks } from '../api.js';

const STATUS_COLORS = {
  'Not Started': 'bg-slate-100 text-slate-700',
  'In Progress': 'bg-blue-100 text-blue-700',
  'Awaiting Client': 'bg-yellow-100 text-yellow-700',
  'Filed': 'bg-green-100 text-green-700',
};

function SummaryCard({ label, count, color, note }) {
  return (
    <div className={`rounded-xl p-5 shadow-sm border ${color}`}>
      <p className="text-sm font-medium opacity-70">{label}</p>
      <p className="text-4xl font-bold mt-1">{count}</p>
      {note && <p className="text-xs mt-2 opacity-60">{note}</p>}
    </div>
  );
}

function TaskRow({ task }) {
  const badgeClass = STATUS_COLORS[task.status] || 'bg-slate-100 text-slate-700';
  return (
    <tr className="border-t hover:bg-slate-50">
      <td className="py-2 px-3 text-sm font-medium text-slate-800">{task.client?.name ?? '—'}</td>
      <td className="py-2 px-3 text-sm text-slate-600">{task.task_type}</td>
      <td className="py-2 px-3 text-sm text-slate-600">{task.period_label}</td>
      <td className="py-2 px-3 text-sm text-slate-600">{task.due_date}</td>
      <td className="py-2 px-3 text-sm">{task.assignee}</td>
      <td className="py-2 px-3">
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${badgeClass}`}>
          {task.status}
        </span>
      </td>
    </tr>
  );
}

function TaskTable({ title, tasks, emptyMsg }) {
  const [open, setOpen] = useState(true);
  if (!tasks || tasks.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
        <h3 className="font-semibold text-slate-700">{title}</h3>
        <p className="text-sm text-slate-400 mt-2">{emptyMsg}</p>
      </div>
    );
  }
  return (
    <div className="bg-white rounded-xl shadow-sm mb-4 overflow-hidden">
      <button
        className="w-full flex justify-between items-center px-5 py-3 text-left"
        onClick={() => setOpen((o) => !o)}
      >
        <h3 className="font-semibold text-slate-700">{title} <span className="text-slate-400 font-normal">({tasks.length})</span></h3>
        <span className="text-slate-400 text-sm">{open ? '▲' : '▼'}</span>
      </button>
      {open && (
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-50">
              <tr>
                {['Client', 'Type', 'Period', 'Due', 'Assignee', 'Status'].map((h) => (
                  <th key={h} className="py-2 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tasks.map((t) => <TaskRow key={t.id} task={t} />)}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Generate tasks form
  const now = new Date();
  const [genYear, setGenYear] = useState(now.getFullYear());
  const [genMonth, setGenMonth] = useState(now.getMonth() + 1);
  const [genResult, setGenResult] = useState(null);
  const [genLoading, setGenLoading] = useState(false);

  const load = () => {
    setLoading(true);
    setError(null);
    getDashboard()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleGenerate = async () => {
    setGenLoading(true);
    setGenResult(null);
    try {
      const result = await generateTasks(genYear, genMonth);
      setGenResult(result);
      load(); // refresh dashboard
    } catch (e) {
      setGenResult({ error: e.message });
    } finally {
      setGenLoading(false);
    }
  };

  if (loading) return <p className="text-slate-500 py-8 text-center">Loading dashboard…</p>;
  if (error) return <p className="text-red-600 py-8 text-center">Error: {error}</p>;

  const { summary, due_this_week, overdue, awaiting_client, workload_per_assignee } = data;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
        <button onClick={load} className="text-sm text-slate-500 hover:text-slate-800 transition">↻ Refresh</button>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <SummaryCard
          label="Due This Week"
          count={summary.due_this_week_count}
          color="border-orange-200 bg-orange-50 text-orange-800"
          note="Not yet filed"
        />
        <SummaryCard
          label="Overdue"
          count={summary.overdue_count}
          color="border-red-200 bg-red-50 text-red-800"
          note="Past due, not filed"
        />
        <SummaryCard
          label="Awaiting Client"
          count={summary.awaiting_client_count}
          color="border-yellow-200 bg-yellow-50 text-yellow-800"
          note="Blocked on client"
        />
        <SummaryCard
          label="Total Open"
          count={summary.total_open_tasks}
          color="border-slate-200 bg-white text-slate-800"
          note="Non-filed tasks"
        />
      </div>

      {/* Workload table */}
      <div className="bg-white rounded-xl shadow-sm p-5 mb-8">
        <h2 className="font-semibold text-slate-700 mb-3">Workload per Assignee</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50">
              <tr>
                {['Assignee', 'Not Started', 'In Progress', 'Awaiting Client', 'Filed', 'Total'].map((h) => (
                  <th key={h} className="py-2 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {workload_per_assignee.map((row) => (
                <tr key={row.assignee} className="border-t hover:bg-slate-50">
                  <td className="py-2 px-3 font-medium text-slate-800">{row.assignee}</td>
                  <td className="py-2 px-3 text-slate-600">{row.not_started}</td>
                  <td className="py-2 px-3 text-blue-600 font-medium">{row.in_progress}</td>
                  <td className="py-2 px-3 text-yellow-600 font-medium">{row.awaiting_client}</td>
                  <td className="py-2 px-3 text-green-600">{row.filed}</td>
                  <td className="py-2 px-3 font-bold text-slate-700">{row.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Task lists */}
      <TaskTable title="⚠️ Overdue Tasks" tasks={overdue} emptyMsg="No overdue tasks." />
      <TaskTable title="📅 Due This Week" tasks={due_this_week} emptyMsg="Nothing due in the next 7 days." />
      <TaskTable title="⏳ Awaiting Client" tasks={awaiting_client} emptyMsg="No tasks waiting on clients." />

      {/* Generate tasks panel */}
      <div className="bg-white rounded-xl shadow-sm p-5 mt-6">
        <h2 className="font-semibold text-slate-700 mb-3">Generate Recurring Tasks</h2>
        <div className="flex flex-wrap gap-3 items-end">
          <div>
            <label className="block text-xs text-slate-500 mb-1">Year</label>
            <input
              type="number"
              value={genYear}
              onChange={(e) => setGenYear(e.target.value)}
              className="border border-slate-300 rounded px-3 py-1.5 text-sm w-24"
              min="2020" max="2100"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Month</label>
            <select
              value={genMonth}
              onChange={(e) => setGenMonth(e.target.value)}
              className="border border-slate-300 rounded px-3 py-1.5 text-sm"
            >
              {['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].map((m, i) => (
                <option key={i} value={i + 1}>{m}</option>
              ))}
            </select>
          </div>
          <button
            onClick={handleGenerate}
            disabled={genLoading}
            className="bg-slate-800 text-white text-sm px-4 py-1.5 rounded hover:bg-slate-700 disabled:opacity-50 transition"
          >
            {genLoading ? 'Generating…' : 'Generate'}
          </button>
        </div>
        {genResult && !genResult.error && (
          <p className="mt-3 text-sm text-green-700 bg-green-50 rounded px-3 py-2">
            ✅ {genResult.period}: {genResult.tasks_created} created, {genResult.tasks_skipped} skipped, {genResult.documents_created} documents.
          </p>
        )}
        {genResult?.error && (
          <p className="mt-3 text-sm text-red-700 bg-red-50 rounded px-3 py-2">❌ {genResult.error}</p>
        )}
      </div>
    </div>
  );
}
