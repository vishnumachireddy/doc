import React, { useState, useRef } from 'react';
import { docApi } from '../services/api';
import { UploadCloud, FileText, CheckCircle, AlertCircle, X, ArrowLeft, RefreshCw } from 'lucide-react';

interface UploaderPageProps {
  onBackToDashboard: () => void;
}

export default function UploaderPage({ onBackToDashboard }: UploaderPageProps) {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<any[]>([]);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateFiles = (selectedFiles: FileList): File[] => {
    const validFiles: File[] = [];
    const maxBytes = 15 * 1024 * 1024; // 15MB
    const allowedExts = ["pdf", "docx", "png", "jpg", "jpeg"];
    
    setError('');

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      const ext = file.name.split('.').pop()?.toLowerCase() || '';
      
      if (!allowedExts.includes(ext)) {
        setError(`File '${file.name}' has an unsupported extension (.${ext}).`);
        continue;
      }
      
      if (file.size > maxBytes) {
        setError(`File '${file.name}' exceeds the 15MB maximum size.`);
        continue;
      }
      
      validFiles.push(file);
    }
    
    return validFiles;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = validateFiles(e.dataTransfer.files);
      setFiles(prev => [...prev, ...dropped]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const selected = validateFiles(e.target.files);
      setFiles(prev => [...prev, ...selected]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    setUploading(true);
    setProgress(0);
    setError('');
    
    try {
      const res = await docApi.upload(files, (pct) => setProgress(pct));
      setResults(res);
      setFiles([]); // clear queue
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload process failed. Please check network/files.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto py-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToDashboard}
            className="p-2 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-white transition-all cursor-pointer"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-white">Upload Documents</h2>
            <p className="text-slate-400 text-sm">Add files to verify authenticity and analyze profile metrics</p>
          </div>
        </div>
        <span className="text-xs font-semibold px-3 py-1.5 bg-slate-900 border border-white/5 text-slate-400 rounded-lg">
          Max File Size: 15MB
        </span>
      </div>

      {results.length > 0 ? (
        /* SUCCESS UPLOAD SUMMARY PANEL */
        <div className="glass-panel rounded-3xl p-8 glow-emerald space-y-6">
          <div className="flex items-center gap-3 text-emerald-400">
            <CheckCircle className="w-8 h-8" />
            <div>
              <h3 className="text-lg font-bold text-white">Files Ingested Successfully</h3>
              <p className="text-slate-400 text-sm">Asynchronous ML queues are analyzing document binary payloads...</p>
            </div>
          </div>

          <div className="space-y-3 bg-slate-950/40 p-4 rounded-2xl border border-white/5">
            {results.map((res, i) => (
              <div key={i} className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-brand-400" />
                  <span className="text-sm font-semibold text-slate-200">
                    ID: <span className="text-brand-400 font-mono text-xs">{res.id}</span>
                  </span>
                </div>
                <span className="text-xs font-bold px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 uppercase tracking-wider">
                  {res.status}
                </span>
              </div>
            ))}
          </div>

          <div className="flex gap-4">
            <button
              onClick={onBackToDashboard}
              className="flex-1 bg-brand-500 hover:bg-brand-600 text-white font-bold py-3 px-4 rounded-xl shadow-lg shadow-brand-500/10 cursor-pointer text-center text-sm transition-all"
            >
              Go to Dashboard
            </button>
            <button
              onClick={() => setResults([])}
              className="px-6 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white font-bold py-3 rounded-xl cursor-pointer text-sm transition-all"
            >
              Upload More
            </button>
          </div>
        </div>
      ) : (
        /* MAIN UPLOAD ZONE PANEL */
        <div className="space-y-6">
          {error && (
            <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 px-4 py-3 rounded-xl text-sm flex items-start gap-2">
              <AlertCircle className="w-5 h-5 mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Drag & Drop Area */}
          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-300 relative ${
              dragActive 
                ? 'border-emerald-500 bg-emerald-500/5 shadow-lg shadow-emerald-500/5' 
                : 'border-slate-700 hover:border-brand-500 bg-slate-900/20 hover:bg-slate-900/30'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleChange}
              className="hidden"
              accept=".pdf,.docx,.png,.jpg,.jpeg"
            />
            
            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 bg-slate-800/80 rounded-2xl flex items-center justify-center border border-white/5 text-slate-400">
                <UploadCloud className="w-9 h-9" />
              </div>
              <div>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="text-brand-400 hover:text-brand-300 font-bold hover:underline cursor-pointer"
                >
                  Click to upload
                </button>
                <span className="text-slate-400"> or drag and drop files here</span>
                <p className="text-slate-500 text-xs mt-2">
                  Supports PDF, DOCX, PNG, JPG, JPEG (Max 15MB)
                </p>
              </div>
            </div>
          </div>

          {/* File Queue List */}
          {files.length > 0 && (
            <div className="glass-panel rounded-3xl p-6 space-y-4">
              <h3 className="text-sm font-bold tracking-wider text-slate-400 uppercase">
                Upload Queue ({files.length})
              </h3>
              
              <div className="space-y-2">
                {files.map((file, idx) => {
                  const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                  return (
                    <div key={idx} className="flex items-center justify-between bg-slate-950/40 p-3.5 rounded-xl border border-white/5">
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-slate-400" />
                        <div>
                          <p className="text-sm font-semibold text-slate-200 max-w-sm truncate">{file.name}</p>
                          <p className="text-slate-500 text-xs">{sizeMB} MB</p>
                        </div>
                      </div>
                      <button
                        onClick={() => removeFile(idx)}
                        disabled={uploading}
                        className="p-1 hover:bg-slate-800 rounded text-slate-500 hover:text-white cursor-pointer transition-all"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  );
                })}
              </div>

              {/* Progress indicator */}
              {uploading && (
                <div className="space-y-2 pt-2">
                  <div className="flex justify-between text-xs font-semibold text-slate-400">
                    <span className="flex items-center gap-1.5">
                      <RefreshCw className="w-3.5 h-3.5 animate-spin text-brand-400" />
                      Uploading binary buffers...
                    </span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-brand-500 to-indigo-500 transition-all duration-150"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {/* Action trigger */}
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="w-full bg-gradient-to-r from-brand-600 to-indigo-500 text-white font-bold py-3 rounded-xl flex items-center justify-center shadow-lg shadow-brand-500/10 cursor-pointer transition-all hover:opacity-90 active:scale-[0.99] disabled:opacity-50 disabled:scale-100 mt-4"
              >
                {uploading ? 'Ingesting data payload...' : 'Analyze Documents'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
