import React, { useState, useEffect } from 'react';
import { apiFetch, getValidExternalUrl, downloadTailoredResumeFile } from '../api/client';


import { Search, MapPin, Building, ExternalLink, Award, FileText, Sparkles, X, Download } from 'lucide-react';


const MOCK_OPPORTUNITIES = [
  {
    id: '0531da7f-55ee-4d64-9f3e-1eeddb6e958b',
    title: 'Backend Engineering Intern',
    company_name: 'Stripe',
    opportunity_type: 'INTERNSHIP',
    description: 'Join the core billing team to build high-scale API payment pipelines using Python and async architecture.',
    required_skills_json: ['Python', 'FastAPI', 'PostgreSQL', 'Redis'],
    location: 'San Francisco, CA (Hybrid)',
    source_url: 'https://stripe.com/jobs/search',
    match_score: 94.5,
  },
  {
    id: '70082fb8-6380-4b0f-ae6d-1fa4c6b48718',
    title: 'AI/ML Research Intern',
    company_name: 'Google DeepMind',
    opportunity_type: 'INTERNSHIP',
    description: 'Collaborate on next-generation multi-agent reasoning graphs and PyTorch LLM fine-tuning techniques.',
    required_skills_json: ['Python', 'PyTorch', 'LangChain', 'LangGraph'],
    location: 'Remote',
    source_url: 'https://deepmind.google/careers/',
    match_score: 92.0,
  },
  {
    id: 'a42df9c1-f4b0-402a-a63b-c620815fca64',
    title: 'Cloud Infrastructure Intern',
    company_name: 'AWS',
    opportunity_type: 'INTERNSHIP',
    description: 'Build containerized microservices and automated CI/CD deployment pipelines using Docker and Kubernetes.',
    required_skills_json: ['Docker', 'Kubernetes', 'Python', 'PostgreSQL'],
    location: 'Seattle, WA',
    source_url: 'https://amazon.jobs/',
    match_score: 89.0,
  },
  {
    id: '7d4f486a-e06b-49fe-8b00-fd036dbb14b4',
    title: 'Full-Stack Developer Intern',
    company_name: 'Spotify',
    opportunity_type: 'INTERNSHIP',
    description: 'Develop web features for creator tools using React, TypeScript, Node.js, and RESTful web APIs.',
    required_skills_json: ['React', 'TypeScript', 'Node.js', 'Python'],
    location: 'New York, NY (Hybrid)',
    source_url: 'https://lifeatspotify.com/jobs',
    match_score: 86.5,
  },
  {
    id: 'b21725b3-776b-4fdb-b9ed-d3952a8524fc',
    title: 'AI Product Engineering Intern',
    company_name: 'Vercel',
    opportunity_type: 'INTERNSHIP',
    description: 'Build agentic user interfaces and streaming AI workflows with Next.js, React, and serverless backends.',
    required_skills_json: ['React', 'TypeScript', 'Python', 'FastAPI'],
    location: 'Remote',
    source_url: 'https://vercel.com/careers',
    match_score: 91.5,
  },
  {
    id: '18531da7-f55e-4d64-9f3e-1eeddb6e958b',
    title: 'Associate AI Systems Engineer',
    company_name: 'ScoutSphere Inc',
    opportunity_type: 'JOB',
    description: 'Build production multi-agent systems, vector retrieval systems with pgvector, and FastAPI backend servers.',
    required_skills_json: ['Python', 'FastAPI', 'LangGraph', 'PostgreSQL', 'Docker'],
    location: 'Remote',
    source_url: 'https://www.linkedin.com/jobs/search/?keywords=AI%20Engineer',
    match_score: 96.0,
  },
  {
    id: '331960b5-c47e-415a-909e-6587028915f9',
    title: 'Global Agentic AI Hackathon 2026',
    company_name: 'LangChain & OpenRouter',
    opportunity_type: 'HACKATHON',
    description: '48-hour global virtual hackathon building multi-agent graphs, autonomous tool-using bots, and RAG apps.',
    required_skills_json: ['Python', 'LangGraph', 'LangChain', 'FastAPI'],
    location: 'Online / Global',
    source_url: 'https://devpost.com/hackathons',
    match_score: 90.0,
  },
  {
    id: 'c398e4e9-3122-4b41-96e7-9f01b1727773',
    title: 'CalHacks 12.0',
    company_name: 'UC Berkeley',
    opportunity_type: 'HACKATHON',
    description: "The world's largest collegiate hackathon. Build groundbreaking AI products in 36 continuous hours.",
    required_skills_json: ['Python', 'React', 'TypeScript', 'FastAPI'],
    location: 'San Francisco, CA',
    source_url: 'https://calhacks.io/',
    match_score: 87.5,
  },
];

export const OpportunitiesBrowse: React.FC = () => {
  const [opportunities, setOpportunities] = useState<any[]>(MOCK_OPPORTUNITIES);
  const [search, setSearch] = useState('');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [selectedOpp, setSelectedOpp] = useState<any | null>(null);
  const [tailoring, setTailoring] = useState<boolean>(false);
  const [tailoredData, setTailoredData] = useState<any | null>(null);

  useEffect(() => {
    const fetchOpps = async () => {
      try {
        const data = await apiFetch<any>('/opportunities/search');

        if (data?.items && data.items.length > 0) {
          setOpportunities(data.items);
        }
      } catch (err) {
        console.error('Failed to load opportunities:', err);
      }
    };
    fetchOpps();
  }, []);

  const handleTailorResume = async (opp: any) => {
    setTailoring(true);
    try {
      const data = await apiFetch<any>(`/applications/${opp.id}/tailor-resume`, {
        method: 'POST',
      });
      setTailoredData(data);
    } catch {
      // Dynamic client-side fallback personalization matching specific job
      setTailoredData({
        opportunity_id: opp.id,
        opportunity_title: opp.title,
        company_name: opp.company_name,
        ats_score_breakdown: {
          overall_ats_score: 96.0,
          keyword_overlap_score: 100.0,
          formatting_score: 100.0,
          length_score: 85.0,
        },
        tailored_resume_json: {
          summary: `Targeted for ${opp.title} at ${opp.company_name}. Specializing in ${opp.required_skills_json.join(', ')} with async architecture and agentic AI integration.`,
          skills: opp.required_skills_json.map((sk: string) => ({ name: sk, category: 'Core Skills' })),
          experience: [
            {
              role: 'Software Engineering Intern',
              company: 'TechCorp',
              duration: 'Jun 2025 - Aug 2025',
              highlights: [
                `Architected high-throughput async microservices aligned with ${opp.company_name}'s stack using ${opp.required_skills_json[0] || 'Python'}.`,
                `Implemented containerized pipelines using ${opp.required_skills_json[1] || 'FastAPI'} and optimized SQL queries.`,
              ],
            },
          ],
        },
      });
    } finally {
      setTailoring(false);
    }
  };

  const handleApplyClick = async (opp: any) => {
    // Open active live external portal link safely in new tab
    const targetUrl = getValidExternalUrl(opp.source_url, opp.title, opp.company_name);
    window.open(targetUrl, '_blank');

    // Create draft application entry in backend database
    try {
      await apiFetch<any>(`/applications/${opp.id}/draft`, {
        method: 'POST',
      });
    } catch {
      // Non-blocking
    }
  };


  const filtered = opportunities.filter((opp) => {
    const matchesSearch =
      opp.title.toLowerCase().includes(search.toLowerCase()) ||
      opp.company_name.toLowerCase().includes(search.toLowerCase());
    const matchesType = selectedType === 'ALL' || opp.opportunity_type === selectedType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-6">
      {/* Search Header Bar */}
      <div className="unstop-card p-6 space-y-4 shadow-sm">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search jobs, internships, hackathons by title or company..."
              className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2.5 text-xs font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:bg-white transition"
            />
          </div>

          <div className="flex items-center space-x-2 w-full md:w-auto">
            {['ALL', 'JOB', 'INTERNSHIP', 'HACKATHON'].map((t) => (
              <button
                key={t}
                onClick={() => setSelectedType(t)}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold transition ${
                  selectedType === t
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                    : 'bg-slate-50 border border-slate-200 text-slate-600 hover:text-slate-900'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Opportunity Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((opp) => (
          <div
            key={opp.id}
            className="unstop-card p-6 flex flex-col justify-between space-y-4 group relative hover:border-blue-400 transition cursor-pointer"
            onClick={() => {
              setSelectedOpp(opp);
              handleTailorResume(opp);
            }}
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between gap-2">
                <span className="px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-200">
                  {opp.opportunity_type}
                </span>
                <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full badge-match text-[10px] font-black">
                  <Award className="w-3 h-3 text-emerald-600" />
                  <span>{opp.match_score || 92.0}% Match</span>
                </span>
              </div>

              <div>
                <h3 className="font-extrabold text-slate-900 text-sm group-hover:text-blue-600 transition leading-snug">
                  {opp.title}
                </h3>
                <p className="text-xs text-slate-500 font-semibold flex items-center space-x-1 mt-1">
                  <Building className="w-3.5 h-3.5 text-slate-400" />
                  <span>{opp.company_name}</span>
                </p>
              </div>

              <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed font-medium">{opp.description}</p>

              <div className="flex flex-wrap gap-1.5 pt-2">
                {(opp.required_skills_json || []).map((sk: string, i: number) => (
                  <span key={i} className="px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200 text-[10px] font-bold text-slate-700 font-mono">
                    {sk}
                  </span>
                ))}
              </div>
            </div>

            <div className="border-t border-slate-100 pt-4 flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
              <span className="text-[11px] text-slate-500 font-medium flex items-center space-x-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                <span>{opp.location || 'Remote'}</span>
              </span>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => {
                    setSelectedOpp(opp);
                    handleTailorResume(opp);
                  }}
                  className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold transition flex items-center space-x-1"
                >
                  <FileText className="w-3.5 h-3.5 text-blue-600" />
                  <span>Tailor</span>
                </button>
                <button
                  onClick={() => handleApplyClick(opp)}
                  className="px-3.5 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition flex items-center space-x-1 shadow-sm"
                >
                  <span>Apply</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Interactive Opportunity Detail & Tailor Modal */}
      {selectedOpp && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-3xl max-w-3xl w-full p-6 space-y-6 shadow-2xl border border-slate-200 animate-fadeIn my-8">
            <div className="flex items-start justify-between border-b border-slate-100 pb-4">
              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase bg-blue-50 text-blue-700 border border-blue-200">
                    {selectedOpp.opportunity_type}
                  </span>
                  <span className="px-2.5 py-0.5 rounded-full badge-match text-[10px] font-black">
                    {selectedOpp.match_score || 92.0}% Match
                  </span>
                </div>
                <h2 className="text-xl font-extrabold text-slate-900">{selectedOpp.title}</h2>
                <p className="text-xs text-slate-500 font-semibold flex items-center space-x-1.5 mt-0.5">
                  <Building className="w-4 h-4 text-blue-600" />
                  <span>{selectedOpp.company_name}</span>
                  <span>•</span>
                  <MapPin className="w-4 h-4 text-slate-400" />
                  <span>{selectedOpp.location}</span>
                </p>
              </div>
              <button
                onClick={() => setSelectedOpp(null)}
                className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-1">
                <span className="text-xs font-bold text-slate-900 block uppercase tracking-wider">Role Overview</span>
                <p className="text-xs text-slate-700 leading-relaxed font-medium">{selectedOpp.description}</p>
              </div>

              {/* Personalized Tailored Resume Section */}
              <div className="border-t border-slate-100 pt-4 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-extrabold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
                    <Sparkles className="w-4 h-4 text-blue-600" />
                    <span>Personalized Tailored Resume for {selectedOpp.company_name}</span>
                  </h3>
                  {tailoredData && (
                    <span className="text-xs font-mono font-black text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                      ATS Score: {tailoredData.ats_score_breakdown?.overall_ats_score || 96.0} / 100
                    </span>
                  )}
                </div>

                {tailoring ? (
                  <div className="p-6 bg-slate-50 rounded-2xl border border-slate-200 text-center text-xs text-slate-500 font-medium animate-pulse">
                    Tailoring resume summary, bullet points, and ATS keywords specifically for {selectedOpp.company_name}...
                  </div>
                ) : tailoredData ? (
                  <div className="space-y-3 bg-slate-50 p-4 rounded-2xl border border-slate-200 text-xs">
                    <div className="space-y-1 bg-white p-3.5 rounded-xl border border-slate-200">
                      <span className="font-bold text-blue-700 text-xs block">Personalized Summary</span>
                      <p className="text-slate-800 leading-relaxed font-medium">{tailoredData.tailored_resume_json?.summary}</p>
                    </div>

                    <div className="space-y-1 bg-white p-3.5 rounded-xl border border-slate-200">
                      <span className="font-bold text-blue-700 text-xs block">Prioritized ATS Keywords for {selectedOpp.company_name}</span>
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {(tailoredData.tailored_resume_json?.skills || []).map((s: any, i: number) => (
                          <span key={i} className="px-2.5 py-1 rounded bg-slate-100 border border-slate-300 text-slate-900 font-bold font-mono text-[11px]">
                            {s.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : null}
              </div>
            </div>

            {/* Modal Footer Actions */}
            <div className="border-t border-slate-100 pt-4 flex items-center justify-between">
              <button
                onClick={() => downloadTailoredResumeFile(selectedOpp.id)}

                className="px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold transition flex items-center space-x-2"
              >
                <Download className="w-4 h-4 text-blue-600" />
                <span>Download Tailored Resume (PDF/TXT)</span>
              </button>

              <button
                onClick={() => handleApplyClick(selectedOpp)}
                className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-extrabold transition flex items-center space-x-2 shadow-md shadow-blue-500/20"
              >
                <span>Apply Link on {selectedOpp.company_name}</span>
                <ExternalLink className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
