import React, { useState, useEffect } from 'react';
import { apiFetch, downloadUserDataExport } from '../api/client';
import { SessionManager } from './SessionManager';
import {
  User,
  Shield,
  Briefcase,
  FileText,
  Bell,
  Download,
  Trash2,
  Check,
  AlertTriangle,
  Sliders,
  Cpu,
  RefreshCw,
  KeyRound,
} from 'lucide-react';


export const SettingsView: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'account' | 'career' | 'agent' | 'resume' | 'notifications' | 'privacy'>('account');

  // Form State
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Settings Data
  const [settings, setSettings] = useState<any>({
    full_name: '',
    email: '',
    pending_new_email: '',
    target_roles: [],
    target_industries: [],
    target_locations: [],
    work_style: 'remote',
    min_salary: 80000,
    opportunity_types: ['internship', 'job', 'hackathon'],
    discovery_frequency: 'daily',
    min_match_score: 70,
    auto_hide_low_score: false,
    default_resume_template: 'modern_clean',
    cover_letter_tone: 'conversational',
    auto_tailor_high_matches: false,
    preferred_llm_provider: 'gemini',
    agent_tone: 'exploratory',
    auto_background_agents: false,
    notify_high_matches: true,
    notify_deadlines: true,
    notify_status_changes: true,
    notify_weekly_digest: true,
    email_notifications_enabled: false,
    exclude_resume_from_training: false,
    theme: 'light',
    layout_density: 'comfortable',
  });

  // Password & Email Flows
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newEmailInput, setNewEmailInput] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [pendingEmailCode, setPendingEmailCode] = useState<string | null>(null);

  // Delete Account Confirmation Modal
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const data = await apiFetch<any>('/settings');
      setSettings(data);
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to load settings.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSaveSettings = async (overridePayload?: any) => {
    setSaving(true);
    setMessage(null);
    try {
      const payload = overridePayload || settings;
      const updated = await apiFetch<any>('/settings', {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
      setSettings(updated);
      setMessage({ type: 'success', text: 'Settings updated successfully!' });
      setTimeout(() => setMessage(null), 4000);
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to update settings.' });
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentPassword || !newPassword) return;
    try {
      await apiFetch<any>('/settings/account/password', {
        method: 'POST',
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      });
      setMessage({ type: 'success', text: 'Password changed successfully!' });
      setCurrentPassword('');
      setNewPassword('');
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Password change failed.' });
    }
  };

  const handleRequestEmailChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmailInput.trim()) return;
    try {
      const res = await apiFetch<any>('/settings/account/email/request', {
        method: 'POST',
        body: JSON.stringify({ new_email: newEmailInput }),
      });
      setPendingEmailCode(res.verification_code_demo);
      setMessage({ type: 'success', text: res.message });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Email change request failed.' });
    }
  };

  const handleVerifyEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!verificationCode.trim()) return;
    try {
      const res = await apiFetch<any>('/settings/account/email/verify', {
        method: 'POST',
        body: JSON.stringify({ verification_code: verificationCode }),
      });
      setMessage({ type: 'success', text: res.message });
      setPendingEmailCode(null);
      setNewEmailInput('');
      setVerificationCode('');
      fetchSettings();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Email verification failed.' });
    }
  };



  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== 'DELETE') return;
    try {
      await apiFetch<any>('/settings/account/purge', { method: 'DELETE' });
      localStorage.clear();
      window.location.href = '/';
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Account purge failed.' });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <RefreshCw className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-12 font-sans text-slate-800">
      {/* Top Banner Header */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200/80 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center space-x-2">
            <span>Settings & Preferences</span>
            <Sliders className="w-6 h-6 text-primary" />
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Manage your account security, AI agent automation dials, career target filters, and data privacy controls.
          </p>
        </div>

        <button
          onClick={() => handleSaveSettings()}
          disabled={saving}
          className="px-6 py-2.5 bg-primary hover:bg-primary/90 text-white font-semibold text-xs rounded-xl shadow-md transition flex items-center space-x-2 disabled:opacity-50 self-start md:self-auto"
        >
          {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
          <span>{saving ? 'Saving...' : 'Save All Preferences'}</span>
        </button>
      </div>

      {/* Global Status Message Toast */}
      {message && (
        <div
          className={`p-4 rounded-xl text-xs font-semibold flex items-center space-x-2 border shadow-sm ${
            message.type === 'success'
              ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
              : 'bg-rose-50 text-rose-800 border-rose-200'
          }`}
        >
          {message.type === 'success' ? <Check className="w-4 h-4 text-emerald-600" /> : <AlertTriangle className="w-4 h-4 text-rose-600" />}
          <span>{message.text}</span>
        </div>
      )}

      {/* Navigation Sub-Tabs Bar */}
      <div className="flex flex-wrap gap-2 border-b border-slate-200/80 pb-2">
        {[
          { id: 'account', label: 'Account & Security', icon: User },
          { id: 'career', label: 'Career & Matching', icon: Briefcase },
          { id: 'agent', label: 'AI & Agent Controls', icon: Cpu },
          { id: 'resume', label: 'Resume & Cover Letter', icon: FileText },
          { id: 'notifications', label: 'Notifications & Theme', icon: Bell },
          { id: 'privacy', label: 'Privacy & Data Controls', icon: Shield },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id as any)}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl font-semibold text-xs transition ${
                isActive
                  ? 'bg-primary text-white shadow-sm'
                  : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200/80 hover:bg-slate-50'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab 1: Account & Security */}
      {activeSubTab === 'account' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Profile & Email */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-5">
            <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3">
              <User className="w-4 h-4 text-primary" />
              <span>Account Profile</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  value={settings.full_name || ''}
                  onChange={(e) => setSettings({ ...settings, full_name: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs text-slate-900 focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Current Email</label>
                <input
                  type="email"
                  disabled
                  value={settings.email || ''}
                  className="w-full bg-slate-100 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs text-slate-500 cursor-not-allowed"
                />
              </div>

              {/* Email Change Flow */}
              <div className="pt-2 border-t border-slate-100 space-y-3">
                <label className="block text-xs font-semibold text-slate-700">Change Email Address</label>
                <form onSubmit={handleRequestEmailChange} className="flex gap-2">
                  <input
                    type="email"
                    placeholder="New email address..."
                    value={newEmailInput}
                    onChange={(e) => setNewEmailInput(e.target.value)}
                    className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-primary"
                  />
                  <button type="submit" className="px-4 py-2 bg-slate-800 text-white rounded-xl text-xs font-semibold hover:bg-slate-900 transition">
                    Send Code
                  </button>
                </form>

                {pendingEmailCode && (
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs space-y-2">
                    <p className="text-amber-800 font-semibold">Demo Code Sent: <span className="font-mono bg-white px-2 py-0.5 rounded border border-amber-300">{pendingEmailCode}</span></p>
                    <form onSubmit={handleVerifyEmail} className="flex gap-2">
                      <input
                        type="text"
                        placeholder="Enter 6-digit verification code..."
                        value={verificationCode}
                        onChange={(e) => setVerificationCode(e.target.value)}
                        className="flex-1 bg-white border border-amber-300 rounded-xl px-3 py-1.5 text-xs focus:outline-none"
                      />
                      <button type="submit" className="px-3 py-1.5 bg-amber-600 text-white rounded-xl text-xs font-bold hover:bg-amber-700">
                        Confirm Email
                      </button>
                    </form>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Password Change */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-5">
            <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3">
              <KeyRound className="w-4 h-4 text-primary" />
              <span>Change Password</span>
            </h2>

            <form onSubmit={handleChangePassword} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Current Password</label>
                <input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs text-slate-900 focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">New Password</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  minLength={6}
                  required
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs text-slate-900 focus:outline-none focus:border-primary"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-slate-900 text-white rounded-xl font-semibold text-xs hover:bg-slate-800 transition"
              >
                Update Password
              </button>
            </form>
          </div>

          {/* Active Security Sessions */}
          <div className="lg:col-span-2">
            <SessionManager />
          </div>
        </div>
      )}

      {/* Tab 2: Career & Matching */}
      {activeSubTab === 'career' && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-6">
          <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3">
            <Briefcase className="w-4 h-4 text-primary" />
            <span>Career Preferences & Opportunity Filters</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Work Style Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">Preferred Work Style</label>
              <div className="grid grid-cols-3 gap-2">
                {['remote', 'hybrid', 'onsite'].map((style) => (
                  <button
                    key={style}
                    type="button"
                    onClick={() => setSettings({ ...settings, work_style: style })}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold capitalize border transition ${
                      settings.work_style === style
                        ? 'bg-primary text-white border-primary shadow-xs'
                        : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {style}
                  </button>
                ))}
              </div>
            </div>

            {/* Min Match Threshold Slider */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-semibold text-slate-700">Minimum Match Threshold</label>
                <span className="text-xs font-bold text-primary px-2 py-0.5 bg-blue-50 rounded-md border border-blue-200">
                  {settings.min_match_score}%
                </span>
              </div>
              <input
                type="range"
                min="50"
                max="95"
                step="5"
                value={settings.min_match_score || 70}
                onChange={(e) => setSettings({ ...settings, min_match_score: parseInt(e.target.value) })}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-primary"
              />
              <p className="text-[11px] text-slate-500 mt-1">
                Only surface roles with match score equal to or higher than {settings.min_match_score}%.
              </p>
            </div>

            {/* Auto Hide Toggle */}
            <div className="flex items-center justify-between p-4 rounded-xl border border-slate-200 bg-slate-50">
              <div>
                <p className="text-xs font-bold text-slate-900">Auto-Hide Low-Score Opportunities</p>
                <p className="text-[11px] text-slate-500">Automatically filter out opportunities below threshold.</p>
              </div>
              <input
                type="checkbox"
                checked={settings.auto_hide_low_score || false}
                onChange={(e) => setSettings({ ...settings, auto_hide_low_score: e.target.checked })}
                className="w-4 h-4 text-primary rounded border-slate-300 focus:ring-primary"
              />
            </div>

            {/* Discovery Frequency */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">Autonomous Discovery Frequency</label>
              <select
                value={settings.discovery_frequency || 'daily'}
                onChange={(e) => setSettings({ ...settings, discovery_frequency: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-medium text-slate-900 focus:outline-none focus:border-primary"
              >
                <option value="daily">Daily Automatic Scanning</option>
                <option value="weekly">Weekly Summary Batch</option>
                <option value="manual">Manual Execution Only</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: AI & Agent Controls */}
      {activeSubTab === 'agent' && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-6">
          <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3">
            <Cpu className="w-4 h-4 text-primary" />
            <span>AI Provider Fallback & Autonomous Agent Dials</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Preferred LLM Provider */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">Preferred LLM Primary Provider</label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: 'gemini', name: 'Google Gemini' },
                  { id: 'groq', name: 'Groq LPU' },
                  { id: 'openrouter', name: 'OpenRouter' },
                  { id: 'ollama', name: 'Local Ollama' },
                ].map((prov) => (
                  <button
                    key={prov.id}
                    type="button"
                    onClick={() => setSettings({ ...settings, preferred_llm_provider: prov.id })}
                    className={`p-3 rounded-xl text-xs font-semibold border text-left transition ${
                      settings.preferred_llm_provider === prov.id
                        ? 'bg-blue-50 border-primary text-primary shadow-xs'
                        : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    {prov.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Agent Tone Dial */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">Career Chatbot Agent Tone</label>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { id: 'conservative', title: 'Conservative', desc: 'Strict factual advice & realistic targets' },
                  { id: 'exploratory', title: 'Exploratory', desc: 'Creative roadmap steps & ambitious targets' },
                ].map((tone) => (
                  <button
                    key={tone.id}
                    type="button"
                    onClick={() => setSettings({ ...settings, agent_tone: tone.id })}
                    className={`p-3 rounded-xl text-xs border text-left transition ${
                      settings.agent_tone === tone.id
                        ? 'bg-blue-50 border-primary text-primary shadow-xs font-bold'
                        : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100 font-semibold'
                    }`}
                  >
                    <p className="font-bold">{tone.title}</p>
                    <p className="text-[10px] opacity-80 font-normal mt-1">{tone.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Auto Background Agents Toggle */}
            <div className="md:col-span-2 p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-slate-900">Let Agents Auto-Run in Background</p>
                <p className="text-[11px] text-slate-500">
                  When enabled, ScoutSphere agents continuously scan opportunities and match profiles autonomously. (Default: Opt-in Off)
                </p>
              </div>
              <input
                type="checkbox"
                checked={settings.auto_background_agents || false}
                onChange={(e) => setSettings({ ...settings, auto_background_agents: e.target.checked })}
                className="w-5 h-5 text-primary rounded border-slate-300 focus:ring-primary cursor-pointer"
              />
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Resume & Cover Letter */}
      {activeSubTab === 'resume' && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-6">
          <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3">
            <FileText className="w-4 h-4 text-primary" />
            <span>Resume & Application Defaults</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">Default Cover Letter Tone</label>
              <select
                value={settings.cover_letter_tone || 'conversational'}
                onChange={(e) => setSettings({ ...settings, cover_letter_tone: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-medium text-slate-900 focus:outline-none focus:border-primary"
              >
                <option value="conversational">Conversational & Engaging</option>
                <option value="formal">Formal & Corporate</option>
                <option value="concise">Concise & Direct (Bullet Points)</option>
              </select>
            </div>

            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-slate-900">Auto-Generate Tailored Resumes for High Matches</p>
                <p className="text-[11px] text-slate-500">Automatically trigger tailoring when match score &gt; 90%.</p>
              </div>
              <input
                type="checkbox"
                checked={settings.auto_tailor_high_matches || false}
                onChange={(e) => setSettings({ ...settings, auto_tailor_high_matches: e.target.checked })}
                className="w-4 h-4 text-primary rounded border-slate-300"
              />
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: Notifications & Appearance */}
      {activeSubTab === 'notifications' && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-6">
          <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3">
            <Bell className="w-4 h-4 text-primary" />
            <span>In-App Event Notifications & Theme</span>
          </h2>

          <div className="space-y-3">
            {[
              { key: 'notify_high_matches', label: 'New High-Match Opportunity Alert' },
              { key: 'notify_deadlines', label: 'Application Deadline Approaching Reminder' },
              { key: 'notify_status_changes', label: 'Application Stage Status Changes' },
              { key: 'notify_weekly_digest', label: 'Weekly Career Roadmap Digest' },
            ].map((item) => (
              <div key={item.key} className="flex items-center justify-between p-3 rounded-xl border border-slate-200/80 bg-slate-50">
                <span className="text-xs font-semibold text-slate-800">{item.label}</span>
                <input
                  type="checkbox"
                  checked={settings[item.key] ?? true}
                  onChange={(e) => setSettings({ ...settings, [item.key]: e.target.checked })}
                  className="w-4 h-4 text-primary rounded border-slate-300"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 6: Privacy & Data Controls */}
      {activeSubTab === 'privacy' && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-6">
          <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3">
            <Shield className="w-4 h-4 text-primary" />
            <span>Privacy & Data Management</span>
          </h2>

          <div className="space-y-4">
            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-slate-900">Exclude Resume Content from Training</p>
                <p className="text-[11px] text-slate-500">Prevent resume data from being used in future model fine-tuning or evaluation pipelines.</p>
              </div>
              <input
                type="checkbox"
                checked={settings.exclude_resume_from_training || false}
                onChange={(e) => setSettings({ ...settings, exclude_resume_from_training: e.target.checked })}
                className="w-4 h-4 text-primary rounded border-slate-300"
              />
            </div>

            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-slate-900">Download My Complete Data Export</p>
                <p className="text-[11px] text-slate-500">Download a full JSON archive containing profile, resumes, matches, applications, and chat history.</p>
              </div>
              <button
                onClick={downloadUserDataExport}
                className="px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold hover:bg-slate-800 transition flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Export JSON Data</span>
              </button>
            </div>

            {/* Danger Zone */}
            <div className="p-4 rounded-xl border border-rose-200 bg-rose-50/50 space-y-3">
              <div className="flex items-center space-x-2 text-rose-800">
                <AlertTriangle className="w-5 h-5 text-rose-600" />
                <h3 className="text-xs font-bold uppercase tracking-wider">Danger Zone</h3>
              </div>
              <p className="text-xs text-rose-700">
                Deleting your account will permanently purge all stored resumes, applications, matches, and settings. This action cannot be undone.
              </p>
              <button
                onClick={() => setShowDeleteModal(true)}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition flex items-center space-x-2"
              >
                <Trash2 className="w-4 h-4" />
                <span>Delete Account</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-200">
            <h3 className="text-base font-bold text-rose-600 flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5" />
              <span>Confirm Permanent Account Deletion</span>
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              To confirm deletion of your ScoutSphere account and immediate purge of all data, please type <span className="font-mono font-bold text-slate-900 bg-slate-100 px-1.5 py-0.5 rounded">DELETE</span> below:
            </p>
            <input
              type="text"
              value={deleteConfirmText}
              onChange={(e) => setDeleteConfirmText(e.target.value)}
              placeholder="Type DELETE..."
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-xs font-mono text-slate-900 focus:outline-none focus:border-rose-600"
            />
            <div className="flex justify-end space-x-3 pt-2">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAccount}
                disabled={deleteConfirmText !== 'DELETE'}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition disabled:opacity-40"
              >
                Permanently Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
