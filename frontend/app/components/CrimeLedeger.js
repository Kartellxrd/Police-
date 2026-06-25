'use client';

import { useState, useEffect } from 'react';

export default function CrimeLedger({ token, refreshTrigger }) {
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    if (!token) return;

    fetch('http://127.0.0.1:8000/dashboard/stats', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => {
      if (data.recent_activity) setActivities(data.recent_activity);
    })
    .catch(err => console.error("Error updating ledger feed:", err));
  }, [refreshTrigger, token]);

  return (
    <div className="bg-[#0f192e] border border-slate-800 rounded-xl shadow-xl flex flex-col h-[585px]">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-[#121e36]/40">
        <div className="flex items-center space-x-2">
          <span className="text-slate-400">📋</span>
          <h2 className="text-sm font-bold tracking-wide uppercase text-white">Live Criminal Ledger Feed</h2>
        </div>
        <button className="text-[10px] bg-[#162544] hover:bg-[#1d315c] text-slate-300 font-bold px-2.5 py-1 rounded border border-slate-700 uppercase tracking-wider">
          Filter ▽
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
        {activities.length === 0 ? (
          <p className="text-xs text-slate-500 text-center py-8">No records available in the network mesh.</p>
        ) : (
          activities.map((activity) => (
            <div key={activity.case_uuid} className="bg-[#080d1a] border border-slate-800 hover:border-slate-700/80 rounded-lg p-4 transition-colors relative">
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center space-x-2">
                  <span className="bg-red-950/60 text-red-400 text-[10px] font-black px-1.5 py-0.5 rounded border border-red-900/40">AR</span>
                  <h3 className="text-xs font-black tracking-wide text-red-400 uppercase">{activity.offense_type}</h3>
                </div>
                <span className="text-[10px] font-mono text-slate-500">
                  {new Date(activity.timestamp_logged).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} CAT
                </span>
              </div>

              <div className="space-y-1 text-xs text-slate-300 font-medium">
                <p className="text-[11px] text-slate-500 font-mono truncate">
                  Case ID: <span className="text-blue-400">{activity.case_uuid}</span>
                </p>
                <p><span className="text-slate-500">🏢 Station:</span> {activity.incident_station || "Gaborone Central Police Station"}</p>
                <p><span className="text-slate-500">👤 Suspect Omang:</span> {activity.omang_number}</p>
                <div className="pt-2 flex gap-2 items-center">
                  <span className="bg-slate-900 px-2 py-0.5 rounded text-[10px] border border-slate-800 text-slate-400">Officer: {activity.logged_by}</span>
                  <span className="bg-red-950/40 px-2 py-0.5 rounded text-[10px] border border-red-900/30 text-red-400 font-bold">High Risk</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
      
      <div className="p-3 border-t border-slate-800 text-center bg-[#121e36]/10">
        <button className="text-[11px] font-bold text-blue-400 hover:text-blue-300 tracking-wide uppercase transition-colors">
          View all incidents →
        </button>
      </div>
    </div>
  );
}