import React, { useState, useEffect, useCallback, useRef } from 'react';
import { docApi, adminApi } from '../services/api';
import { 
  FileText, RefreshCw, 
  Trash2, Search, ArrowUpRight, BarChart3, Plus
} from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';

interface DashboardPageProps {
  onUploadClick: () => void;
  onViewAnalysis: (docId: string) => void;
  onViewMatching: (docId: string) => void;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#14b8a6', '#f43f5e', '#64748b'];

export default function DashboardPage({ onUploadClick, onViewAnalysis, onViewMatching }: DashboardPageProps) {
  const [documents, setDocuments] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [chartData, setChartData] = useState<any[]>([]);
  const [stats, setStats] = useState({
    avgAts: 0,
    avgVerification: 0,
    accuracy: 96.5,
    totalCount: 0
  });

  const pollIntervalRef = useRef<any>(null);

  // Fetch documents list
  const fetchDocs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await docApi.history({
        search: search || undefined,
        status: statusFilter || undefined,
        page,
        limit: 10
      });
      setDocuments(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error('Error fetching document list:', err);
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, page]);

  // Fetch admin stats for charts and cards
  const fetchStats = useCallback(async () => {
    try {
      const res = await adminApi.stats();
      setStats({
        avgAts: res.average_ats_score,
        avgVerification: res.average_verification_score,
        accuracy: res.classification_accuracy,
        totalCount: res.total_uploads
      });
      
      const distribution = res.category_distribution.map((cat: any) => ({
        name: cat.label,
        value: cat.count
      }));
      setChartData(distribution);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  }, []);

  // Poll for pending/processing documents
  const startPolling = useCallback(() => {
    if (pollIntervalRef.current) return;
    
    pollIntervalRef.current = setInterval(async () => {
      // Check if there are any documents in pending or processing status
      const hasUnfinished = documents.some(doc => ['pending', 'processing'].includes(doc.status));
      if (!hasUnfinished) {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        return;
      }
      
      // Re-fetch docs silently
      try {
        const res = await docApi.history({
          search: search || undefined,
          status: statusFilter || undefined,
          page,
          limit: 10
        });
        setDocuments(res.items);
        setTotal(res.total);
        // Refresh charts
        fetchStats();
      } catch (err) {
        console.error('Error during status polling:', err);
      }
    }, 3000);
  }, [documents, search, statusFilter, page, fetchStats]);

  useEffect(() => {
    fetchDocs();
    fetchStats();
  }, [fetchDocs, fetchStats]);

  // Handle active status polling triggers
  useEffect(() => {
    const hasUnfinished = documents.some(doc => ['pending', 'processing'].includes(doc.status));
    if (hasUnfinished) {
      startPolling();
    } else {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    }
    
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [documents, startPolling]);

  const handleDelete = async (id: string) => {
    if (!window.confirm("Are you sure you want to delete this document?")) return;
    try {
      await docApi.delete(id);
      fetchDocs();
      fetchStats();
    } catch (err) {
      alert("Failed to delete document.");
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
      case 'processing': return 'bg-sky-500/10 text-sky-400 border border-sky-500/20 animate-pulse';
      case 'completed': return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
      case 'failed': return 'bg-rose-500/10 text-rose-400 border border-rose-500/20';
      default: return 'bg-slate-800 text-slate-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">Dashboard Overview</h2>
          <p className="text-slate-400 text-sm">Real-time asynchronous analytics dashboard representing files verification status.</p>
        </div>
        <button
          onClick={onUploadClick}
          className="bg-brand-500 hover:bg-brand-600 text-white font-bold py-2.5 px-4 rounded-xl flex items-center gap-2 cursor-pointer transition-all shadow-md shadow-brand-500/15"
        >
          <Plus className="w-5 h-5" />
          Upload Document
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between h-32">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Uploads</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-3xl font-extrabold text-white">{stats.totalCount}</span>
            <span className="text-slate-500 text-xs">Files verified</span>
          </div>
        </div>

        {/* Metric 2 */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between h-32">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Avg ATS Score</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-3xl font-extrabold text-white">{stats.avgAts ? `${stats.avgAts}` : 'N/A'}</span>
            <span className="text-slate-500 text-xs">Resumes / 100</span>
          </div>
        </div>

        {/* Metric 3 */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between h-32">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Verification Quality</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-3xl font-extrabold text-white">{stats.avgVerification ? `${stats.avgVerification}%` : 'N/A'}</span>
            <span className="text-slate-500 text-xs">Clarity average</span>
          </div>
        </div>

        {/* Metric 4 */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between h-32">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Model Accuracy</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-3xl font-extrabold text-brand-400">{stats.accuracy}%</span>
            <span className="text-slate-500 text-xs">Classification consensus</span>
          </div>
        </div>
      </div>

      {/* Main Charts & History Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Document History (Left 2 Columns) */}
        <div className="lg:col-span-2 glass-panel rounded-3xl p-6 space-y-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-white/5 pb-4">
            <h3 className="font-bold text-lg text-white">Files Processing Logs</h3>
            
            {/* Search and Filters */}
            <div className="flex w-full sm:w-auto gap-2">
              <div className="relative flex-1 sm:w-60">
                <Search className="absolute inset-y-0 left-3 w-4 h-4 my-auto text-slate-500" />
                <input
                  type="text"
                  placeholder="Search file or category..."
                  value={search}
                  onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                  className="w-full bg-slate-950/45 border border-white/10 rounded-xl py-2 pl-9 pr-4 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
                />
              </div>
              
              <select
                value={statusFilter}
                onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
                className="bg-slate-950/45 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-brand-500"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>

          {loading && documents.length === 0 ? (
            <div className="flex justify-center items-center py-20">
              <RefreshCw className="w-8 h-8 animate-spin text-brand-400" />
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-20 text-slate-500 text-sm">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-20" />
              No documents found. Start by uploading files.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/5 text-slate-500 text-xs font-bold uppercase tracking-wider">
                    <th className="pb-3 pr-2">File Info</th>
                    <th className="pb-3 px-2">Type Category</th>
                    <th className="pb-3 px-2">Status</th>
                    <th className="pb-3 px-2 text-center">Quality</th>
                    <th className="pb-3 pl-2 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-sm">
                  {documents.map((doc) => {
                    const rawFilename = doc.file_path ? doc.file_path.split(/[\\/]/).pop() || "" : "";
                    const filename = rawFilename.length > 33 ? rawFilename.substring(33) : (rawFilename || "Document");
                    const dateStr = new Date(doc.created_at).toLocaleDateString(undefined, {
                      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                    });
                    
                    return (
                      <tr key={doc.id} className="hover:bg-slate-900/10 transition-colors group">
                        {/* File details */}
                        <td className="py-3.5 pr-2">
                          <div className="flex items-center gap-2.5">
                            <div className="w-9 h-9 bg-slate-800 rounded-lg flex items-center justify-center border border-white/5 shrink-0">
                              <FileText className="w-4 h-4 text-slate-300" />
                            </div>
                            <div className="min-w-0">
                              <p className="font-semibold text-slate-200 truncate max-w-[150px] sm:max-w-[200px]" title={filename}>
                                {filename || "Document"}
                              </p>
                              <span className="text-slate-500 text-[11px] block">{dateStr}</span>
                            </div>
                          </div>
                        </td>
                        
                        {/* Classification Label */}
                        <td className="py-3.5 px-2">
                          {doc.classification_label ? (
                            <div>
                              <span className="font-semibold text-slate-300">{doc.classification_label}</span>
                              <span className="text-slate-500 text-[10px] block font-mono">
                                Conf: {Math.round(doc.classification_confidence * 100)}%
                              </span>
                            </div>
                          ) : (
                            <span className="text-slate-500 italic text-xs">Awaiting NLP...</span>
                          )}
                        </td>
                        
                        {/* Status Badge */}
                        <td className="py-3.5 px-2">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${getStatusBadgeClass(doc.status)}`}>
                            {doc.status}
                          </span>
                        </td>
                        
                        {/* Verification Score */}
                        <td className="py-3.5 px-2 text-center">
                          {doc.status === 'completed' ? (
                            <span className={`font-mono font-bold ${
                              doc.verification_score >= 80 ? 'text-emerald-400' :
                              doc.verification_score >= 50 ? 'text-amber-400' : 'text-rose-400'
                            }`}>
                              {doc.verification_score}/100
                            </span>
                          ) : (
                            <span className="text-slate-600 font-mono">-</span>
                          )}
                        </td>
                        
                        {/* Actions */}
                        <td className="py-3.5 pl-2 text-right">
                          <div className="flex items-center justify-end gap-1.5 opacity-80 group-hover:opacity-100 transition-opacity">
                            {doc.status === 'completed' && doc.classification_label === 'Resume' && (
                              <>
                                <button
                                  onClick={() => onViewAnalysis(doc.id)}
                                  className="p-1.5 bg-brand-500/10 text-brand-400 hover:bg-brand-500 hover:text-white rounded-lg transition-all cursor-pointer"
                                  title="View ATS & AI Analysis"
                                >
                                  <BarChart3 className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => onViewMatching(doc.id)}
                                  className="p-1.5 bg-violet-500/10 text-violet-400 hover:bg-violet-500 hover:text-white rounded-lg transition-all cursor-pointer"
                                  title="Match Job Description"
                                >
                                  <ArrowUpRight className="w-4 h-4" />
                                </button>
                              </>
                            )}
                            <button
                              onClick={() => handleDelete(doc.id)}
                              className="p-1.5 hover:bg-slate-800 text-slate-500 hover:text-rose-400 rounded-lg transition-all cursor-pointer"
                              title="Delete Record"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
          
          {/* Simple Pagination */}
          {total > 10 && (
            <div className="flex justify-between items-center pt-4 border-t border-white/5 text-xs text-slate-400">
              <button
                disabled={page === 1}
                onClick={() => setPage(p => Math.max(1, p - 1))}
                className="px-3 py-1.5 bg-slate-900 border border-white/5 rounded-lg disabled:opacity-40"
              >
                Previous
              </button>
              <span>Page {page} of {Math.ceil(total / 10)}</span>
              <button
                disabled={page >= Math.ceil(total / 10)}
                onClick={() => setPage(p => p + 1)}
                className="px-3 py-1.5 bg-slate-900 border border-white/5 rounded-lg disabled:opacity-40"
              >
                Next
              </button>
            </div>
          )}
        </div>

        {/* Charts & Distributions (Right Column) */}
        <div className="glass-panel rounded-3xl p-6 flex flex-col h-[400px] lg:h-auto">
          <h3 className="font-bold text-lg text-white border-b border-white/5 pb-4 mb-4">
            Category Distributions
          </h3>
          
          {chartData.length === 0 ? (
            <div className="flex-1 flex flex-col justify-center items-center text-slate-500 text-sm">
              <BarChart3 className="w-12 h-12 mb-2 opacity-25" />
              Upload files to visualize categories
            </div>
          ) : (
            <div className="flex-1 flex flex-col justify-between">
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                      itemStyle={{ color: '#fff' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              
              {/* Legend Summary */}
              <div className="grid grid-cols-2 gap-2 text-xs text-slate-400 mt-2 overflow-y-auto max-h-24">
                {chartData.map((item, idx) => (
                  <div key={idx} className="flex items-center gap-1.5 truncate">
                    <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></span>
                    <span className="truncate">{item.name}: {item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
