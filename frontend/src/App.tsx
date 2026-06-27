import { useState, useEffect } from 'react';
import { authApi } from './services/api';
import AuthScreen from './components/AuthScreen';
import DashboardPage from './pages/DashboardPage';
import UploaderPage from './pages/UploaderPage';
import AnalysisPage from './pages/AnalysisPage';
import JobMatcherPage from './pages/JobMatcherPage';
import AdminPage from './pages/AdminPage';

import { ShieldCheck, LogOut, LayoutDashboard, UploadCloud, ShieldAlert, Loader2 } from 'lucide-react';

export default function App() {
  const [user, setUser] = useState<any>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'uploader' | 'analysis' | 'matching' | 'admin'>('dashboard');
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);

  // Check user session on mount
  useEffect(() => {
    const verifySession = async () => {
      try {
        const currentUser = await authApi.me();
        setUser(currentUser);
      } catch (err) {
        setUser(null);
      } finally {
        setCheckingAuth(false);
      }
    };
    verifySession();
  }, []);

  const handleLogout = async () => {
    try {
      await authApi.logout();
      setUser(null);
      setActiveTab('dashboard');
      setSelectedDocId(null);
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  const handleViewAnalysis = (docId: string) => {
    setSelectedDocId(docId);
    setActiveTab('analysis');
  };

  const handleViewMatching = (docId: string) => {
    setSelectedDocId(docId);
    setActiveTab('matching');
  };

  if (checkingAuth) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#070b13] gap-3 text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
        <span className="text-xs font-semibold tracking-wider">Restoring secure session...</span>
      </div>
    );
  }

  if (!user) {
    return <AuthScreen onAuthSuccess={setUser} />;
  }

  return (
    <div className="min-h-screen bg-[#070b13] flex flex-col relative overflow-hidden">
      {/* Decorative Glow Circles */}
      <div className="absolute top-0 right-1/4 w-[400px] h-[400px] bg-brand-500/5 rounded-full blur-[140px] animate-pulse-slow pointer-events-none"></div>
      <div className="absolute bottom-0 left-1/4 w-[400px] h-[400px] bg-indigo-500/5 rounded-full blur-[140px] animate-pulse-slow pointer-events-none" style={{ animationDelay: '3s' }}></div>

      {/* Navigation Header */}
      <header className="glass-nav sticky top-0 z-50 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div 
              className="flex items-center gap-2 cursor-pointer group"
              onClick={() => { setActiveTab('dashboard'); setSelectedDocId(null); }}
            >
              <div className="w-8 h-8 bg-gradient-to-tr from-brand-600 to-indigo-500 rounded-lg flex items-center justify-center shadow shadow-brand-500/20 border border-brand-400/20 group-hover:scale-105 transition-transform">
                <ShieldCheck className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-black text-white">
                Resume<span className="gradient-text">IQ</span>
              </span>
            </div>

            {/* Navigation Tabs */}
            <nav className="hidden sm:flex items-center gap-1 bg-slate-950/40 p-1 rounded-xl border border-white/5">
              <button
                onClick={() => { setActiveTab('dashboard'); setSelectedDocId(null); }}
                className={`flex items-center gap-1.5 px-4 py-2 text-xs font-bold rounded-lg transition-all duration-200 cursor-pointer ${
                  activeTab === 'dashboard' ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <LayoutDashboard className="w-3.5 h-3.5" />
                Dashboard
              </button>
              
              <button
                onClick={() => { setActiveTab('uploader'); setSelectedDocId(null); }}
                className={`flex items-center gap-1.5 px-4 py-2 text-xs font-bold rounded-lg transition-all duration-200 cursor-pointer ${
                  activeTab === 'uploader' ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <UploadCloud className="w-3.5 h-3.5" />
                Upload Documents
              </button>

              <button
                onClick={() => { setActiveTab('admin'); setSelectedDocId(null); }}
                className={`flex items-center gap-1.5 px-4 py-2 text-xs font-bold rounded-lg transition-all duration-200 cursor-pointer ${
                  activeTab === 'admin' ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <ShieldAlert className="w-3.5 h-3.5" />
                Admin Panel
              </button>
            </nav>

            {/* Profile & Logout */}
            <div className="flex items-center gap-4">
              <span className="hidden lg:inline text-xs font-semibold px-3 py-1.5 bg-slate-900 border border-white/5 text-slate-400 rounded-lg max-w-[200px] truncate">
                👤 {user.email}
              </span>
              <button
                onClick={handleLogout}
                className="p-2 bg-slate-900 border border-white/5 rounded-xl hover:bg-slate-800 text-slate-400 hover:text-rose-400 transition-all cursor-pointer shadow-sm"
                title="Sign Out"
              >
                <LogOut className="w-4.5 h-4.5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Area */}
      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 z-10">
        {activeTab === 'dashboard' && (
          <DashboardPage 
            onUploadClick={() => setActiveTab('uploader')}
            onViewAnalysis={handleViewAnalysis}
            onViewMatching={handleViewMatching}
          />
        )}
        
        {activeTab === 'uploader' && (
          <UploaderPage 
            onBackToDashboard={() => setActiveTab('dashboard')}
          />
        )}

        {activeTab === 'analysis' && selectedDocId && (
          <AnalysisPage 
            docId={selectedDocId}
            onBackToDashboard={() => { setActiveTab('dashboard'); setSelectedDocId(null); }}
          />
        )}

        {activeTab === 'matching' && selectedDocId && (
          <JobMatcherPage 
            docId={selectedDocId}
            onBackToDashboard={() => { setActiveTab('dashboard'); setSelectedDocId(null); }}
          />
        )}

        {activeTab === 'admin' && (
          <AdminPage />
        )}
      </main>

      {/* Global Footer */}
      <footer className="border-t border-white/5 py-4 text-center text-slate-600 text-xs mt-auto">
        <p>© 2026 ResumeIQ. Containerized Full-Stack AI Platform.</p>
      </footer>
    </div>
  );
}
