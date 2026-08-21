import React from 'react';
import { useAuth } from '../context/AuthContext';

interface LandingPageProps {
  onGetStarted: () => void;
  onOpenAuth?: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted, onOpenAuth }) => {
  const { user, logout } = useAuth();

  return (
    <div className="bg-background text-on-background font-sans min-h-screen flex flex-col antialiased">
      {/* TopNavBar Header */}
      <header className="bg-surface/80 backdrop-blur-md sticky top-0 w-full border-b border-outline-variant/20 shadow-sm z-50">
        <div className="flex justify-between items-center w-full px-6 max-w-container-max mx-auto h-16">
          <div className="flex items-center space-x-8">
            <button onClick={onGetStarted} className="text-2xl font-bold text-primary tracking-tight">
              ScoutSphere
            </button>
            <nav className="hidden md:flex items-center space-x-2">
              <button onClick={onGetStarted} className="text-on-surface-variant hover:text-primary transition-colors hover:bg-primary-container/10 px-3.5 py-2 rounded-lg font-medium text-sm">
                Discover
              </button>
              <button onClick={onGetStarted} className="text-on-surface-variant hover:text-primary transition-colors hover:bg-primary-container/10 px-3.5 py-2 rounded-lg font-medium text-sm">
                Analyze
              </button>
              <button onClick={onGetStarted} className="text-on-surface-variant hover:text-primary transition-colors hover:bg-primary-container/10 px-3.5 py-2 rounded-lg font-medium text-sm">
                Match
              </button>
              <button onClick={onGetStarted} className="text-on-surface-variant hover:text-primary transition-colors hover:bg-primary-container/10 px-3.5 py-2 rounded-lg font-medium text-sm">
                Track
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
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuAuSueEMHL1KVrpaiFdPeXUNhidP_7LX3ELxAJKrsZFjhSztQkFSbLIXKx3RNFFJD5wY11bH_jsvHzAzWleDn3BmHu9S3eqss-7P3Zjk_vu-GL-uJqT-Dp8-fxvNW5ZowallHBqo6iATv367U-bERjl7WqZfmXZ_aPqNbWyRKP_YSx8E8P3mSknW46G-VhA-rbedpK66dA8WoFuDTHUJnjGDSVoxC6RLIFKzCKZFDWP-1ZjKUZKHfHu"
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
        <section className="py-20 bg-surface">
          <div className="max-w-container-max mx-auto px-4 md:px-8 space-y-16">
            <div className="text-center max-w-2xl mx-auto space-y-3">
              <h2 className="text-3xl md:text-4xl font-bold text-on-surface tracking-tight">Intelligent Career Engineering</h2>
              <p className="text-base text-on-surface-variant leading-relaxed">
                We leverage advanced models to optimize every touchpoint of your job search and career trajectory.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[250px]">
              {/* Feature 1: Large Span */}
              <div className="md:col-span-2 glass-panel rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden group hover:shadow-xl transition-all duration-300 border border-white/80">
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
              <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between group hover:-translate-y-1 transition-transform border border-white/80 shadow-sm">
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
              <div className="glass-panel rounded-2xl p-6 flex flex-col space-y-3 group hover:-translate-y-1 transition-transform border border-white/80 shadow-sm">
                <span className="material-symbols-outlined text-tertiary p-2 bg-tertiary-container/20 rounded-xl w-fit inline-block text-2xl">psychology</span>
                <h3 className="text-xl font-bold text-on-surface">Skill Gap Analysis</h3>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  Identify exactly what technical or soft skills are missing between your current profile and your dream role.
                </p>
              </div>

              {/* Feature 4: Large Span */}
              <div className="md:col-span-2 glass-panel rounded-2xl p-6 flex items-center justify-between relative overflow-hidden group border border-white/80 shadow-sm">
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
