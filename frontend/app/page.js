'use client';

import { useState, useEffect } from 'react';
import CrimeLedger from './components/CrimeLedeger';
import DashboardMetrics from './components/DashboardMetrics';
import SuspectForm from './components/SuspectForm';

export default function AppEngine() {
  // Authentication & View States
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('BPS-4102');
  const [password, setPassword] = useState('securepass123');
  const [token, setToken] = useState('');
  const [authError, setAuthError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Operational Dashboard States
  const [stats, setStats] = useState({ total_suspects: 0, total_crimes: 0, risk_breakdown: { "High Risk": 0 } });
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Handle Login Authentication against your FastAPI backend
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setAuthError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch('http://127.0.0.1:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Invalid credentials or server configuration mismatch.');
      }

      const data = await response.json();
      setToken(data.access_token);
      setIsLoggedIn(true);
    } catch (err) {
      setAuthError(err.message || 'Failed to connect to authentication server.');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch metrics dynamically once logged in
  useEffect(() => {
    if (!isLoggedIn || !token) return;

    fetch('http://127.0.0.1:8000/dashboard/stats', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => {
      if (data.metrics) setStats(data.metrics);
    })
    .catch(err => console.error("Error pulling metrics:", err));
  }, [refreshTrigger, isLoggedIn, token]);

  // ==========================================
  // VIEW 1: HIGH-TECH POLICE LANDING / LOGIN PAGE
  // ==========================================
  if (!isLoggedIn) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#070b14] px-4">
        <div className="w-full max-w-md bg-[#0f192e] border border-slate-800 rounded-xl p-8 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-600 via-sky-500 to-blue-800"></div>
          
          <div className="text-center mb-8">
            <div className="inline-block bg-blue-600 text-white px-3 py-1.5 rounded-md font-bold text-xs tracking-widest uppercase mb-3 shadow-md">
              BPS CODESPACE NODE
            </div>
            <h1 className="text-xl font-extrabold tracking-wide text-white uppercase">Republika ya Botswana</h1>
            <p className="text-xs text-slate-400 mt-1 uppercase font-semibold tracking-wider text-blue-400">
              National Suspect Identity Registry
            </p>
          </div>

          <form onSubmit={handleLoginSubmit} className="space-y-5">
            {authError && (
              <div className="p-3 bg-red-950/50 border border-red-800 rounded-lg text-xs text-red-400 font-medium">
                ⚠️ {authError}
              </div>
            )}

            <div>
              <label className="block text-xs font-bold tracking-wider text-slate-400 uppercase mb-2">Officer Username</label>
              <input 
                type="text" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-[#16223f] border border-slate-700 rounded-lg px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                placeholder="e.g. BPS-4102"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-bold tracking-wider text-slate-400 uppercase mb-2">Security Passphrase</label>
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#16223f] border border-slate-700 rounded-lg px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                placeholder="••••••••••••"
                required
              />
            </div>

            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white font-bold text-sm uppercase tracking-wider py-3.5 rounded-lg shadow-lg shadow-blue-900/20 active:translate-y-px transition-all"
            >
              {isLoading ? 'Decrypting Security Token...' : 'Secure Node Authorization 🔐'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <span className="text-[10px] text-slate-600 font-mono uppercase tracking-widest">
              SECURE LOG: ACCESS STRICTLY FOR AUTHORIZED PERSONNEL ONLY
            </span>
          </div>
        </div>
      </div>
    );
  }

  // ==========================================
  // VIEW 2: AUTHENTICATED OPERATIONAL DASHBOARD
  // ==========================================
  return (
    <div className="flex flex-col min-h-screen bg-[#070b14]">
      {/* 🛡️ TOP MASTER HEADER */}
      <header className="border-b border-slate-800 bg-[#0f192e] px-6 py-4 flex items-center justify-between shadow-md">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-600 text-white p-2 rounded-md font-bold text-sm tracking-wider shadow">BPS</div>
          <div>
            <h1 className="text-md font-bold tracking-wide uppercase text-white">Republika ya Botswana</h1>
            <p className="text-xs text-blue-400 font-medium tracking-tight">NATIONAL SUSPECT IDENTITY REGISTRY</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs bg-[#172545] border border-slate-700 px-3 py-2 rounded-lg">
            <span className="text-slate-400">Officer:</span>
            <span className="text-blue-400 font-bold tracking-wider">{username} 👤</span>
          </div>
          <button 
            onClick={() => { setIsLoggedIn(false); setToken(''); }}
            className="text-xs text-slate-400 hover:text-red-400 font-medium bg-slate-800/40 hover:bg-red-950/30 px-3 py-2 rounded-lg border border-slate-700/60 transition-colors"
          >
            Logout
          </button>
        </div>
      </header>

      {/* MAIN OPERATIONAL WORKSPACE CONTAINER */}
      <main className="flex-1 p-6 space-y-6 max-w-7xl mx-auto w-full">
        
        {/* 📈 METRICS INTERFACE CARD GRID */}
        <DashboardMetrics stats={stats} />

        {/* TWO-PANE WORKSPACE INTERFACE */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* LEFT COLUMN: REGISTRATION INPUT & VALIDATION FORM */}
          <div className="lg:col-span-7">
            <SuspectForm token={token} onRecordAdded={() => setRefreshTrigger(prev => prev + 1)} />
          </div>

          {/* RIGHT COLUMN: INTER-STATION REALTIME INCIDENT LEDGER */}
          <div className="lg:col-span-5">
            <CrimeLedger token={token} refreshTrigger={refreshTrigger} />
          </div>
        </div>
      </main>

      {/* SYSTEM STATUS FOOTER BANNER */}
      <footer className="border-t border-slate-800 bg-[#0f192e] px-6 py-3 flex items-center justify-between text-xs text-slate-500 mt-auto">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-emerald-400 font-medium">All national database clusters synchronized</span>
        </div>
        <div>© 2026 Botswana Police Service Registry</div>
      </footer>
    </div>
  );
}