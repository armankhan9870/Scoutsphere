import React, { useState, useEffect } from 'react';
import { apiFetch, getValidExternalUrl, downloadTailoredResumeFile } from '../api/client';

import { useAuth } from '../context/AuthContext';
import { CheckCircle2, AlertCircle, Download, ExternalLink, FileText } from 'lucide-react';

interface SkillGapLearningProps {
  opportunity?: any;
}

export const SkillGapLearning: React.FC<SkillGapLearningProps> = ({ opportunity }) => {
  const { user } = useAuth();
  const userId = user?.id || '3e8ec9ae-9d67-48f7-9622-c52de2c7def9';

  const [activeTab, setActiveTab] = useState<'tailored' | 'original'>('tailored');


  const oppTitle = opportunity?.title || 'Associate AI Systems Engineer';
  const oppCompany = opportunity?.company_name || 'ScoutSphere Inc';
  const applyUrl = opportunity?.source_url || 'https://www.linkedin.com/jobs/search/?keywords=AI%20Engineer';
  const oppId = opportunity?.id || 'e2ece369-11c5-4234-ac41-af2e6bb18e13';

  useEffect(() => {
    const fetchSkillGap = async () => {
      try {
        await apiFetch<any>(`/skill-gaps/users/${userId}/skill-gaps`).catch(() => null);
      } catch (err) {
        console.error('Failed to load skill gap data:', err);
      }
    };

    fetchSkillGap();
  }, [userId, oppId]);


  const matchScore = opportunity?.match_score || 92.0;

  return (
    <div className="space-y-8">
      {/* Top Header (Matching Image 3) */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Opportunity Analysis</h1>
          <p className="text-xs text-slate-500 font-semibold mt-0.5">
            {oppTitle} - <span className="text-slate-800 font-extrabold">{oppCompany}</span>
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => downloadTailoredResumeFile(oppId)}
            className="scout-btn-secondary text-xs px-4 py-2"
          >
            <Download className="w-3.5 h-3.5 text-blue-600" />
            <span>Download Tailored Resume</span>
          </button>

          <button
            onClick={() => {
              const targetUrl = getValidExternalUrl(applyUrl, oppTitle, oppCompany);
              window.open(targetUrl, '_blank');
            }}
            className="scout-btn-primary text-xs px-5 py-2"
          >
            <span>Apply via ScoutSphere</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </div>

      </div>

      {/* Main 2-Column Grid Layout (Matching Image 3) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: AI Suitability & Key Requirements (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* AI Suitability Score Card */}
          <div className="scout-card p-6 flex items-center justify-between bg-slate-50 border-slate-200">
            <div className="space-y-1 pr-4">
              <h3 className="text-base font-extrabold text-slate-900">AI Suitability Score</h3>
              <p className="text-xs text-slate-600 font-medium leading-relaxed">
                Your current profile is a strong match for this role, but there are specific areas to optimize for ATS screening.
              </p>
            </div>

            {/* Green Circular Score Gauge */}
            <div className="relative w-16 h-16 shrink-0 flex items-center justify-center">
              <svg className="w-16 h-16 transform -rotate-90">
                <circle cx="32" cy="32" r="24" stroke="#cbd5e1" strokeWidth="4" fill="transparent" />
                <circle cx="32" cy="32" r="24" stroke="#059669" strokeWidth="4" fill="transparent" strokeDasharray="150" strokeDashoffset={`${150 - (150 * (matchScore / 100))}`} />
              </svg>
              <span className="absolute font-black text-emerald-700 text-sm">{matchScore}%</span>
            </div>
          </div>

          {/* Key Requirements Checklist Card */}
          <div className="scout-card p-6 space-y-4">
            <span className="text-[11px] font-extrabold text-slate-500 uppercase tracking-wider block">
              KEY REQUIREMENTS
            </span>

            <div className="space-y-3.5 text-xs font-medium">
              <div className="flex items-start space-x-3 text-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>Proficiency in Python and FastAPI backend services.</span>
              </div>

              <div className="flex items-start space-x-3 text-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>Experience with PostgreSQL, async architecture, and Redis.</span>
              </div>

              <div className="flex items-start space-x-3 text-slate-800">
                <AlertCircle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                <span>Familiarity with containerization (Docker/Kubernetes).</span>
              </div>
            </div>
          </div>

          {/* Skill Gap Detected Alert Card (Pink/Light Red background) */}
          <div className="rounded-2xl p-5 bg-rose-50/70 border border-rose-200 text-rose-900 space-y-2">
            <div className="flex items-center space-x-2 text-rose-700 font-extrabold text-xs">
              <AlertCircle className="w-4 h-4 text-rose-600" />
              <span>Skill Gap Detected</span>
            </div>
            <p className="text-xs text-rose-800 leading-relaxed font-medium">
              To increase your match score to 96%, we recommend learning <strong className="font-black text-rose-950">Docker</strong>. Adding this keyword to your tailored resume will significantly improve ATS pass rates.
            </p>
          </div>
        </div>

        {/* Right Column: Resume Tailoring Engine Preview (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-extrabold text-slate-900 flex items-center space-x-2">
              <FileText className="w-4 h-4 text-blue-600" />
              <span>Resume Tailoring Engine</span>
            </h3>

            {/* Toggle Tabs (Matching Image 3) */}
            <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-bold">
              <button
                onClick={() => setActiveTab('tailored')}
                className={`px-3 py-1.5 rounded-lg transition ${
                  activeTab === 'tailored' ? 'bg-primary text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Tailored (After)
              </button>
              <button
                onClick={() => setActiveTab('original')}
                className={`px-3 py-1.5 rounded-lg transition ${
                  activeTab === 'original' ? 'bg-primary text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Original (Before)
              </button>
            </div>
          </div>

          {/* Styled Document Paper Preview */}
          <div className="resume-paper max-h-[600px] overflow-y-auto border-2 border-slate-200 shadow-lg">
            {/* Header / Contact */}
            <div className="text-center space-y-1 border-b border-slate-200 pb-4">
              <h2 className="text-xl font-black text-slate-900">Alex Rivera</h2>
              <p className="text-xs text-slate-500 font-medium">
                alex.rivera@example.com | (555) 019-2831 | github.com/alexrivera
              </p>
            </div>

            {/* Education */}
            <div className="space-y-1">
              <h3 className="font-extrabold text-xs text-blue-700 uppercase tracking-wider border-b border-slate-100 pb-1">
                EDUCATION
              </h3>
              <div className="flex justify-between text-xs font-bold text-slate-800">
                <span>B.S. Computer Science, State University</span>
                <span className="text-slate-500 font-normal">Expected May 2026</span>
              </div>
              <p className="text-xs text-slate-600 font-medium">GPA: 3.8/4.0</p>
            </div>

            {/* Experience */}
            <div className="space-y-2">
              <h3 className="font-extrabold text-xs text-blue-700 uppercase tracking-wider border-b border-slate-100 pb-1">
                EXPERIENCE
              </h3>
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-bold text-slate-800">
                  <span>Software Engineering Intern | TechCorp</span>
                  <span className="text-slate-500 font-normal">Jun 2025 - Aug 2025</span>
                </div>
                <ul className="list-disc list-inside text-xs text-slate-700 space-y-1 font-medium pl-1">
                  <li>
                    Developed high-throughput async microservices using{' '}
                    <span className="highlight-tag">Python and FastAPI</span>, improving API throughput by 40%.
                  </li>
                  <li>
                    Optimized query performance and schema indexing on{' '}
                    <span className="highlight-tag">PostgreSQL and Redis</span>.
                  </li>
                  <li>Participated in daily stand-ups, code reviews, and container deployment pipelines.</li>
                </ul>
              </div>
            </div>

            {/* Projects */}
            <div className="space-y-2">
              <h3 className="font-extrabold text-xs text-blue-700 uppercase tracking-wider border-b border-slate-100 pb-1">
                PROJECTS
              </h3>
              <div>
                <span className="font-bold text-slate-800 text-xs block">ScoutSphere Career Assistant</span>
                <p className="text-xs text-slate-600 font-medium">
                  Built a production multi-agent system using FastAPI, LangGraph, SentenceTransformers, and async PostgreSQL database engines.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
