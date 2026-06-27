import React, { useState } from 'react';
import { analysisApi } from '../services/api';
import { 
  ArrowLeft, Sparkles, AlertCircle, Layers, CheckCircle2, 
  ShieldAlert, BookOpen, AlertTriangle
} from 'lucide-react';

interface JobMatcherPageProps {
  docId: string;
  onBackToDashboard: () => void;
}

export default function JobMatcherPage({ docId, onBackToDashboard }: JobMatcherPageProps) {
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState('');

  const handleMatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobDescription.trim()) {
      setError('Please paste a job description first.');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const res = await analysisApi.matchJob(docId, jobDescription);
      setResults(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Job matching calculation failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto py-2">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={onBackToDashboard}
          className="p-2 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-white transition-all cursor-pointer"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-white">Semantic Job Matching</h2>
          <p className="text-slate-400 text-sm">Align professional profile components to target job description metrics</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        
        {/* Left Side: JD Input */}
        <div className="glass-panel p-6 rounded-3xl space-y-4">
          <h3 className="font-bold text-lg text-white flex items-center gap-2 pb-3 border-b border-white/5">
            <BookOpen className="w-5 h-5 text-brand-400" />
            Paste Job Description
          </h3>
          
          <form onSubmit={handleMatch} className="space-y-4">
            {error && (
              <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 px-4 py-3 rounded-xl text-sm flex gap-2">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{error}</span>
              </div>
            )}
            
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the target job description requirements here (e.g. key qualifications, required skills, technologies)..."
              rows={12}
              className="w-full bg-slate-950/45 border border-white/10 rounded-2xl p-4 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition-all resize-none"
              required
            />
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-brand-600 to-indigo-500 text-white font-bold py-3 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 active:scale-[0.99] disabled:opacity-50 disabled:scale-100 cursor-pointer shadow-lg shadow-brand-500/15"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Calculating Semantic Overlaps...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Evaluate Skill Match
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Side: Matching Results */}
        <div className="h-full">
          {results ? (
            /* Results Panel */
            <div className="glass-panel p-6 rounded-3xl space-y-6 animate-fade-in">
              <h3 className="font-bold text-lg text-white flex items-center gap-2 pb-3 border-b border-white/5">
                <Layers className="w-5 h-5 text-brand-400" />
                Matching Results
              </h3>

              {/* Similarity Score ring */}
              <div className="flex flex-col sm:flex-row items-center gap-6 bg-slate-950/20 p-5 rounded-2xl border border-white/5">
                <div className="relative w-28 h-28 flex items-center justify-center shrink-0">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle cx="56" cy="56" r="46" className="stroke-slate-800 fill-none" strokeWidth="8" />
                    <circle 
                      cx="56" 
                      cy="56" 
                      r="46" 
                      className={`fill-none transition-all duration-1000 ${
                        results.skill_match_percentage >= 85 ? 'stroke-emerald-500' :
                        results.skill_match_percentage >= 50 ? 'stroke-amber-500' : 'stroke-rose-500'
                      }`}
                      strokeWidth="8" 
                      strokeDasharray={289}
                      strokeDashoffset={289 - (289 * results.skill_match_percentage) / 100}
                      strokeLinecap="round"
                    />
                  </svg>
                  <span className="absolute text-2xl font-black text-white">{results.skill_match_percentage}%</span>
                </div>
                
                <div>
                  <h4 className="font-bold text-slate-200 text-sm">Semantic Skill Match Ratio</h4>
                  <p className="text-slate-400 text-xs mt-1.5 leading-relaxed">
                    Evaluates structural context similarities and keyword Jaccard indices across parsed details.
                  </p>
                </div>
              </div>

              {/* Missing Skills */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-500" />
                  Skill Gaps Detected ({results.missing_skills.length})
                </h4>
                
                <div className="bg-slate-950/40 p-4 border border-white/5 rounded-2xl min-h-16">
                  {results.missing_skills.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {results.missing_skills.map((skill: string) => (
                        <span 
                          key={skill} 
                          className="px-2.5 py-1 bg-amber-500/10 text-amber-400 rounded-lg text-xs font-semibold border border-amber-500/20"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <div className="flex gap-2 text-xs text-emerald-400 items-center">
                      <CheckCircle2 className="w-4 h-4 shrink-0" />
                      <span>Zero skill gaps! You match all primary requested credentials.</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Missing Keywords */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4 text-brand-400" />
                  High-Frequency Job Keywords Missing ({results.missing_keywords.length})
                </h4>
                
                <div className="bg-slate-950/40 p-4 border border-white/5 rounded-2xl min-h-16">
                  {results.missing_keywords.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {results.missing_keywords.map((kw: string) => (
                        <span 
                          key={kw} 
                          className="px-2.5 py-1 bg-brand-500/10 text-brand-400 rounded-lg text-xs font-semibold border border-brand-500/20"
                        >
                          {kw}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <div className="flex gap-2 text-xs text-slate-500 items-center">
                      <CheckCircle2 className="w-4 h-4 shrink-0" />
                      <span>Context keywords align with job specification.</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Actionable recommendations */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Improvement Suggestions</h4>
                <div className="space-y-2 text-xs text-slate-300 bg-slate-950/40 p-4 border border-white/5 rounded-2xl">
                  {results.improvement_suggestions.map((sug: string, idx: number) => (
                    <div key={idx} className="flex gap-2 items-start leading-relaxed">
                      <span className="text-brand-400 shrink-0 font-bold">•</span>
                      <span>{sug}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          ) : (
            /* Blank State Panel */
            <div className="glass-panel p-12 rounded-3xl text-center text-slate-500 flex flex-col items-center justify-center h-full min-h-[300px]">
              <Sparkles className="w-12 h-12 mb-3 opacity-25" />
              <h4 className="text-slate-300 font-bold mb-1">Evaluate Matching Matrix</h4>
              <p className="text-xs max-w-xs mx-auto leading-relaxed">
                Paste the requirements of the job description on the left and submit to verify qualification alignment.
              </p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
