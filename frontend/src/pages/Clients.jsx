import { useEffect, useState } from 'react';
import { getClients, createClient, updateClient, deleteClient } from '../api.js';

const ENTITY_TYPES = ['Individual', 'Company', 'LLP', 'Partnership', 'Trust'];
const PARTNERS = ['Rajesh Kumar', 'Priya Sharma', 'Amit Patel', 'Sneha Reddy'];

const EMPTY_FORM = {
  name: '',
  entity_type: 'Company',
  pan: '',
  gstin: '',
  contact_name: '',
  contact_email: '',
  contact_phone: '',
  partner_in_charge: 'Rajesh Kumar',
};

function ClientModal({ client, onClose, onSave }) {
  const [form, setForm] = useState(client ? { ...client } : { ...EMPTY_FORM });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handle = (k) => (e) => setForm((prev) => ({ ...prev, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      // Clean up empty optional strings to null
      const payload = { ...form };
      ['pan', 'gstin', 'contact_name', 'contact_email', 'contact_phone'].forEach((k) => {
        if (!payload[k]) payload[k] = null;
      });
      const saved = client
        ? await updateClient(client.id, payload)
        : await createClient(payload);
      onSave(saved);
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center px-6 py-4 border-b">
          <h2 className="font-semibold text-slate-800">{client ? 'Edit Client' : 'Add Client'}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 text-xl">×</button>
        </div>
        <form onSubmit={submit} className="p-6 space-y-4">
          <Field label="Name *" value={form.name} onChange={handle('name')} required />
          <div className="grid grid-cols-2 gap-4">
            <SelectField label="Entity Type *" value={form.entity_type} onChange={handle('entity_type')} options={ENTITY_TYPES} />
            <SelectField label="Partner in Charge *" value={form.partner_in_charge} onChange={handle('partner_in_charge')} options={PARTNERS} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Field label="PAN" value={form.pan || ''} onChange={handle('pan')} maxLength={10} />
            <Field label="GSTIN" value={form.gstin || ''} onChange={handle('gstin')} maxLength={15} />
          </div>
          <Field label="Contact Name" value={form.contact_name || ''} onChange={handle('contact_name')} />
          <div className="grid grid-cols-2 gap-4">
            <Field label="Contact Email" value={form.contact_email || ''} onChange={handle('contact_email')} type="email" />
            <Field label="Contact Phone" value={form.contact_phone || ''} onChange={handle('contact_phone')} />
          </div>
          {error && <p className="text-red-600 text-sm bg-red-50 px-3 py-2 rounded">{error}</p>}
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={saving}
              className="bg-slate-800 text-white text-sm px-5 py-2 rounded hover:bg-slate-700 disabled:opacity-50 transition"
            >
              {saving ? 'Saving…' : 'Save'}
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

function Field({ label, ...props }) {
  return (
    <div>
      <label className="block text-xs text-slate-500 mb-1">{label}</label>
      <input
        {...props}
        className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
      />
    </div>
  );
}

function SelectField({ label, value, onChange, options }) {
  return (
    <div>
      <label className="block text-xs text-slate-500 mb-1">{label}</label>
      <select
        value={value}
        onChange={onChange}
        className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
      >
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

export default function Clients() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modal, setModal] = useState(null); // null | 'add' | client object

  const load = () => {
    setLoading(true);
    setError(null);
    getClients()
      .then(setClients)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleSave = (saved) => {
    setClients((prev) => {
      const idx = prev.findIndex((c) => c.id === saved.id);
      if (idx >= 0) {
        const updated = [...prev];
        updated[idx] = saved;
        return updated;
      }
      return [saved, ...prev];
    });
    setModal(null);
  };

  const handleDelete = async (client) => {
    if (!confirm(`Delete "${client.name}"? All their tasks will also be deleted.`)) return;
    try {
      await deleteClient(client.id);
      setClients((prev) => prev.filter((c) => c.id !== client.id));
    } catch (e) {
      alert(`Delete failed: ${e.message}`);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-2xl font-bold text-slate-800">Clients</h1>
        <button
          onClick={() => setModal('add')}
          className="bg-slate-800 text-white text-sm px-4 py-2 rounded hover:bg-slate-700 transition"
        >
          + Add Client
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <p className="text-slate-500 py-8 text-center">Loading…</p>
        ) : error ? (
          <p className="text-red-600 py-8 text-center">Error: {error}</p>
        ) : clients.length === 0 ? (
          <p className="text-slate-400 py-8 text-center">No clients. Add one above.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-50">
                <tr>
                  {['#', 'Name', 'Type', 'PAN', 'Partner', 'Contact', 'Actions'].map((h) => (
                    <th key={h} className="py-2 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {clients.map((c) => (
                  <tr key={c.id} className="border-t hover:bg-slate-50">
                    <td className="py-2 px-3 text-slate-400">{c.id}</td>
                    <td className="py-2 px-3 font-medium text-slate-800">{c.name}</td>
                    <td className="py-2 px-3">
                      <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">{c.entity_type}</span>
                    </td>
                    <td className="py-2 px-3 text-slate-500 font-mono text-xs">{c.pan ?? '—'}</td>
                    <td className="py-2 px-3 text-slate-600">{c.partner_in_charge}</td>
                    <td className="py-2 px-3 text-slate-500">{c.contact_email ?? c.contact_phone ?? '—'}</td>
                    <td className="py-2 px-3 flex gap-2">
                      <button
                        onClick={() => setModal(c)}
                        className="text-xs text-blue-600 hover:underline"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(c)}
                        className="text-xs text-red-500 hover:underline"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {modal && (
        <ClientModal
          client={modal === 'add' ? null : modal}
          onClose={() => setModal(null)}
          onSave={handleSave}
        />
      )}
    </div>
  );
}
