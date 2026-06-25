'use client';

export default function DashboardMetrics({ stats }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
      {/* CARD 1: TOTAL SUSPECTS */}
      <div className="bg-[#0f192e] border border-slate-800 rounded-xl p-5 flex items-center justify-between shadow-lg relative overflow-hidden">
        <div className="space-y-1">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Suspects</p>
          <p className="text-3xl font-extrabold text-white">{stats.total_suspects || 0}</p>
          <p className="text-[10px] text-slate-500">Total registered suspect profiles</p>
        </div>
        <div className="p-3 bg-blue-950/40 rounded-xl border border-blue-900/30 text-blue-400">
          <span className="text-2xl">👤</span>
        </div>
      </div>

      {/* CARD 2: CRIMES LOGGED */}
      <div className="bg-[#0f192e] border border-slate-800 rounded-xl p-5 flex items-center justify-between shadow-lg relative overflow-hidden">
        <div className="space-y-1">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Crimes Logged</p>
          <p className="text-3xl font-extrabold text-white">{stats.total_crimes || 0}</p>
          <p className="text-[10px] text-slate-500">Incidents recorded today</p>
        </div>
        <div className="p-3 bg-red-950/40 rounded-xl border border-red-900/30 text-red-400 animate-pulse">
          <span className="text-2xl">🚨</span>
        </div>
      </div>

      {/* CARD 3: HIGH-RISK TIERS */}
      <div className="bg-[#0f192e] border border-slate-800 rounded-xl p-5 flex items-center justify-between shadow-lg relative overflow-hidden">
        <div className="space-y-1">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">High-Risk Tiers</p>
          <p className="text-3xl font-extrabold text-amber-500">{stats.risk_breakdown?.["High Risk"] || 0}</p>
          <p className="text-[10px] text-slate-500">Active high-risk suspects</p>
        </div>
        <div className="p-3 bg-amber-950/40 rounded-xl border border-amber-900/30 text-amber-400">
          <span className="text-2xl">⚠️</span>
        </div>
      </div>
    </div>
  );
}