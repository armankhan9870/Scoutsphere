import React, { useState, useEffect } from 'react';
import {
  LayoutGrid,
  Briefcase,
  Map,
  Target,
  Sparkles,
  HelpCircle,
  Settings as SettingsIcon,
  MessageSquare,
  Search,
  User,
} from 'lucide-react';

import { LandingPage } from './components/LandingPage';
import { DashboardOverview } from './components/DashboardOverview';
import { OpportunitiesBrowse } from './components/OpportunitiesBrowse';
import { ResumeTailoringWorkspace } from './components/ResumeTailoringWorkspace';
import { ApplicationTracker } from './components/ApplicationTracker';
import { SkillGapLearning } from './components/SkillGapLearning';
import { RoadmapView } from './components/RoadmapView';
import { CareerChatbot } from './components/CareerChatbot';
import { SettingsView } from './components/SettingsView';
import { ProfileSetupWizard } from './components/ProfileSetupWizard';
import { AuthModal } from './components/AuthModal';
import { ProtectedRoute } from './components/ProtectedRoute';
import { ApplicationCoPilot } from './components/ApplicationCoPilot';
import { useAuth } from './context/AuthContext';


export const App: React.FC = () => {
  const { user, logout } = useAuth();
  const [viewMode, setViewMode] = useState<'app' | 'landing'>('landing');

  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [selectedOpp, setSelectedOpp] = useState<any | null>(null);
  const [showChatbotModal, setShowChatbotModal] = useState<boolean>(false);
  const [showAuthModal, setShowAuthModal] = useState<boolean>(false);

  // Automatically take user to dashboard app view whenever authenticated
  useEffect(() => {
    if (user) {
      setViewMode('app');
      setActiveTab('dashboard');
    }
  }, [user]);

  const handleSelectOpportunity = (opp: any) => {
    setSelectedOpp(opp);
  };

  const handleAuthSuccess = () => {
    setShowAuthModal(false);
    setViewMode('app');
    setActiveTab('dashboard');
  };

  if (viewMode === 'landing') {
    return (
      <>
        <LandingPage
          onGetStarted={() => {
            if (user) {
              setViewMode('app');
              setActiveTab('dashboard');
            } else {
              setShowAuthModal(true);
            }
          }}
          onOpenAuth={() => setShowAuthModal(true)}
        />
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          onSuccess={handleAuthSuccess}
        />
      </>
    );
  }

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-row font-sans text-slate-900 selection:bg-blue-500 selection:text-white">
      {/* Sidebar Navigation (Matching Reference Images 1, 2, 3) */}
      <aside className="scout-sidebar border-r border-slate-200/80 bg-white flex flex-col justify-between p-5 min-h-screen w-64 shrink-0 shadow-sm sticky top-0 h-screen z-30">
        <div className="space-y-6">
          {/* Brand Logo & Subtitle */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setViewMode('landing')}>
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-black text-sm shadow-md shadow-blue-500/30">
              🚀
            </div>
            <div>
              <span className="font-extrabold text-blue-700 text-lg tracking-tight block leading-none">ScoutSphere</span>
              <span className="text-[10px] text-slate-400 font-bold block mt-0.5">Career Assistant</span>
            </div>
          </div>

          {/* Top Sidebar Action Button (Matching Reference Screenshot) */}
          <button
            onClick={() => setActiveTab('resume-tailor')}
            className="w-full scout-btn-primary text-xs py-3 flex items-center justify-center space-x-2"
          >
            <Sparkles className="w-4 h-4" />
            <span>Optimize Resume</span>
          </button>

          {/* Navigation Menu List */}
          <nav className="space-y-1">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`w-full scout-nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            >
              <LayoutGrid className="w-4 h-4" />
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => setActiveTab('profile')}
              className={`w-full scout-nav-item ${activeTab === 'profile' ? 'active' : ''}`}
            >
              <User className="w-4 h-4" />
              <span>Profile</span>
            </button>

            <button
              onClick={() => setActiveTab('tracker')}
              className={`w-full scout-nav-item ${activeTab === 'tracker' ? 'active' : ''}`}
            >
              <Briefcase className="w-4 h-4" />
              <span>Application Tracker</span>
            </button>

            <button
              onClick={() => setActiveTab('copilot')}
              className={`w-full scout-nav-item ${activeTab === 'copilot' ? 'active' : ''}`}
            >
              <Sparkles className="w-4 h-4 text-indigo-500" />
              <span>App CoPilot</span>
            </button>

            <button
              onClick={() => setActiveTab('roadmap')}
              className={`w-full scout-nav-item ${activeTab === 'roadmap' ? 'active' : ''}`}
            >
              <Map className="w-4 h-4" />
              <span>Roadmap</span>
            </button>

            <button
              onClick={() => setActiveTab('skill-gap')}
              className={`w-full scout-nav-item ${activeTab === 'skill-gap' ? 'active' : ''}`}
            >
              <Target className="w-4 h-4" />
              <span>Skill Gap</span>
            </button>

            <button
              onClick={() => setActiveTab('opportunities')}
              className={`w-full scout-nav-item ${activeTab === 'opportunities' ? 'active' : ''}`}
            >
              <Search className="w-4 h-4" />
              <span>Opportunities</span>
            </button>
          </nav>
        </div>

        {/* Bottom Sidebar Footer Navigation */}
        <div className="space-y-1 border-t border-slate-100 pt-4">
          <button className="w-full scout-nav-item">
            <HelpCircle className="w-4 h-4" />
            <span>Help</span>
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`w-full scout-nav-item ${activeTab === 'settings' ? 'active' : ''}`}
          >
            <SettingsIcon className="w-4 h-4" />
            <span>Settings</span>
          </button>
        </div>
      </aside>

      {/* Main Container Right Side */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navigation Header Bar (Matching Reference Images) */}
        <header className="bg-white border-b border-slate-200/80 px-8 py-3.5 flex items-center justify-between sticky top-0 z-20 shadow-xs">
          {/* Center Header Links */}
          <nav className="flex items-center space-x-8 text-xs font-bold text-slate-600">
            <button onClick={() => setViewMode('landing')} className="text-primary font-bold hover:text-blue-700 transition flex items-center space-x-1">
              <span className="material-symbols-outlined text-sm">home</span>
              <span>Landing Page</span>
            </button>
            <button onClick={() => setActiveTab('opportunities')} className="hover:text-blue-600 transition">
              Discover
            </button>
            <button onClick={() => setActiveTab('skill-gap')} className="hover:text-blue-600 transition">
              Analyze
            </button>
            <button onClick={() => setActiveTab('dashboard')} className="hover:text-blue-600 transition">
              Match
            </button>
            <button onClick={() => setActiveTab('tracker')} className="hover:text-blue-600 transition">
              Application Tracker
            </button>
          </nav>


          {/* Right Header Controls */}
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowChatbotModal(!showChatbotModal)}
              className="px-4 py-2 rounded-xl bg-blue-50 hover:bg-blue-100 text-primary border border-blue-200 text-xs font-extrabold flex items-center space-x-2 transition shadow-2xs"
            >
              <MessageSquare className="w-4 h-4" />
              <span>AI Chat</span>
            </button>

            <button
              onClick={() => setActiveTab('settings')}
              className="p-2 rounded-xl border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition"
              title="Settings"
            >
              <SettingsIcon className="w-4 h-4" />
            </button>

            {user ? (
              <div className="flex items-center gap-2">
                <div
                  onClick={() => setActiveTab('profile')}
                  className="flex items-center gap-2 cursor-pointer p-1 rounded-xl hover:bg-slate-100 transition"
                  title="View Profile"
                >
                  <div className="w-8 h-8 rounded-full bg-indigo-600 text-white font-bold text-xs flex items-center justify-center shadow-xs overflow-hidden">
                    {user.avatar_url ? (
                      <img src={user.avatar_url} alt={user.full_name} className="w-full h-full object-cover" />
                    ) : (
                      user.full_name.charAt(0).toUpperCase()
                    )}
                  </div>
                  <span className="text-xs font-semibold text-slate-700 hidden sm:inline">{user.full_name}</span>
                </div>
                <button
                  onClick={async () => {
                    await logout();
                    setViewMode('landing');
                  }}
                  className="px-3 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-100 text-slate-600 hover:text-rose-600 text-xs font-semibold transition cursor-pointer"
                  title="Log Out"
                >
                  Log Out
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition shadow-md shadow-indigo-500/20 cursor-pointer"
              >
                Sign In
              </button>
            )}
          </div>
        </header>

        {/* View Workspace Content Area */}
        <main className="p-8 max-w-7xl mx-auto w-full flex-1">
          {activeTab === 'dashboard' && (
            <ProtectedRoute>
              <DashboardOverview onNavigateTab={setActiveTab} onSelectOpportunity={handleSelectOpportunity} />
            </ProtectedRoute>
          )}

          {activeTab === 'profile' && (
            <ProtectedRoute>
              <ProfileSetupWizard onNavigateTab={setActiveTab} />
            </ProtectedRoute>
          )}

          {activeTab === 'tracker' && (
            <ProtectedRoute>
              <ApplicationTracker />
            </ProtectedRoute>
          )}

          {activeTab === 'copilot' && (
            <ProtectedRoute>
              <ApplicationCoPilot onNavigateTab={setActiveTab} />
            </ProtectedRoute>
          )}

          {activeTab === 'roadmap' && (
            <ProtectedRoute>
              <RoadmapView />
            </ProtectedRoute>
          )}

          {activeTab === 'skill-gap' && (
            <ProtectedRoute>
              <SkillGapLearning opportunity={selectedOpp} />
            </ProtectedRoute>
          )}

          {activeTab === 'opportunities' && <OpportunitiesBrowse />}

          {activeTab === 'resume-tailor' && (
            <ProtectedRoute>
              <ResumeTailoringWorkspace />
            </ProtectedRoute>
          )}

          {activeTab === 'settings' && (
            <ProtectedRoute>
              <SettingsView />
            </ProtectedRoute>
          )}
        </main>
      </div>

      {/* Floating Chatbot Panel */}
      {showChatbotModal && (
        <div className="fixed bottom-6 right-6 z-50 w-[420px] max-w-[92vw] h-[580px] max-h-[85vh] shadow-2xl rounded-3xl border border-slate-200 overflow-hidden bg-white animate-fadeIn">
          <CareerChatbot onClose={() => setShowChatbotModal(false)} />
        </div>
      )}

      {/* Authentication Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={handleAuthSuccess}
      />
    </div>
  );
};

export default App;
