'use client';

import { useState, useEffect } from 'react';

export default function SuspectForm({ token, onRecordAdded }) {
  // Input fields state
  const [omang, setOmang] = useState('543216789');
  const [firstName, setFirstName] = useState('Thabo');
  const [lastName, setLastName] = useState('Molefi');
  const [gender, setGender] = useState('Male');
  const [riskTier, setRiskTier] = useState('High Risk');
  const [dob, setDob] = useState('1990-05-14');
  
  // Biometric state engine
  const [biometricToken, setBiometricToken] = useState('fpr_9d3ac7b1e6f4427aa1c8c9d7e5f3a6b2');
  const [isScanning, setIsScanning] = useState(false);
  const [scanStatus, setScanStatus] = useState('Ready');

  // Form messaging state
  const [omangFeedback, setOmangFeedback] = useState({ valid: true, message: 'Valid Omang format. 5th digit (1) matches selected gender (Male).' });
  const [submitStatus, setSubmitStatus] = useState({ type: '', text: '' });

  // Monitor and evaluate Omang format matching conditions reactively
  useEffect(() => {
    if (!omang) {
      setOmangFeedback({ valid: false, message: 'Omang number is required.' });
      return;
    }

    // Standard 9-digit validation
    if (omang.length !== 9 || !/^\d+$/.test(omang)) {
      setOmangFeedback({ valid: false, message: 'Omang must be exactly 9 numeric digits.' });
      return;
    }

    const fifthDigit = omang[4]; // Extract 5th character index

    if (gender === 'Male' && fifthDigit !== '1') {
      setOmangFeedback({ valid: false, message: 'Gender mismatch: Male citizen Omang must have 1 as the 5th digit.' });
    } else if (gender === 'Female' && fifthDigit !== '2') {
      setOmangFeedback({ valid: false, message: 'Gender mismatch: Female citizen Omang must have 2 as the 5th digit.' });
    } else {
      setOmangFeedback({ 
        valid: true, 
        message: `Valid Omang format. 5th digit (${fifthDigit}) matches selected gender (${gender}).`
      });
    }
  }, [omang, gender]);

  // Biometric Sandbox Scanner Simulator
  const triggerBiometricScan = () => {
    setIsScanning(true);
    setScanStatus('Scanning...');
    setBiometricToken('');

    setTimeout(() => {
      const mockHash = 'fpr_' + Math.random().toString(16).substring(2, 10) + Math.random().toString(16).substring(2, 10);
      setBiometricToken(mockHash);
      setIsScanning(false);
      setScanStatus('Ready');
    }, 1800);
  };

  // Submit complete crime incident model to API
  const handleRegisterProfile = async (e) => {
    e.preventDefault();
    if (!omangFeedback.valid) return;

    setSubmitStatus({ type: 'loading', text: 'Transmitting record to national registry...' });

    try {
      const response = await fetch('(https://expert-goggles-5w57qwp7ggqf657-8000.app.github.dev/crimes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          omang_number: omang,
          offense_type: "Armed Robbery", // Standardized mapping match
          case_narrative: `Suspect apprehended at industrial site following matching biometric feedback checks. Name: ${firstName} ${lastName}, DOB: ${dob}.`,
          incident_station: "Gaborone Central"
        })
      });

      if (!response.ok) throw new Error('API submission rejected.');
      
      setSubmitStatus({ type: 'success', text: 'Identity Profile permanently saved to ledger!' });
      onRecordAdded(); // Reload dashboard stats & ledger logs immediately
    } catch (err) {
      setSubmitStatus({ type: 'error', text: 'Failed to record incident entry.' });
    }
  };

  return (
    <div className="bg-[#0f192e] border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">
      <div className="flex items-center space-x-2 pb-2 border-b border-slate-800">
        <span className="text-blue-500 text-lg">👤+</span>
        <h2 className="text-sm font-bold tracking-wide uppercase text-white">Register Suspect ID & Biometrics</h2>
      </div>

      <form onSubmit={handleRegisterProfile} className="space-y-4">
        {submitStatus.text && (
          <div className={`p-3 rounded-lg text-xs font-medium border ${
            submitStatus.type === 'success' ? 'bg-emerald-950/40 border-emerald-800 text-emerald-400' :
            submitStatus.type === 'error' ? 'bg-red-950/40 border-red-800 text-red-400' : 'bg-blue-950/40 border-blue-800 text-blue-400'
          }`}>
            {submitStatus.text}
          </div>
        )}

        {/* OMANG INPUT STAGE */}
        <div>
          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Omang Number *</label>
          <div className="relative">
            <input 
              type="text" 
              maxLength={9}
              value={omang}
              onChange={(e) => setOmang(e.target.value)}
              className={`w-full bg-[#080d1a] border rounded-lg px-3 py-2.5 text-sm font-mono tracking-widest text-white focus:outline-none transition-colors ${
                omangFeedback.valid ? 'border-slate-700 focus:border-blue-500' : 'border-red-800 focus:border-red-500'
              }`}
            />
            {omangFeedback.valid && (
              <span className="absolute right-3 top-2.5 bg-emerald-950/80 border border-emerald-800 text-emerald-400 text-[10px] px-2 py-0.5 rounded font-bold">
                ✓ Valid {gender} ID
              </span>
            )}
          </div>
          <p className={`text-[11px] mt-1.5 font-medium ${omangFeedback.valid ? 'text-emerald-500' : 'text-red-400'}`}>
            {omangFeedback.message}
          </p>
        </div>

        {/* NAMES ENTRY GRID */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">First Name *</label>
            <input 
              type="text" 
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              className="w-full bg-[#080d1a] border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Last Name *</label>
            <input 
              type="text" 
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              className="w-full bg-[#080d1a] border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* SELECT CONTROL OBJECTS GRID */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Gender *</label>
            <select 
              value={gender} 
              onChange={(e) => setGender(e.target.value)}
              className="w-full bg-[#080d1a] border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            >
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Risk Tier *</label>
            <select 
              value={riskTier} 
              onChange={(e) => setRiskTier(e.target.value)}
              className="w-full bg-[#080d1a] border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            >
              <option value="High Risk">High Risk</option>
              <option value="Medium Risk">Medium Risk</option>
              <option value="Low Risk">Low Risk</option>
            </select>
          </div>
        </div>

        {/* BIRTHDATE PICKER */}
        <div>
          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Date of Birth</label>
          <input 
            type="date" 
            value={dob}
            onChange={(e) => setDob(e.target.value)}
            className="w-full bg-[#080d1a] border border-slate-700 rounded-lg px-3 py-2 text-sm font-mono text-white focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* 🧬 BIOMETRICS SCANNERS EMBED BOX */}
        <div className="border border-dashed border-slate-800 rounded-xl p-4 bg-[#080d1a]/50 space-y-3">
          <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400 flex items-center gap-1.5">
            <span>🧬</span> BIOMETRIC ENROLLMENT
          </p>
          
          <div className="flex flex-col sm:flex-row items-center gap-4 justify-between">
            <div className="flex items-center space-x-3 w-full sm:w-auto">
              <div className={`p-2.5 rounded-lg border text-xl ${isScanning ? 'bg-blue-950/50 border-blue-800 text-blue-400 animate-pulse' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>
                ✋
              </div>
              <button 
                type="button"
                onClick={triggerBiometricScan}
                disabled={isScanning}
                className="bg-blue-600 hover:bg-blue-500 text-white font-extrabold text-xs uppercase tracking-wider px-4 py-2.5 rounded-lg shadow transition-colors w-full sm:w-auto"
              >
                {isScanning ? 'Reading Ridges...' : 'SCAN THUMBPRINT'}
              </button>
            </div>

            <div className="text-right space-y-1 w-full sm:w-auto text-left sm:text-right">
              <p className="text-[11px] text-slate-400">Status: <span className={isScanning ? "text-blue-400 font-bold" : "text-emerald-400 font-bold"}>{scanStatus}</span></p>
              <p className="text-[10px] font-mono text-slate-500 truncate max-w-[200px]">Token: {biometricToken || "None linked"}</p>
            </div>
          </div>
        </div>

        {/* SUBMISSION ACTIVATION */}
        <button 
          type="submit"
          disabled={!omangFeedback.valid || submitStatus.type === 'loading'}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-extrabold text-xs uppercase tracking-widest py-3.5 rounded-lg shadow-md transition-all"
        >
          💾 REGISTER SUSPECT PROFILE
        </button>
      </form>
    </div>
  );
}