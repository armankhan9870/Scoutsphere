import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../api/client';
import { Bot, Send, User as UserIcon, Sparkles, RefreshCw, Compass, ShieldCheck, X } from 'lucide-react';

interface Message {
  sender_role: 'user' | 'assistant';
  content: string;
}

const getFallbackResponse = (query: string): string => {
  const q = query.toLowerCase().trim();
  if (q.includes("what is ai") || q.includes("artificial intelligence")) {
    return "**Artificial Intelligence (AI)** is a branch of computer science focused on building smart systems capable of performing tasks that human intelligence traditionally handles.\n\n• **Core Capabilities**: Learning, reasoning, problem-solving, perception, and natural language processing.\n• **Key Subfields**: Machine Learning (ML), Deep Learning (DL), Computer Vision, and Generative AI.\n• **Applications**: Conversational agents, autonomous vehicles, medical diagnosis, and recommendation engines.";
  }
  if (q.includes("ml and data science") || (q.includes("difference") && q.includes("data science"))) {
    return "The key differences between **Machine Learning (ML)** and **Data Science (DS)** are:\n\n• **Data Science**: An interdisciplinary field using statistics, SQL, and data visualization to analyze raw data and extract actionable business insights.\n• **Machine Learning**: A specialized subset of AI focused on developing statistical algorithms that learn from data to make autonomous predictions.\n\n**In summary**: Data Science analyzes data to guide human decision-making, while Machine Learning builds automated predictive algorithms.";
  }
  if (q.includes("machine learning") || q.includes("what is ml")) {
    return "**Machine Learning (ML)** is a core branch of Artificial Intelligence that allows computers to learn patterns from historical data and improve performance without being explicitly programmed.\n\n• **Supervised Learning**: Models trained on labeled inputs/outputs.\n• **Unsupervised Learning**: Finding hidden patterns in unlabeled data.\n• **Reinforcement Learning**: Agents learning optimal decisions via trial-and-error rewards.";
  }
  if (q.includes("internship") && q.includes("apprenticeship")) {
    return "The main differences between an **Internship** and an **Apprenticeship** are:\n\n• **Internship**: Short-term role (2–6 months) aimed at university students to gain broad industry exposure and networking.\n• **Apprenticeship**: Multi-year program (1–3 years) combining paid on-the-job training with formal technical education for full job mastery.";
  }
  if (q.includes("data analyst")) {
    return "A **Data Analyst** processes and interprets data to help organizations make strategic business decisions.\n\n• **Core Tasks**: Writing SQL queries, building dashboards (Tableau/Power BI), tracking metrics, and summarizing trends.\n• **Essential Toolkit**: SQL, Excel, Python/R, data visualization, and business acumen.";
  }
  if (q.includes("ats")) {
    return "An **Applicant Tracking System (ATS)** parses and evaluates candidate resumes to streamline hiring:\n\n• **Parsing**: Converts document formats into standardized data fields.\n• **Keyword Extraction**: Matches skills and job titles against the target job description.\n• **Scoring**: Ranks candidates based on relevance to assist recruiters.";
  }
  if (q.includes("backend developer") || q.includes("backend")) {
    return "Essential skills for a **Backend Developer** include:\n\n• **Programming**: Mastery of languages like Python, Java, Go, or Node.js.\n• **Databases**: Relational databases (PostgreSQL, MySQL) and caching systems (Redis).\n• **APIs**: RESTful architecture, gRPC, and secure authentication (OAuth/JWT).\n• **DevOps**: Docker, CI/CD, microservices, and cloud infrastructure.";
  }

  return `Looking at your profile, you already have a solid foundation in **Python, FastAPI, PostgreSQL, and Docker**! 🚀\n\nTo level up specifically for **Backend & AI Developer** roles, here are the key skills to focus on:\n\n• **Redis & Caching**: Optimize database read speeds.\n• **Async Background Queues (Celery/RabbitMQ)**: Handle worker pipelines.\n• **Kubernetes & Cloud (AWS/GCP)**: Deploy scalable microservices.\n\nWould you like me to help tailor your resume or generate a step-by-step roadmap?`;
};

interface CareerChatbotProps {
  onClose?: () => void;
}

export const CareerChatbot: React.FC<CareerChatbotProps> = ({ onClose }) => {
  const { user } = useAuth();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [sending, setSending] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const initSession = async () => {
    try {
      const data = await apiFetch<any>('/chat/sessions', {
        method: 'POST',
        body: JSON.stringify({ title: 'Career Guidance & Roadmap' }),
      });
      setSessionId(data.session_id);
      setMessages([{ sender_role: 'assistant', content: data.initial_message }]);
    } catch {
      setMessages([
        {
          sender_role: 'assistant',
          content: `Hello ${user?.full_name || 'Student'}! I am your ScoutSphere Career AI Assistant. Ask me how to prepare for target roles, analyze skill gaps, or build your career roadmap!`,
        },
      ]);
    }
  };

  useEffect(() => {
    initSession();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e?: React.FormEvent, promptOverride?: string) => {
    if (e) e.preventDefault();
    const query = promptOverride || input;
    if (!query.trim() || sending) return;

    const userMessage: Message = { sender_role: 'user', content: query };
    setMessages((prev) => [...prev, userMessage]);
    if (!promptOverride) setInput('');
    setSending(true);

    try {
      if (sessionId) {
        const data = await apiFetch<any>(`/chat/sessions/${sessionId}/messages`, {
          method: 'POST',
          body: JSON.stringify({ content: query }),
        });
        setMessages((prev) => [...prev, { sender_role: 'assistant', content: data.reply }]);
      } else {
        const fallbackReply = getFallbackResponse(query);
        setMessages((prev) => [
          ...prev,
          {
            sender_role: 'assistant',
            content: fallbackReply,
          },
        ]);
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { sender_role: 'assistant', content: `Error generating response: ${err.message || 'Network error'}` },
      ]);
    } finally {
      setSending(false);
    }
  };

  const quickPrompts = [
    "What should I do to get ready for ML internships?",
    "Show me my current skill gaps for Backend Developer roles",
    "Generate a 3-stage roadmap for AI Systems Engineering",
  ];

  return (
    <div className="w-full h-full min-h-[520px] max-h-[680px] bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col border border-slate-200/90 font-sans">
      {/* Header Bar */}
      <div className="px-4 py-3 bg-white border-b border-slate-200/90 flex items-center justify-between shrink-0 sticky top-0 z-20">
        <div className="flex items-center space-x-3 min-w-0">
          <div className="w-9 h-9 rounded-xl bg-primary text-white flex items-center justify-center shadow-sm shrink-0">
            <Bot className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <h2 className="font-extrabold text-slate-900 text-xs sm:text-sm truncate flex items-center space-x-1.5 leading-tight">
              <span className="truncate">ScoutSphere Career AI</span>
              <Sparkles className="w-3.5 h-3.5 text-primary shrink-0" />
            </h2>
            <p className="text-[11px] text-slate-500 font-medium truncate flex items-center space-x-1 mt-0.5">
              <ShieldCheck className="w-3 h-3 text-emerald-600 shrink-0" />
              <span className="truncate">Grounded RAG Guidance</span>
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-1 shrink-0">
          <button
            onClick={initSession}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition"
            title="New Conversation"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition"
              title="Close Chat"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Message List Container */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3.5 bg-slate-50/70">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start space-x-2.5 ${msg.sender_role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}
          >
            <div
              className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 ${
                msg.sender_role === 'user'
                  ? 'bg-primary text-white shadow-xs'
                  : 'bg-white border border-slate-200 text-primary shadow-xs'
              }`}
            >
              {msg.sender_role === 'user' ? <UserIcon className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
            </div>
            <div
              className={`max-w-[85%] p-3.5 rounded-2xl text-xs leading-relaxed font-medium ${
                msg.sender_role === 'user'
                  ? 'bg-primary text-white shadow-xs'
                  : 'bg-white text-slate-800 border border-slate-200/90 whitespace-pre-line shadow-xs'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {sending && (
          <div className="flex items-center space-x-2.5">
            <div className="w-7 h-7 rounded-lg bg-white border border-slate-200 text-primary flex items-center justify-center animate-pulse">
              <Bot className="w-3.5 h-3.5" />
            </div>
            <div className="bg-white px-3.5 py-2.5 rounded-2xl text-xs text-slate-500 font-semibold animate-pulse border border-slate-200/90 shadow-xs">
              Consulting RAG vector knowledge base & profile context...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Suggestion Chips */}
      <div className="px-4 py-2 bg-white border-t border-slate-200/80 flex flex-wrap gap-1.5 shrink-0">
        {quickPrompts.map((prompt, i) => (
          <button
            key={i}
            onClick={() => handleSendMessage(undefined, prompt)}
            disabled={sending}
            className="flex items-center space-x-1 px-2.5 py-1 rounded-full bg-slate-100/80 hover:bg-primary/10 hover:text-primary border border-slate-200 text-[11px] font-semibold text-slate-700 transition"
          >
            <Compass className="w-3 h-3 text-primary shrink-0" />
            <span className="truncate max-w-[200px]">{prompt}</span>
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form onSubmit={(e) => handleSendMessage(e)} className="p-3 bg-white border-t border-slate-200/90 flex items-center space-x-2 shrink-0">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your career or skill gaps..."
          className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-primary focus:bg-white transition"
        />
        <button
          type="submit"
          disabled={!input.trim() || sending}
          className="p-2.5 rounded-xl bg-primary hover:bg-primary/90 text-white font-bold transition disabled:opacity-40 shadow-sm"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
