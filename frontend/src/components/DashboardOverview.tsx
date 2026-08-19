import React, { useState, useEffect } from 'react';
import { apiFetch } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Search, FolderCheck, Award, TrendingUp, Building, MapPin, ArrowRight, MessageSquare, X } from 'lucide-react';

interface DashboardOverviewProps {
  onNavigateTab: (tab: string) => void;
  onSelectOpportunity?: (opp: any) => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({ onNavigateTab, onSelectOpportunity }) => {
  const { user } = useAuth();
  const userId = user?.id || '3e8ec9ae-9d67-48f7-9622-c52de2c7def9';

  const [showAiPopup, setShowAiPopup] = useState(true);
  const [stats, setStats] = useState<any>({
    total_applications: 3,
    submitted: 2,
    response_rate_percent: 66.7,
  });
  const [opportunities, setOpportunities] = useState<any[]>([]);


  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        // 1. Load Application Stats
        const statsData = await apiFetch<any>(`/applications/users/${userId}/applications/stats`).catch(() => null);
        if (statsData?.pipeline_stats) {
          setStats(statsData.pipeline_stats);
        }

        // 2. Load Opportunities Catalog
        const oppsData = await apiFetch<any>('/opportunities/search').catch(() => null);
        if (oppsData?.items && oppsData.items.length > 0) {
          setOpportunities(oppsData.items.slice(0, 4));
        } else {
          setOpportunities([
            {
              id: '93080d6b-a6ee-4710-9ddc-b77896618db4',
              title: 'Backend Engineering Intern',
              company_name: 'Stripe',
              location: 'San Francisco, CA (Hybrid)',
              match_score: 94.5,
              required_skills_json: ['Python', 'FastAPI', 'PostgreSQL', 'Redis'],
              posted: 'Posted 2 days ago',
              source_url: 'https://stripe.com/jobs/search',
            },
            {
              id: '6264f7ce-fc39-4201-a77f-2a5af377b819',
              title: 'AI/ML Research Intern',
              company_name: 'Google DeepMind',
              location: 'Remote',
              match_score: 92.0,
              required_skills_json: ['Python', 'PyTorch', 'LangChain', 'LangGraph'],
              posted: 'Posted today',
              source_url: 'https://deepmind.google/careers/',
            },
          ]);
        }
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      }
    };

    loadDashboardData();
  }, [userId]);


  return (
    <div className="space-y-8 relative pb-16">
      {/* 3 Top Stat Cards (Matching Image 1) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Stat Card 1 */}
        <div className="scout-card p-6 flex flex-col justify-between space-y-4">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[11px] font-extrabold text-slate-500 uppercase tracking-wider block mb-1">
                OPPORTUNITIES FOUND TODAY
              </span>
              <span className="text-4xl font-black text-primary leading-none">
                {opportunities.length > 0 ? opportunities.length * 4 + 8 : 24}
              </span>
            </div>
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Search className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-center space-x-1.5 text-emerald-700 text-xs font-bold">
            <TrendingUp className="w-4 h-4 text-emerald-600" />
            <span>+12% vs yesterday</span>
          </div>
        </div>

        {/* Stat Card 2 */}
        <div className="scout-card p-6 flex flex-col justify-between space-y-4">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[11px] font-extrabold text-slate-500 uppercase tracking-wider block mb-1">
                APPLICATIONS IN PROGRESS
              </span>
              <span className="text-4xl font-black text-slate-900 leading-none">
                {stats.total_applications || 3}
              </span>
            </div>
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <FolderCheck className="w-5 h-5" />
            </div>
          </div>
          <span className="text-xs text-slate-500 font-bold">
            {stats.submitted || 2} pending response
          </span>
        </div>

        {/* Stat Card 3 */}
        <div className="scout-card p-6 flex flex-col justify-between space-y-4">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[11px] font-extrabold text-slate-500 uppercase tracking-wider block mb-1">
                RESUME STRENGTH
              </span>
              <span className="text-4xl font-black text-emerald-700 leading-none">85%</span>
            </div>
            {/* Circular Gauge Graphic */}
            <div className="relative w-12 h-12 flex items-center justify-center">
              <svg className="w-12 h-12 transform -rotate-90">
                <circle cx="24" cy="24" r="18" stroke="#e2e8f0" strokeWidth="4" fill="transparent" />
                <circle cx="24" cy="24" r="18" stroke="#059669" strokeWidth="4" fill="transparent" strokeDasharray="113" strokeDashoffset="17" />
              </svg>
            </div>
          </div>
          <button onClick={() => onNavigateTab('resume-tailor')} className="text-xs font-bold text-primary hover:text-blue-700 flex items-center space-x-1">
            <span>View AI Suggestions</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Recommended for You Section (Matching Image 1) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-black text-slate-900 tracking-tight">Recommended for You</h2>
            <p className="text-xs text-slate-500 font-medium">AI-matched opportunities based on your skills</p>
          </div>
          <button onClick={() => onNavigateTab('opportunities')} className="text-xs font-extrabold text-primary hover:text-blue-700">
            View All
          </button>
        </div>

        {/* Job Opportunity Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {opportunities.map((opp) => (
            <div
              key={opp.id}
              className="scout-card p-6 border-l-4 border-l-emerald-600 space-y-4 hover:border-l-primary transition cursor-pointer"
              onClick={() => {
                if (onSelectOpportunity) onSelectOpportunity(opp);
                onNavigateTab('skill-gap');
              }}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-slate-500 text-xs">
                    {opp.company_name ? opp.company_name.slice(0, 2).toUpperCase() : 'ST'}
                  </div>
                  <div>
                    <h3 className="font-extrabold text-slate-900 text-base hover:text-primary transition">{opp.title}</h3>
                    <p className="text-xs text-slate-500 font-semibold flex items-center space-x-1.5 mt-0.5">
                      <Building className="w-3.5 h-3.5 text-slate-400" />
                      <span>{opp.company_name}</span>
                      <span>•</span>
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      <span>{opp.location || 'Remote'}</span>
                    </p>
                  </div>
                </div>

                <span className="badge-match">
                  <Award className="w-3 h-3 text-emerald-600" />
                  <span>{opp.match_score || 94.5}% Match</span>
                </span>
              </div>

              <div className="flex flex-wrap gap-1.5 pt-1">
                {(opp.required_skills_json || opp.required_skills || ['Python', 'FastAPI']).map((sk: string, i: number) => (
                  <span key={i} className="px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200 text-[11px] font-bold text-slate-700 font-mono">
                    {sk}
                  </span>
                ))}
              </div>

              <div className="border-t border-slate-100 pt-4 flex items-center justify-between text-xs" onClick={(e) => e.stopPropagation()}>
                <span className="text-slate-400 font-medium">Posted recently</span>
                <button
                  onClick={() => {
                    if (onSelectOpportunity) onSelectOpportunity(opp);
                    onNavigateTab('skill-gap');
                  }}
                  className="scout-btn-secondary text-xs px-3.5 py-1.5"
                >
                  <span>📊 Analyze Fit</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Floating AI Popup Widget */}
      {showAiPopup && (
        <div className="fixed bottom-6 right-6 z-50 flex items-end space-x-3">
          <div className="bg-white rounded-2xl p-4 shadow-2xl border border-slate-200 max-w-sm space-y-3 animate-fadeIn">
            <div className="flex items-start justify-between space-x-2">
              <div className="flex items-center space-x-2 text-primary font-extrabold text-xs">
                <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center">
                  🤖
                </div>
                <span>AI Agent Nudge</span>
              </div>
              <button onClick={() => setShowAiPopup(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-700 leading-relaxed font-medium">
              I found <strong className="text-slate-900 font-extrabold">3 new opportunities</strong> matching your Python and Backend Engineer skills. Want to see a quick analysis?
            </p>

            <div className="flex items-center space-x-2 pt-1">
              <button onClick={() => onNavigateTab('opportunities')} className="scout-btn-primary text-xs px-3 py-1.5">
                Yes, show me
              </button>
              <button onClick={() => setShowAiPopup(false)} className="scout-btn-secondary text-xs px-3 py-1.5">
                Later
              </button>
            </div>
          </div>

          <button onClick={() => onNavigateTab('chat')} className="w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center shadow-lg shadow-blue-500/30 hover:scale-105 transition">
            <MessageSquare className="w-6 h-6" />
          </button>
        </div>
      )}
    </div>
  );
};
