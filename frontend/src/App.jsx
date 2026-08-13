import { useState } from 'react';
import Navbar from './components/Navbar.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Tasks from './pages/Tasks.jsx';
import Clients from './pages/Clients.jsx';

const PAGES = ['Dashboard', 'Tasks', 'Clients'];

export default function App() {
  const [page, setPage] = useState('Dashboard');

  return (
    <div className="min-h-screen bg-slate-100">
      <Navbar current={page} onNavigate={setPage} pages={PAGES} />
      <main className="max-w-7xl mx-auto px-4 py-6">
        {page === 'Dashboard' && <Dashboard />}
        {page === 'Tasks' && <Tasks />}
        {page === 'Clients' && <Clients />}
      </main>
    </div>
  );
}
