import React from 'react';
import { CheckCircle2, Lock, Edit, Sparkles, AlertCircle, ArrowRight } from 'lucide-react';



export const RoadmapView: React.FC = () => {
  const milestones = [
    {
      id: 1,
      title: 'React Native Certification',
      subtitle: 'Meta Coursera Program',
      date: 'Jan 2024',
      status: 'COMPLETED',
    },
    {
      id: 2,
      title: 'First Hackathon Win',
      subtitle: 'Global AI Build-a-thon',
      date: 'Mar 2024',
      status: 'COMPLETED',
    },
    {
      id: 3,
      title: 'System Design Interview Prep',
      subtitle: 'Mastering scalable architecture',
      date: 'In Progress',
      status: 'IN_PROGRESS',
    },
    {
      id: 4,
      title: 'Lead a Feature Team',
      subtitle: 'Target role requirement',
      date: 'Q3 2024',
      status: 'LOCKED',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Career Roadmap</h1>
          <p className="text-xs text-slate-500 font-semibold mt-0.5">
            Target: <span className="text-blue-700 font-extrabold">Senior Frontend Developer</span>
          </p>
        </div>

        <button className="scout-btn-secondary text-xs px-4 py-2 self-start md:self-auto">
          <Edit className="w-3.5 h-3.5 text-blue-600" />
          <span>Edit Target</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Vertical Timeline Card (Matching Image 2) */}
        <div className="lg:col-span-2 scout-card p-8 space-y-6 bg-white relative">
          <div className="flex items-center space-x-2 text-slate-900 font-extrabold text-sm border-b border-slate-100 pb-4">
            <span className="text-emerald-600 font-black text-base">📈</span>
            <span>Milestones</span>
          </div>

          <div className="relative pl-6 space-y-12">
            {/* Continuous Vertical Line */}
            <div className="absolute left-[31px] top-4 bottom-4 w-[2px] bg-slate-200"></div>

            {milestones.map((ms) => {
              const isCompleted = ms.status === 'COMPLETED';
              const isInProgress = ms.status === 'IN_PROGRESS';
              const isLocked = ms.status === 'LOCKED';

              return (
                <div key={ms.id} className="relative flex items-start space-x-6 z-10">
                  {/* Node Icon */}
                  <div className="shrink-0 bg-white rounded-full p-1">
                    {isCompleted && (
                      <div className="w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center shadow-sm">
                        <CheckCircle2 className="w-4 h-4" />
                      </div>
                    )}

                    {isInProgress && (
                      <div className="w-6 h-6 rounded-full border-4 border-blue-600 bg-white flex items-center justify-center shadow-sm">
                        <div className="w-2 h-2 rounded-full bg-blue-600"></div>
                      </div>
                    )}

                    {isLocked && (
                      <div className="w-6 h-6 rounded-full border-2 border-slate-300 bg-slate-100 text-slate-400 flex items-center justify-center">
                        <Lock className="w-3 h-3" />
                      </div>
                    )}
                  </div>

                  {/* Milestone Content Box */}
                  <div className="space-y-1">
                    <h3 className={`font-extrabold text-sm ${isInProgress ? 'text-blue-700' : 'text-slate-900'}`}>
                      {ms.title}
                    </h3>
                    <p className="text-xs text-slate-500 font-medium">{ms.subtitle}</p>

                    <div className="pt-1">
                      <span className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-extrabold font-mono ${
                        isCompleted
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : isInProgress
                          ? 'bg-blue-50 text-blue-700 border border-blue-200'
                          : 'bg-slate-100 text-slate-500 border border-slate-200'
                      }`}>
                        {ms.date}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Side Drawer / AI Assistant Panel (Matching Image 2 Right Side) */}
        <div className="space-y-6">
          <div className="scout-card p-6 space-y-4 bg-slate-50 border-slate-200">
            <div className="flex items-center space-x-2 text-blue-700 font-extrabold text-xs">
              <Sparkles className="w-4 h-4 text-blue-600" />
              <span>Spheria AI Roadmap Tips</span>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed font-medium">
              Completing <strong className="text-slate-900">System Design Interview Prep</strong> will increase your eligibility for Senior roles by 42%.
            </p>

            <button className="scout-btn-primary text-xs w-full py-2">
              <span>Start System Design Module</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="scout-card p-6 space-y-4">
            <div className="flex items-center space-x-2 text-slate-800 font-extrabold text-xs">
              <AlertCircle className="w-4 h-4 text-amber-500" />
              <span>Skill Gap Nudge</span>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed font-medium">
              You are missing 1 core requirement for your target role: <strong className="text-slate-900">Docker & Kubernetes</strong>.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
