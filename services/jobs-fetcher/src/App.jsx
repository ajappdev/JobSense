import { Routes, Route, Link } from 'react-router-dom';
import Auth from './pages/Auth';
import Settings from './pages/Settings';
import Jobs from './pages/Jobs';
import JobDetail from './pages/JobDetail';
import { Home } from 'lucide-react';

function App() {
  return (
    <>
      <nav className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-6">
          <Link to="/" className="flex items-center gap-2 font-bold text-xl text-white">
            <Home className="w-6 h-6" />
            JobSense
          </Link>
          <Link to="/settings" className="text-slate-300 hover:text-white transition-colors">Settings</Link>
          <Link to="/jobs" className="text-slate-300 hover:text-white transition-colors">Jobs</Link>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Auth />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/jobs/:id" element={<JobDetail />} />
      </Routes>
    </>
  );
}

export default App;