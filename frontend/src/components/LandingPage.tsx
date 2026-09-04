import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

interface LandingPageProps {
  onGetStarted: () => void;
  onOpenAuth?: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted, onOpenAuth }) => {
  const { user, logout } = useAuth();
  const [activeStep, setActiveStep] = useState(1);

  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStep((prev) => (prev >= 4 ? 1 : prev + 1));
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="bg-background text-on-background font-sans min-h-screen flex flex-col antialiased">
      {/* TopNavBar Header */}
      <header className="bg-surface/80 backdrop-blur-md sticky top-0 w-full border-b border-outline-variant/20 shadow-sm z-50">
        <div className="flex justify-between items-center w-full px-6 max-w-container-max mx-auto h-16">
          <div className="flex items-center space-x-8">
            <button onClick={onGetStarted} className="flex items-center space-x-2 text-2xl font-bold text-primary tracking-tight">
              <span className="material-symbols-outlined text-3xl">explore</span>
              <span>ScoutSphere</span>
            </button>
            <nav className="hidden md:flex items-center space-x-2">
              <button onClick={() => document.getElementById('section-features')?.scrollIntoView({ behavior: 'smooth' })} className="text-on-surface-variant hover:text-primary transition-colors hover:bg-primary-container/10 px-3.5 py-2 rounded-lg font-medium text-sm">
                Features
              </button>
              <button onClick={() => document.getElementById('section-how-it-works')?.scrollIntoView({ behavior: 'smooth' })} className="text-on-surface-variant hover:text-primary transition-colors hover:bg-primary-container/10 px-3.5 py-2 rounded-lg font-medium text-sm">
                Process
              </button>
              <button onClick={() => document.getElementById('section-audience')?.scrollIntoView({ behavior: 'smooth' })} className="text-on-surface-variant hover:text-primary transition-colors hover:bg-primary-container/10 px-3.5 py-2 rounded-lg font-medium text-sm">
                Audience
              </button>
            </nav>
          </div>

          {/* Mobile Menu Button */}
          <button onClick={onGetStarted} className="md:hidden text-on-surface p-2">
            <span className="material-symbols-outlined">menu</span>
          </button>

          {/* Trailing Actions (Desktop) */}
          <div className="hidden md:flex items-center space-x-3">
            {user ? (
              <div className="flex items-center space-x-3">
                <span className="text-xs font-semibold text-slate-700 bg-slate-100 border border-slate-200 px-3.5 py-1.5 rounded-full">
                  User: <strong className="text-blue-700 font-bold">{user.full_name || user.email}</strong>
                </span>
                <button onClick={onGetStarted} className="px-4 py-2 font-semibold text-xs text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition">
                  Go to Dashboard
                </button>
                <button onClick={logout} className="px-3 py-2 font-medium text-xs text-rose-600 bg-rose-50 hover:bg-rose-100 rounded-lg transition">
                  Log Out
                </button>
              </div>
            ) : (
              <>
                <button onClick={onOpenAuth || onGetStarted} className="px-4 py-2 font-medium text-sm text-primary bg-primary/10 hover:bg-primary/20 rounded-lg transition-colors">
                  Log In
                </button>
                <button onClick={onOpenAuth || onGetStarted} className="px-5 py-2 font-medium text-sm text-on-primary bg-primary hover:bg-primary/90 rounded-lg shadow-sm transition-all hover:scale-95 duration-150">
                  Sign Up
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow">
        {/* Hero Section */}
        <section className="relative pt-16 pb-24 md:pt-20 md:pb-28 overflow-hidden hero-gradient">
          <div className="max-w-container-max mx-auto px-4 md:px-8 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center relative z-10">
            {/* Hero Content (Left 6 Cols) */}
            <div className="lg:col-span-6 flex flex-col items-start space-y-6">
              <div className="inline-flex items-center space-x-2 bg-secondary-container/40 border border-secondary-fixed-dim/60 px-3.5 py-1.5 rounded-full">
                <span className="material-symbols-outlined text-secondary text-base">auto_awesome</span>
                <span className="text-xs font-semibold text-secondary tracking-wide">AI-Powered Career Intelligence</span>
              </div>

              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-on-surface tracking-tight leading-[1.15]">
                Your Career, <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-blue-600 to-secondary">
                  Autonomously Discovered.
                </span>
              </h1>

              <p className="text-base md:text-lg text-on-surface-variant max-w-xl leading-relaxed font-normal">
                The AI career assistant that finds, analyzes, and applies to opportunities for you. Stop searching and start advancing with data-driven professional growth.
              </p>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-3 sm:space-y-0 sm:space-x-4 pt-2 w-full sm:w-auto">
                <button onClick={onGetStarted} className="bg-primary text-on-primary font-semibold text-sm px-6 py-3.5 rounded-xl shadow-md hover:shadow-xl hover:bg-primary/90 transition-all duration-200 flex items-center justify-center space-x-2 active:scale-95">
                  <span>Get Started for Free</span>
                  <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </button>
                <button onClick={onGetStarted} className="glass-panel text-primary font-semibold text-sm px-6 py-3.5 rounded-xl hover:bg-surface-variant/60 transition-all duration-200 flex items-center justify-center space-x-2 active:scale-95">
                  <span className="material-symbols-outlined text-base">play_circle</span>
                  <span>Watch Demo</span>
                </button>
              </div>
            </div>

            {/* Hero Visual (Right 6 Cols with Absolute Floating Glass Cards) */}
            <div className="lg:col-span-6 relative w-full h-[480px] md:h-[520px] flex items-center justify-start">
              {/* Blur Glow Background */}
              <div className="absolute inset-0 bg-primary/10 rounded-full blur-3xl opacity-60"></div>

              {/* Main Image Card */}
              <div className="w-[82%] h-[440px] md:h-[480px] glass-panel rounded-2xl overflow-hidden relative shadow-2xl border border-white/80">
                <img
                  className="w-full h-full object-cover object-top"
                  alt="A professional woman reviewing an interactive holographic career dashboard"
                  src="/hero_dashboard.jpg"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-slate-950/20 to-transparent"></div>
                <div className="absolute bottom-5 left-5 right-5 text-white space-y-1">
                  <div className="flex items-center space-x-1.5 mb-1">
                    <span className="material-symbols-outlined text-emerald-400 text-base">check_circle</span>
                    <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">Match Found</span>
                  </div>
                  <p className="text-xl font-bold text-white leading-snug">Senior Product Designer</p>
                  <p className="text-xs text-white/80 font-medium">98% Skill Alignment</p>
                </div>
              </div>

              {/* Stats Card 1 (Floating Top Right - Fully Contained Padding) */}
              <div className="hidden sm:flex absolute top-4 right-0 z-20 glass-panel rounded-2xl p-4 shadow-xl border border-white/90 flex-col items-center justify-center text-center min-w-[160px] animate-fadeIn">
                <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center mb-2">
                  <span className="material-symbols-outlined text-primary text-2xl">trending_up</span>
                </div>
                <h3 className="text-2xl font-bold text-on-surface leading-none mb-1">3x</h3>
                <p className="text-xs font-medium text-on-surface-variant">Interview Rate</p>
              </div>

              {/* Mini Chart Card (Floating Bottom Right - Generous Clean Container) */}
              <div className="hidden sm:flex absolute bottom-4 right-2 z-30 glass-panel rounded-2xl p-5 shadow-2xl border border-white/90 flex-col w-[260px] space-y-3 animate-fadeIn">
                <h4 className="text-xs font-bold text-on-surface tracking-wide uppercase">Skill Gap Analysis</h4>
                <div className="space-y-3 w-full">
                  <div>
                    <div className="flex justify-between text-xs font-semibold text-on-surface-variant mb-1">
                      <span>Figma</span>
                      <span className="text-tertiary font-bold">95%</span>
                    </div>
                    <div className="w-full bg-slate-200/80 rounded-full h-2 overflow-hidden">
                      <div className="bg-tertiary h-full rounded-full transition-all" style={{ width: '95%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs font-semibold text-on-surface-variant mb-1">
                      <span>Prototyping</span>
                      <span className="text-secondary font-bold">80%</span>
                    </div>
                    <div className="w-full bg-slate-200/80 rounded-full h-2 overflow-hidden">
                      <div className="bg-secondary h-full rounded-full transition-all" style={{ width: '80%' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section (Bento Grid) */}
        <section id="section-features" className="py-20 bg-surface">
          <div className="max-w-container-max mx-auto px-4 md:px-8 space-y-16">
            <div className="text-center max-w-2xl mx-auto space-y-3">
              <h2 className="text-3xl md:text-4xl font-bold text-on-surface tracking-tight">Intelligent Career Engineering</h2>
              <p className="text-base text-on-surface-variant leading-relaxed">
                We leverage advanced models to optimize every touchpoint of your job search and career trajectory.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[250px]">
              {/* Feature 1: Large Span */}
              <div id="feature-discover" className="md:col-span-2 glass-panel rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden group hover:shadow-xl transition-all duration-300 border border-white/80">
                <div className="z-10 w-full md:w-2/3 space-y-2">
                  <span className="material-symbols-outlined text-primary mb-2 p-2 bg-primary-container/20 rounded-xl inline-block text-2xl">search_insights</span>
                  <h3 className="text-2xl font-bold text-on-surface">Automated Discovery</h3>
                  <p className="text-sm text-on-surface-variant leading-relaxed">
                    Our AI constantly scans the market, identifying unlisted and highly-relevant roles based on your dynamic profile.
                  </p>
                </div>
                <div className="absolute -bottom-10 -right-10 w-64 h-64 bg-primary/10 rounded-full blur-2xl group-hover:bg-primary/20 transition-all"></div>
                <img
                  className="absolute top-1/2 -translate-y-1/2 right-4 w-48 h-48 object-contain opacity-80 mix-blend-multiply hidden md:block"
                  alt="Data visualization nodes"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuDUslFgGbEBuJzWju4fYmexGynZl24-dCBl5d94DxCHG-9zgms_d4Y7E06bswZHTsUmfp-8zFmOJJ2_Zxt9rIo2JjrcLRxxulaJtRHIBc4sBfxW1T9aK-KQ33TVkJizUYcGtV5xIDTSoFmHg7HViUwBCwF430De0pJrOi0bkLULA1Dj_kKizTFWjIpPe4VN5TmmEI71hvwVmMliH4tejRhOzozvz0K6s44VbBSxEyMuz8z9xLvCJwZn"
                />
              </div>

              {/* Feature 2 */}
              <div id="feature-match" className="glass-panel rounded-2xl p-6 flex flex-col justify-between group hover:-translate-y-1 transition-transform border border-white/80 shadow-sm">
                <div className="space-y-2">
                  <span className="material-symbols-outlined text-secondary mb-2 p-2 bg-secondary-container/20 rounded-xl inline-block text-2xl">document_scanner</span>
                  <h3 className="text-xl font-bold text-on-surface">ATS-Friendly Tailoring</h3>
                  <p className="text-xs text-on-surface-variant leading-relaxed">
                    Instantly adapt your resume keywords and phrasing to match specific job descriptions seamlessly.
                  </p>
                </div>
                <div className="mt-4 h-14 w-full rounded-xl bg-gradient-to-r from-surface-variant to-surface relative overflow-hidden border border-outline-variant/30 flex items-center px-4">
                  <div className="flex items-center space-x-2 text-secondary font-bold text-xs">
                    <span className="material-symbols-outlined text-secondary text-base">check_circle</span>
                    <span>100% ATS Keyword Pass Rate</span>
                  </div>
                </div>
              </div>

              {/* Feature 3 */}
              <div id="feature-analyze" className="glass-panel rounded-2xl p-6 flex flex-col space-y-3 group hover:-translate-y-1 transition-transform border border-white/80 shadow-sm">
                <span className="material-symbols-outlined text-tertiary p-2 bg-tertiary-container/20 rounded-xl w-fit inline-block text-2xl">psychology</span>
                <h3 className="text-xl font-bold text-on-surface">Skill Gap Analysis</h3>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  Identify exactly what technical or soft skills are missing between your current profile and your dream role.
                </p>
              </div>

              {/* Feature 4: Large Span */}
              <div id="feature-track" className="md:col-span-2 glass-panel rounded-2xl p-6 flex items-center justify-between relative overflow-hidden group border border-white/80 shadow-sm">
                <div className="flex-1 z-10 space-y-2">
                  <span className="material-symbols-outlined text-primary mb-2 p-2 bg-primary-container/20 rounded-xl inline-block text-2xl">map</span>
                  <h3 className="text-2xl font-bold text-on-surface">Interactive Roadmaps</h3>
                  <p className="text-sm text-on-surface-variant leading-relaxed">
                    Visualize your 5-year trajectory with actionable, step-by-step guidance generated by industry-specific AI models.
                  </p>
                </div>
                <div className="hidden md:flex flex-1 justify-end items-center">
                  <div className="w-full max-w-[200px] space-y-4 bg-white/60 p-4 rounded-xl border border-slate-200/60 shadow-sm">
                    <div className="flex items-center space-x-3">
                      <div className="w-3.5 h-3.5 rounded-full bg-primary ring-4 ring-primary/20"></div>
                      <div className="h-2 w-full bg-slate-200 rounded-full"><div className="h-full bg-primary rounded-full w-full"></div></div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="w-3.5 h-3.5 rounded-full bg-tertiary"></div>
                      <div className="h-2 w-full bg-slate-200 rounded-full"><div className="h-full bg-tertiary rounded-full w-1/2"></div></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section id="section-how-it-works" className="py-24 bg-surface-container-low relative overflow-hidden">
          <div className="max-w-container-max mx-auto px-4 md:px-8 relative z-10">
            <h2 className="text-3xl md:text-4xl font-bold text-on-surface tracking-tight mb-16">How it works</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-8 items-center">
              {/* Left Column: Vertical Timeline */}
              <div className="relative pl-8 space-y-12 before:absolute before:inset-y-0 before:left-[15px] before:w-[2px] before:bg-outline-variant/30">
                
                {[
                  {
                    step: 1,
                    title: 'Build Profile',
                    desc: 'Upload your resume and let AI extract your core skills, past experiences, and future career goals instantly.'
                  },
                  {
                    step: 2,
                    title: 'Intelligent Matching',
                    desc: "ScoutSphere's agents scan thousands of live job boards to find high-probability matches tailored exactly to your unique profile."
                  },
                  {
                    step: 3,
                    title: 'Automated Optimization',
                    desc: 'We automatically rewrite and tailor your resume keywords for each specific job description to beat the ATS every time.'
                  },
                  {
                    step: 4,
                    title: 'Apply & Track',
                    desc: 'Manage all your applications in a smart kanban board, complete with interview preparation roadmaps and skill gap learning.'
                  }
                ].map((item) => (
                  <div 
                    key={item.step}
                    className={`relative cursor-pointer transition-all duration-300 ${activeStep === item.step ? 'opacity-100 scale-105' : 'opacity-50 hover:opacity-80'}`}
                    onClick={() => setActiveStep(item.step)}
                  >
                    <div className={`absolute -left-[39px] top-0 w-8 h-8 rounded-full border-2 flex items-center justify-center font-bold text-sm z-10 transition-colors duration-300 ${activeStep === item.step ? 'bg-primary/20 border-primary text-primary shadow-[0_0_15px_rgba(59,130,246,0.5)] bg-surface' : 'bg-surface border-outline-variant text-on-surface-variant'}`}>
                      {item.step}
                    </div>
                    <h3 className="text-xl font-bold text-on-surface mb-2">{item.title}</h3>
                    <p className="text-sm text-on-surface-variant leading-relaxed">
                      {item.desc}
                    </p>
                  </div>
                ))}
              </div>

              {/* Right Column: Visual Node Graph representation */}
              <div className="hidden lg:flex justify-center items-center h-[450px] relative w-full">
                {/* Central AI Node */}
                <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-24 h-24 bg-surface rounded-3xl border transition-all duration-500 flex items-center justify-center ${activeStep > 0 ? 'border-primary/80 shadow-[0_0_30px_rgba(59,130,246,0.4)]' : 'border-outline-variant/30'}`}>
                  <span className={`material-symbols-outlined text-5xl text-primary transition-all duration-500 ${activeStep > 0 ? 'animate-pulse' : ''}`}>smart_toy</span>
                </div>
                
                {/* Connection Lines (SVG) */}
                <svg className="absolute inset-0 w-full h-full z-10" pointerEvents="none">
                  {/* Outer Pipeline Flow (The Process) */}
                  {/* 1 to 2 */}
                  <line x1="25%" y1="20%" x2="75%" y2="20%" stroke={activeStep >= 2 ? 'rgba(59,130,246,0.8)' : 'var(--color-outline-variant)'} strokeWidth={activeStep === 2 ? "3" : "2"} strokeDasharray={activeStep >= 2 ? "none" : "6,6"} className={`transition-all duration-500 ${activeStep >= 2 ? 'opacity-100' : 'opacity-20'}`} />
                  {/* 2 to 3 */}
                  <line x1="75%" y1="20%" x2="75%" y2="80%" stroke={activeStep >= 3 ? 'rgba(59,130,246,0.8)' : 'var(--color-outline-variant)'} strokeWidth={activeStep === 3 ? "3" : "2"} strokeDasharray={activeStep >= 3 ? "none" : "6,6"} className={`transition-all duration-500 ${activeStep >= 3 ? 'opacity-100' : 'opacity-20'}`} />
                  {/* 3 to 4 */}
                  <line x1="75%" y1="80%" x2="25%" y2="80%" stroke={activeStep >= 4 ? 'rgba(59,130,246,0.8)' : 'var(--color-outline-variant)'} strokeWidth={activeStep === 4 ? "3" : "2"} strokeDasharray={activeStep >= 4 ? "none" : "6,6"} className={`transition-all duration-500 ${activeStep >= 4 ? 'opacity-100' : 'opacity-20'}`} />

                  {/* AI Center Connections (Supervision) */}
                  <line x1="50%" y1="50%" x2="25%" y2="20%" stroke="rgba(59,130,246,0.5)" strokeWidth="2" strokeDasharray="4,4" className={`transition-all duration-500 ${activeStep === 1 ? 'opacity-100' : 'opacity-10'}`} />
                  <line x1="50%" y1="50%" x2="75%" y2="20%" stroke="rgba(59,130,246,0.5)" strokeWidth="2" strokeDasharray="4,4" className={`transition-all duration-500 ${activeStep === 2 ? 'opacity-100' : 'opacity-10'}`} />
                  <line x1="50%" y1="50%" x2="75%" y2="80%" stroke="rgba(59,130,246,0.5)" strokeWidth="2" strokeDasharray="4,4" className={`transition-all duration-500 ${activeStep === 3 ? 'opacity-100' : 'opacity-10'}`} />
                  <line x1="50%" y1="50%" x2="25%" y2="80%" stroke="rgba(59,130,246,0.5)" strokeWidth="2" strokeDasharray="4,4" className={`transition-all duration-500 ${activeStep === 4 ? 'opacity-100' : 'opacity-10'}`} />
                </svg>

                {/* Surrounding Nodes in a Pipeline (C-Shape) */}
                {/* Node 1 (Top Left) */}
                <div className={`absolute top-[20%] left-[25%] -translate-x-1/2 -translate-y-1/2 z-20 glass-panel px-4 py-2 rounded-xl flex items-center space-x-2 border transition-all duration-500 ${activeStep === 1 ? 'border-primary shadow-[0_0_15px_rgba(59,130,246,0.4)] scale-110 opacity-100 bg-surface' : activeStep > 1 ? 'border-primary/50 shadow-sm opacity-100 bg-surface' : 'border-outline-variant/40 shadow-sm opacity-50 scale-100 bg-surface/50'}`}>
                  <span className={`material-symbols-outlined text-sm ${activeStep >= 1 ? 'text-primary' : 'text-secondary'}`}>description</span>
                  <span className="text-xs font-bold text-on-surface">Base Resume</span>
                </div>

                {/* Node 2 (Top Right) */}
                <div className={`absolute top-[20%] left-[75%] -translate-x-1/2 -translate-y-1/2 z-20 glass-panel px-4 py-2 rounded-xl flex items-center space-x-2 border transition-all duration-500 ${activeStep === 2 ? 'border-primary shadow-[0_0_15px_rgba(59,130,246,0.4)] scale-110 opacity-100 bg-surface' : activeStep > 2 ? 'border-primary/50 shadow-sm opacity-100 bg-surface' : 'border-outline-variant/40 shadow-sm opacity-50 scale-100 bg-surface/50'}`}>
                  <span className={`material-symbols-outlined text-sm ${activeStep >= 2 ? 'text-primary' : 'text-tertiary'}`}>radar</span>
                  <span className="text-xs font-bold text-on-surface">Market Scan</span>
                </div>

                {/* Node 3 (Bottom Right) */}
                <div className={`absolute top-[80%] left-[75%] -translate-x-1/2 -translate-y-1/2 z-20 glass-panel px-4 py-2 rounded-xl flex items-center space-x-2 border transition-all duration-500 ${activeStep === 3 ? 'border-primary shadow-[0_0_15px_rgba(59,130,246,0.4)] scale-110 opacity-100 bg-surface' : activeStep > 3 ? 'border-primary/50 shadow-sm opacity-100 bg-surface' : 'border-outline-variant/40 shadow-sm opacity-50 scale-100 bg-surface/50'}`}>
                  <span className={`material-symbols-outlined text-sm ${activeStep >= 3 ? 'text-primary' : 'text-emerald-500'}`}>tune</span>
                  <span className="text-xs font-bold text-on-surface">ATS Tailoring</span>
                </div>

                {/* Node 4 (Bottom Left) */}
                <div className={`absolute top-[80%] left-[25%] -translate-x-1/2 -translate-y-1/2 z-20 backdrop-blur-md px-5 py-3 rounded-xl flex flex-col items-center justify-center border transition-all duration-500 ${activeStep === 4 ? 'bg-primary/10 border-primary shadow-[0_0_25px_rgba(59,130,246,0.5)] scale-110 opacity-100' : 'bg-primary/5 border-primary/30 shadow-sm opacity-50 scale-100'}`}>
                  <span className="text-[10px] text-primary font-bold uppercase tracking-wider mb-1">Final Output</span>
                  <span className="text-sm font-bold text-on-surface">Matched App</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Who Can Benefit Section */}
        <section id="section-audience" className="py-20 bg-surface">
          <div className="max-w-container-max mx-auto px-4 md:px-8 space-y-16">
            <div className="text-center max-w-2xl mx-auto space-y-3">
              <h2 className="text-3xl md:text-4xl font-bold text-on-surface tracking-tight">Built for Your Journey</h2>
              <p className="text-base text-on-surface-variant leading-relaxed">
                Whether you're starting out or stepping up, ScoutSphere adapts to your specific career stage.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Audience 1 */}
              <div className="border border-outline-variant/30 bg-surface-container hover:bg-surface-container-high transition-colors p-8 rounded-3xl flex flex-col items-center text-center space-y-4 group shadow-sm">
                <span className="material-symbols-outlined text-4xl text-primary group-hover:scale-110 transition-transform">school</span>
                <h3 className="text-xl font-bold text-on-surface">Students & Grads</h3>
                <p className="text-sm text-on-surface-variant">Find hidden internships, understand what skills you're missing, and land your first role with confidence.</p>
              </div>
              {/* Audience 2 */}
              <div className="border border-outline-variant/30 bg-surface-container hover:bg-surface-container-high transition-colors p-8 rounded-3xl flex flex-col items-center text-center space-y-4 group shadow-sm">
                <span className="material-symbols-outlined text-4xl text-secondary group-hover:scale-110 transition-transform">published_with_changes</span>
                <h3 className="text-xl font-bold text-on-surface">Career Switchers</h3>
                <p className="text-sm text-on-surface-variant">Translate your past experiences into the right keywords for a completely new industry.</p>
              </div>
              {/* Audience 3 */}
              <div className="border border-outline-variant/30 bg-surface-container hover:bg-surface-container-high transition-colors p-8 rounded-3xl flex flex-col items-center text-center space-y-4 group shadow-sm">
                <span className="material-symbols-outlined text-4xl text-tertiary group-hover:scale-110 transition-transform">work</span>
                <h3 className="text-xl font-bold text-on-surface">Tech Professionals</h3>
                <p className="text-sm text-on-surface-variant">Let the AI passively hunt for senior roles that match your exact salary and culture requirements.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA Section */}
        <section className="py-24 relative overflow-hidden bg-primary text-on-primary">
          <div className="absolute inset-0 bg-white/5 bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:20px_20px] opacity-20"></div>
          <div className="max-w-4xl mx-auto px-4 relative z-10 text-center space-y-8">
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-white">Ready to let AI drive your career?</h2>
            <p className="text-lg text-white/80 max-w-2xl mx-auto font-medium">
              Join thousands of professionals who have automated their job search. Stop applying into the void and start landing interviews.
            </p>
            <button onClick={onGetStarted} className="bg-surface text-primary font-bold text-base px-8 py-4 rounded-xl shadow-2xl hover:scale-105 transition-transform duration-200 mt-4 flex items-center space-x-2 mx-auto">
              <span>Get Started for Free</span>
              <span className="material-symbols-outlined text-xl">arrow_forward</span>
            </button>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-surface-container-lowest py-8 border-t border-outline-variant/30">
        <div className="flex flex-col md:flex-row justify-between items-center px-6 max-w-container-max mx-auto gap-4">
          <div className="flex flex-col items-center md:items-start space-y-1">
            <span className="text-xl font-bold text-primary">ScoutSphere</span>
            <span className="text-xs text-on-surface-variant">© 2026 ScoutSphere AI. Empowering professional growth.</span>
          </div>
          <nav className="flex flex-wrap justify-center gap-6 text-xs font-medium">
            <a className="text-on-surface-variant hover:text-primary transition-opacity" href="#">Resources</a>
            <a className="text-on-surface-variant hover:text-primary transition-opacity" href="#">Privacy Policy</a>
            <a className="text-on-surface-variant hover:text-primary transition-opacity" href="#">Terms of Service</a>
            <a className="text-on-surface-variant hover:text-primary transition-opacity" href="#">API Docs</a>
          </nav>
        </div>
      </footer>
    </div>
  );
};
