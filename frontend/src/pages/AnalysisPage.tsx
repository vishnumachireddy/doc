import { useState, useEffect } from 'react';
import { analysisApi } from '../services/api';
import { 
  ArrowLeft, Download, User, Mail, Phone, Award, Briefcase, 
  GraduationCap, Cpu, Layers, AlertCircle, FileText, CheckCircle2, ShieldAlert
} from 'lucide-react';

interface AnalysisPageProps {
  docId: string;
  onBackToDashboard: () => void;
}

export default function AnalysisPage({ docId, onBackToDashboard }: AnalysisPageProps) {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeSubTab, setActiveSubTab] = useState<'profile' | 'ats' | 'ai'>('profile');

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const res = await analysisApi.getReport(docId);
        setAnalysis(res);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to fetch resume analysis data.');
      } finally {
        setLoading(false);
      }
    };
    fetchAnalysis();
  }, [docId]);

  const handleExport = () => {
    // Navigate window directly to download endpoint
    const url = analysisApi.exportReportUrl(docId);
    window.open(url, '_blank');
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center py-40 gap-4">
        <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 text-sm">Processing natural language models...</p>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="glass-panel rounded-3xl p-8 text-center max-w-xl mx-auto space-y-4">
        <AlertCircle className="w-12 h-12 text-rose-500 mx-auto opacity-70" />
        <h3 className="text-lg font-bold text-white">Analysis Unavailable</h3>
        <p className="text-slate-400 text-sm">{error || "Could not load intelligence record."}</p>
        <button
          onClick={onBackToDashboard}
          className="bg-brand-500 text-white px-6 py-2.5 rounded-xl text-sm font-bold cursor-pointer"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  const { extracted_data, suggestions, ats_score, ai_likelihood_score } = analysis;
  const contact = extracted_data.get_current_user || extracted_data.contact || {};
  const skills = extracted_data.skills || [];
  const skillDurations = extracted_data.skill_durations || {};
  const experience = extracted_data.experience || [];
  const projects = extracted_data.projects || [];
  const education = extracted_data.education || [];
  const certifications = extracted_data.certifications || [];
  
  // Readiness Score
  const readiness = extracted_data.recruiter_readiness_score || 70;

  return (
    <div className="space-y-6 max-w-5xl mx-auto py-2">
      {/* Header Navigation */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToDashboard}
            className="p-2 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-white transition-all cursor-pointer"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-white">Resume Intelligence</h2>
            <p className="text-slate-400 text-sm">Semantic insights and ATS conformity scoring for {contact.name || 'Applicant'}</p>
          </div>
        </div>
        
        <button
          onClick={handleExport}
          className="w-full sm:w-auto bg-slate-800 hover:bg-slate-700 text-white font-bold py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 cursor-pointer transition-all border border-white/5 shadow-md"
        >
          <Download className="w-4 h-4" />
          Download Report
        </button>
      </div>

      {/* Highlights Dashboard Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* ATS score gauge */}
        <div className="glass-panel p-6 rounded-3xl flex flex-col items-center justify-center text-center relative overflow-hidden">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">ATS Compliance Score</span>
          <div className="relative w-32 h-32 flex items-center justify-center">
            {/* Circular Progress Ring */}
            <svg className="w-full h-full transform -rotate-90">
              <circle cx="64" cy="64" r="54" className="stroke-slate-800 fill-none" strokeWidth="8" />
              <circle 
                cx="64" 
                cy="64" 
                r="54" 
                className="stroke-brand-500 fill-none transition-all duration-1000" 
                strokeWidth="8" 
                strokeDasharray={339}
                strokeDashoffset={339 - (339 * ats_score) / 100}
                strokeLinecap="round"
              />
            </svg>
            <span className="absolute text-3xl font-black text-white">{ats_score}<span className="text-slate-500 text-sm font-normal">/100</span></span>
          </div>
          <p className="text-slate-400 text-xs mt-4">Calculated from document formatting, readability ease, and entity counts.</p>
        </div>

        {/* Readiness gauge */}
        <div className="glass-panel p-6 rounded-3xl flex flex-col items-center justify-center text-center relative overflow-hidden">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Recruiter Readiness</span>
          <div className="relative w-32 h-32 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90">
              <circle cx="64" cy="64" r="54" className="stroke-slate-800 fill-none" strokeWidth="8" />
              <circle 
                cx="64" 
                cy="64" 
                r="54" 
                className="stroke-emerald-500 fill-none transition-all duration-1000" 
                strokeWidth="8" 
                strokeDasharray={339}
                strokeDashoffset={339 - (339 * readiness) / 100}
                strokeLinecap="round"
              />
            </svg>
            <span className="absolute text-3xl font-black text-white">{readiness}%</span>
          </div>
          <p className="text-slate-400 text-xs mt-4">Weights formatting integrity alongside accumulated chronological experience.</p>
        </div>

        {/* AI Likelihood gauge */}
        <div className="glass-panel p-6 rounded-3xl flex flex-col items-center justify-center text-center relative overflow-hidden">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">AI Written Estimate</span>
          <div className="relative w-32 h-32 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90">
              <circle cx="64" cy="64" r="54" className="stroke-slate-800 fill-none" strokeWidth="8" />
              <circle 
                cx="64" 
                cy="64" 
                r="54" 
                className={`fill-none transition-all duration-1000 ${
                  ai_likelihood_score > 70 ? 'stroke-rose-500' :
                  ai_likelihood_score > 35 ? 'stroke-amber-500' : 'stroke-indigo-500'
                }`}
                strokeWidth="8" 
                strokeDasharray={339}
                strokeDashoffset={339 - (339 * ai_likelihood_score) / 100}
                strokeLinecap="round"
              />
            </svg>
            <span className="absolute text-3xl font-black text-white">{ai_likelihood_score}%</span>
          </div>
          <span className={`text-xs font-bold px-2 py-0.5 rounded-full mt-4 border uppercase tracking-wider ${
            ai_likelihood_score > 70 ? 'bg-rose-500/10 text-rose-400 border-rose-500/25' :
            ai_likelihood_score > 35 ? 'bg-amber-500/10 text-amber-400 border-amber-500/25' : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/25'
          }`}>
            {suggestions.ai_classification || (ai_likelihood_score > 70 ? "Mostly AI Assisted" : ai_likelihood_score > 35 ? "Human with AI" : "Mostly Human")}
          </span>
        </div>

      </div>

      {/* Tabs Selection */}
      <div className="flex bg-slate-900/60 p-1.5 rounded-2xl border border-white/5 w-full md:w-fit">
        <button
          onClick={() => setActiveSubTab('profile')}
          className={`flex items-center gap-2 px-5 py-2.5 text-sm font-bold rounded-xl transition-all duration-200 cursor-pointer ${
            activeSubTab === 'profile' ? 'bg-brand-500 text-white shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          <User className="w-4 h-4" />
          Extracted Profile
        </button>
        
        <button
          onClick={() => setActiveSubTab('ats')}
          className={`flex items-center gap-2 px-5 py-2.5 text-sm font-bold rounded-xl transition-all duration-200 cursor-pointer ${
            activeSubTab === 'ats' ? 'bg-brand-500 text-white shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Layers className="w-4 h-4" />
          ATS Improvements
        </button>

        <button
          onClick={() => setActiveSubTab('ai')}
          className={`flex items-center gap-2 px-5 py-2.5 text-sm font-bold rounded-xl transition-all duration-200 cursor-pointer ${
            activeSubTab === 'ai' ? 'bg-brand-500 text-white shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Cpu className="w-4 h-4" />
          Authorship Report
        </button>
      </div>

      {/* Tab Contents */}
      <div className="space-y-6">
        {activeSubTab === 'profile' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Profile Core (Left 2 Columns) */}
            <div className="lg:col-span-2 space-y-6">
              {/* Contact Card */}
              <div className="glass-panel p-6 rounded-3xl space-y-4">
                <h3 className="font-bold text-lg text-white flex items-center gap-2 pb-3 border-b border-white/5">
                  <User className="w-5 h-5 text-brand-400" />
                  Contact Credentials
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm text-slate-300">
                  <div>
                    <span className="text-slate-500 text-xs font-bold uppercase tracking-wider block">Full Name</span>
                    <span className="font-semibold text-white text-base">{contact.name || 'Applicant'}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-xs font-bold uppercase tracking-wider block">Email Address</span>
                    <span className="flex items-center gap-1.5 mt-0.5 truncate">
                      <Mail className="w-4 h-4 text-slate-500 shrink-0" />
                      {contact.email || 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-xs font-bold uppercase tracking-wider block">Contact Number</span>
                    <span className="flex items-center gap-1.5 mt-0.5">
                      <Phone className="w-4 h-4 text-slate-500" />
                      {contact.phone || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Experience Card */}
              <div className="glass-panel p-6 rounded-3xl space-y-6">
                <h3 className="font-bold text-lg text-white flex items-center gap-2 pb-3 border-b border-white/5">
                  <Briefcase className="w-5 h-5 text-brand-400" />
                  Professional Experience
                </h3>
                
                {experience.length === 0 ? (
                  <p className="text-slate-500 text-sm italic">No experience blocks extracted.</p>
                ) : (
                  <div className="relative border-l border-slate-800 ml-3 pl-6 space-y-6">
                    {experience.map((exp: any, idx: number) => (
                      <div key={idx} className="relative group">
                        {/* Timeline Node dot */}
                        <div className="absolute -left-[31px] top-1.5 w-4.5 h-4.5 bg-[#0b0f19] border-2 border-brand-500 rounded-full group-hover:scale-110 transition-transform"></div>
                        
                        <div>
                          <h4 className="font-bold text-slate-100 text-base">{exp.role}</h4>
                          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 mt-1">
                            <span className="text-brand-400">{exp.company}</span>
                            <span>•</span>
                            <span>{exp.duration}</span>
                          </div>
                          <p className="text-slate-400 text-sm mt-3 leading-relaxed whitespace-pre-line">{exp.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Projects Card */}
              <div className="glass-panel p-6 rounded-3xl space-y-6">
                <h3 className="font-bold text-lg text-white flex items-center gap-2 pb-3 border-b border-white/5">
                  <FileText className="w-5 h-5 text-brand-400" />
                  Key Projects
                </h3>
                
                {projects.length === 0 ? (
                  <p className="text-slate-500 text-sm italic">No project listings parsed.</p>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {projects.map((proj: any, idx: number) => (
                      <div key={idx} className="bg-slate-950/30 border border-white/5 rounded-2xl p-4 hover:border-brand-500/10 transition-colors">
                        <h4 className="font-bold text-slate-200 text-sm mb-2">{proj.title}</h4>
                        <p className="text-slate-400 text-xs leading-relaxed">{proj.description}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Profile Meta Info (Right Column) */}
            <div className="space-y-6">
              {/* Skills and years list */}
              <div className="glass-panel p-6 rounded-3xl space-y-4">
                <h3 className="font-bold text-base text-white flex items-center gap-2 pb-3 border-b border-white/5">
                  <Award className="w-4.5 h-4.5 text-brand-400" />
                  Skills Chronology
                </h3>
                {skills.length === 0 ? (
                  <p className="text-slate-500 text-xs italic">No skills cataloged.</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {skills.map((skill: string) => {
                      const years = skillDurations[skill] || 0.0;
                      return (
                        <div 
                          key={skill} 
                          className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 border border-white/5 text-slate-300 rounded-xl text-xs hover:border-brand-500/20 transition-all font-semibold"
                        >
                          <span>{skill}</span>
                          {years > 0.0 && (
                            <span className="px-1.5 py-0.2 bg-brand-500/10 text-brand-400 rounded-md text-[10px] font-mono font-bold">
                              {years} yrs
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
                <p className="text-slate-500 text-[10px] leading-relaxed pt-2">
                  ℹ️ Experience length calculated chronologically by parsing job section date ranges rather than just matching words.
                </p>
              </div>

              {/* Education Card */}
              <div className="glass-panel p-6 rounded-3xl space-y-4">
                <h3 className="font-bold text-base text-white flex items-center gap-2 pb-3 border-b border-white/5">
                  <GraduationCap className="w-4.5 h-4.5 text-brand-400" />
                  Education History
                </h3>
                {education.length === 0 ? (
                  <p className="text-slate-500 text-xs italic">No education listings extracted.</p>
                ) : (
                  <div className="space-y-3.5">
                    {education.map((edu: any, idx: number) => (
                      <div key={idx} className="text-xs">
                        <h4 className="font-bold text-slate-200">{edu.degree}</h4>
                        <p className="text-slate-400 mt-0.5">{edu.institution}</p>
                        <span className="text-slate-500 font-mono block mt-1">Graduation Year: {edu.year}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Certifications Card */}
              {certifications.length > 0 && (
                <div className="glass-panel p-6 rounded-3xl space-y-4">
                  <h3 className="font-bold text-base text-white flex items-center gap-2 pb-3 border-b border-white/5">
                    <Award className="w-4.5 h-4.5 text-brand-400" />
                    Certifications
                  </h3>
                  <ul className="list-disc list-inside text-xs text-slate-400 space-y-2">
                    {certifications.map((cert: string, idx: number) => (
                      <li key={idx} className="truncate" title={cert}>{cert}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

          </div>
        )}

        {activeSubTab === 'ats' && (
          <div className="glass-panel p-8 rounded-3xl space-y-6">
            <h3 className="font-bold text-xl text-white border-b border-white/5 pb-4">
              ATS Formatting & Optimization Recommendations
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Action Verbs */}
              <div className="space-y-3">
                <h4 className="text-sm font-extrabold uppercase tracking-wider text-slate-400">Action Verbs Usage</h4>
                <div className="bg-slate-950/40 border border-white/5 p-4 rounded-2xl min-h-24">
                  {suggestions.action_verbs && suggestions.action_verbs.length > 0 ? (
                    suggestions.action_verbs.map((item: string, i: number) => (
                      <div key={i} className="flex gap-2 text-sm text-slate-300 items-start">
                        <CheckCircle2 className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
                        <span>{item}</span>
                      </div>
                    ))
                  ) : (
                    <span className="text-xs text-slate-500 italic">No suggestions generated.</span>
                  )}
                </div>
              </div>

              {/* Layout and structure */}
              <div className="space-y-3">
                <h4 className="text-sm font-extrabold uppercase tracking-wider text-slate-400">Layout & ATS Formatting</h4>
                <div className="bg-slate-950/40 border border-white/5 p-4 rounded-2xl min-h-24">
                  {suggestions.ats_formatting && suggestions.ats_formatting.length > 0 ? (
                    suggestions.ats_formatting.map((item: string, i: number) => (
                      <div key={i} className="flex gap-2 text-sm text-slate-300 items-start">
                        <AlertCircle className="w-4 h-4 text-brand-400 shrink-0 mt-0.5" />
                        <span>{item}</span>
                      </div>
                    ))
                  ) : (
                    <span className="text-xs text-slate-500 italic">No formatting errors detected. Good structure!</span>
                  )}
                </div>
              </div>

              {/* Bullet style */}
              <div className="space-y-3">
                <h4 className="text-sm font-extrabold uppercase tracking-wider text-slate-400">Bullet Points Structure</h4>
                <div className="bg-slate-950/40 border border-white/5 p-4 rounded-2xl min-h-24">
                  {suggestions.bullet_points && suggestions.bullet_points.length > 0 ? (
                    suggestions.bullet_points.map((item: string, i: number) => (
                      <div key={i} className="flex gap-2 text-sm text-slate-300 items-start">
                        <AlertCircle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                        <span>{item}</span>
                      </div>
                    ))
                  ) : (
                    <div className="flex gap-2 text-sm text-emerald-400 items-center">
                      <CheckCircle2 className="w-4 h-4 shrink-0" />
                      <span>Consistent professional bullet usage verified.</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Project descriptions */}
              <div className="space-y-3">
                <h4 className="text-sm font-extrabold uppercase tracking-wider text-slate-400">Project Descriptions Quality</h4>
                <div className="bg-slate-950/40 border border-white/5 p-4 rounded-2xl min-h-24">
                  {suggestions.project_descriptions && suggestions.project_descriptions.length > 0 ? (
                    suggestions.project_descriptions.map((item: string, i: number) => (
                      <div key={i} className="flex gap-2 text-sm text-slate-300 items-start">
                        <AlertCircle className="w-4 h-4 text-brand-400 shrink-0 mt-0.5" />
                        <span>{item}</span>
                      </div>
                    ))
                  ) : (
                    <div className="flex gap-2 text-sm text-emerald-400 items-center">
                      <CheckCircle2 className="w-4 h-4 shrink-0" />
                      <span>All listed projects contain sufficient details.</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeSubTab === 'ai' && (
          <div className="glass-panel p-8 rounded-3xl space-y-6">
            <h3 className="font-bold text-xl text-white border-b border-white/5 pb-4 flex items-center gap-2">
              <Cpu className="w-5 h-5 text-indigo-400" />
              AI Writing Likelihood Detailed Report
            </h3>

            <div className="bg-[#0b0f19] border border-white/5 p-6 rounded-2xl space-y-4">
              <div className="flex items-center gap-3">
                <ShieldAlert className="w-8 h-8 text-indigo-400" />
                <div>
                  <h4 className="text-base font-bold text-slate-200">
                    Est. AI Assistance: <span className="text-indigo-400">{ai_likelihood_score}%</span>
                  </h4>
                  <p className="text-slate-500 text-xs">Probabilistic estimate based on text styling structures.</p>
                </div>
              </div>

              <div className="space-y-3 text-sm text-slate-300 pt-4">
                <p className="font-semibold text-slate-200">Authorship Evidence Details:</p>
                {suggestions.ai_analysis && suggestions.ai_analysis.length > 0 ? (
                  suggestions.ai_analysis.map((reason: string, idx: number) => (
                    <div key={idx} className="flex gap-2 items-start text-xs text-slate-400">
                      <span className="text-indigo-400">•</span>
                      <span>{reason}</span>
                    </div>
                  ))
                ) : (
                  <span className="text-xs text-slate-500 italic">No significant indicators of automated text templates detected.</span>
                )}
              </div>

              <div className="bg-slate-900/40 p-4 rounded-xl text-xs text-slate-500 mt-4 leading-relaxed border border-white/5">
                💡 **Platform Disclaimer**: Authorship estimation models represent a statistical evaluation of sentence pacing variation, lexical distribution, and common AI cliché densities. They are estimates and do not claim absolute certainty of automated generation. Use the results to optimize vocabulary diversity.
              </div>
            </div>
          </div>
        )}
      </div>

    </div>
  );
}
