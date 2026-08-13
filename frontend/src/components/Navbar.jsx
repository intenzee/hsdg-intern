export default function Navbar({ current, onNavigate, pages }) {
  return (
    <nav className="bg-slate-800 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 flex items-center gap-6 h-14">
        <span className="font-bold text-lg tracking-tight text-white mr-4">
          📋 CA Firm MIS
        </span>
        {pages.map((p) => (
          <button
            key={p}
            onClick={() => onNavigate(p)}
            className={`text-sm font-medium px-3 py-1 rounded transition-colors ${
              current === p
                ? 'bg-slate-600 text-white'
                : 'text-slate-300 hover:text-white hover:bg-slate-700'
            }`}
          >
            {p}
          </button>
        ))}
      </div>
    </nav>
  );
}
