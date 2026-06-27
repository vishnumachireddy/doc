import React, { useState, useEffect } from 'react';
import { adminApi } from '../services/api';
import { 
  ShieldCheck, Users, UploadCloud, Target, Cpu, RefreshCw, 
  Settings, AlertCircle, CheckCircle2, BarChart3
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function AdminPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Override state
  const [overrideDocId, setOverrideDocId] = useState('');
  const [overrideLabel, setOverrideLabel] = useState('Resume');
  const [overrideLoading, setOverrideLoading] = useState(false);
  const [overrideMessage, setOverrideMessage] = useState('');
  const [overrideError, setOverrideError] = useState('');

  const fetchStats = async () => {
    setLoading(true);
    try {
      const res = await adminApi.stats();
      setStats(res);
    } catch (err) {
      setError('Failed to fetch administrative metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleOverride = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!overrideDocId.trim()) {
      setOverrideError('Please enter a valid document identifier.');
      return;
    }
    
    setOverrideLoading(true);
    setOverrideMessage('');
    setOverrideError('');
    
    try {
      const res = await adminApi.overrideCategory(overrideDocId, overrideLabel);
      setOverrideMessage(res.message);
      setOverrideDocId('');
      // Refresh statistics after override
      fetchStats();
    } catch (err: any) {
      setOverrideError(err.response?.data?.detail || 'Category override failed. Validate document ID.');
    } finally {
      setOverrideLoading(false);
    }
  };

  const TARGET_CATEGORIES = [
    "Resume", "Aadhaar Card", "PAN Card", "Passport", "Driving License", 
    "Marksheet", "Degree Certificate", "Invoice", "Receipt", "Bank Statement", 
    "Generic Document"
  ];

  if (loading && !stats) {
    return (
      <div className="flex flex-col justify-center items-center py-40 gap-4">
        <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 text-sm">Retrieving system diagnostics...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-white/5 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-6.5 h-6.5 text-brand-400" />
            Administrative Panel
          </h2>
          <p className="text-slate-400 text-sm">Global upload metrics, daily trends, and document override operations</p>
        </div>
        <button
          onClick={fetchStats}
          disabled={loading}
          className="p-2 bg-slate-900 border border-white/5 rounded-xl hover:bg-slate-800 text-slate-400 hover:text-white transition-all cursor-pointer disabled:opacity-55"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 px-4 py-3 rounded-xl text-sm flex gap-2">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {stats && (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* Total Users */}
            <div className="glass-panel p-6 rounded-2xl flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-500/10 border border-blue-500/20 rounded-xl flex items-center justify-center text-blue-400">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500">Active Members</span>
                <h4 className="text-2xl font-extrabold text-white mt-0.5">{stats.total_users}</h4>
              </div>
            </div>

            {/* Total Uploads */}
            <div className="glass-panel p-6 rounded-2xl flex items-center gap-4">
              <div className="w-12 h-12 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center justify-center text-emerald-400">
                <UploadCloud className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500">Global Uploads</span>
                <h4 className="text-2xl font-extrabold text-white mt-0.5">{stats.total_uploads}</h4>
              </div>
            </div>

            {/* Classifier Accuracy */}
            <div className="glass-panel p-6 rounded-2xl flex items-center gap-4">
              <div className="w-12 h-12 bg-indigo-500/10 border border-indigo-500/20 rounded-xl flex items-center justify-center text-indigo-400">
                <Target className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500">Model Accuracy</span>
                <h4 className="text-2xl font-extrabold text-indigo-400 mt-0.5">{stats.classification_accuracy}%</h4>
              </div>
            </div>

            {/* Scores averages */}
            <div className="glass-panel p-6 rounded-2xl flex items-center gap-4">
              <div className="w-12 h-12 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-center justify-center text-amber-400">
                <Cpu className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500">Avg ATS Audit</span>
                <h4 className="text-2xl font-extrabold text-white mt-0.5">{stats.average_ats_score || '0.0'}</h4>
              </div>
            </div>

          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Upload Trends Area Chart (Left 2 Columns) */}
            <div className="lg:col-span-2 glass-panel rounded-3xl p-6 space-y-4">
              <h3 className="font-bold text-lg text-white flex items-center gap-2 pb-3 border-b border-white/5">
                <BarChart3 className="w-5 h-5 text-brand-400" />
                Upload Activity Trends (Last 7 Days)
              </h3>
              
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={stats.daily_uploads}
                    margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient id="colorUploads" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
                    <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickLine={false} />
                    <YAxis stroke="#64748b" fontSize={10} tickLine={false} allowDecimals={false} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                      itemStyle={{ color: '#fff' }}
                      labelStyle={{ color: '#64748b', fontSize: '10px' }}
                    />
                    <Area type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorUploads)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Category Override Panel (Right Column) */}
            <div className="glass-panel p-6 rounded-3xl space-y-4">
              <h3 className="font-bold text-lg text-white flex items-center gap-2 pb-3 border-b border-white/5">
                <Settings className="w-5 h-5 text-brand-400" />
                Category Override
              </h3>
              
              <p className="text-slate-400 text-xs leading-relaxed">
                Manually adjust document classification. If changed to Resume, the system automatically triggers structured ATS parsing.
              </p>

              <form onSubmit={handleOverride} className="space-y-4 pt-2">
                {overrideMessage && (
                  <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-4 py-2.5 rounded-xl text-xs flex gap-2">
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                    <span>{overrideMessage}</span>
                  </div>
                )}
                
                {overrideError && (
                  <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 px-4 py-2.5 rounded-xl text-xs flex gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{overrideError}</span>
                  </div>
                )}

                {/* Doc ID input */}
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Document ID</label>
                  <input
                    type="text"
                    value={overrideDocId}
                    onChange={(e) => setOverrideDocId(e.target.value)}
                    placeholder="Enter unique 32-char ID"
                    className="w-full bg-slate-950/45 border border-white/10 rounded-xl py-2 px-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
                    required
                  />
                </div>

                {/* Target dropdown */}
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Correct Category</label>
                  <select
                    value={overrideLabel}
                    onChange={(e) => setOverrideLabel(e.target.value)}
                    className="w-full bg-slate-950/45 border border-white/10 rounded-xl py-2 px-3 text-xs text-white focus:outline-none focus:border-brand-500"
                  >
                    {TARGET_CATEGORIES.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                <button
                  type="submit"
                  disabled={overrideLoading}
                  className="w-full bg-brand-500 hover:bg-brand-600 text-white font-bold py-2.5 rounded-xl flex items-center justify-center text-xs cursor-pointer shadow-md shadow-brand-500/10 transition-all disabled:opacity-55"
                >
                  {overrideLoading ? 'Applying Override...' : 'Apply Correction'}
                </button>
              </form>
            </div>

          </div>
        </>
      )}
    </div>
  );
}
