import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../api/client';
import {
  Upload,
  FileText,
  CheckCircle2,
  MapPin,
  Sparkles,
  AlertCircle,
  User,
  Plus,
  X,
  Award,
  Layers,
  RefreshCw,
} from 'lucide-react';

interface ProfileSetupWizardProps {
  onNavigateTab?: (tab: string) => void;
}

export const ProfileSetupWizard: React.FC<ProfileSetupWizardProps> = ({ onNavigateTab }) => {
  const { user, refreshUser } = useAuth();
  
  // Profile Editable State
  const [fullName, setFullName] = useState<string>(user?.full_name || '');
  const [bio, setBio] = useState<string>(user?.bio || 'Aspiring Software & AI Systems Engineer building scalable web applications and microservices.');
  const [targetRolesList, setTargetRolesList] = useState<string[]>(user?.target_roles || []);
  const [newRoleInput, setNewRoleInput] = useState<string>('');
  const [locationPref, setLocationPref] = useState<string>(user?.location_preference || 'Remote / Hybrid');
  
  // Resume & File State
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [savingProfile, setSavingProfile] = useState<boolean>(false);
  const [uploadMessage, setUploadMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [activeResume, setActiveResume] = useState<any>(null);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setTargetRolesList(user.target_roles || []);
      setLocationPref(user.location_preference || 'Remote / Hybrid');
      if (user.bio) setBio(user.bio);
      fetchActiveResume();
    }
  }, [user]);

  const fetchActiveResume = async () => {
    try {
      const resume = await apiFetch<any>('/resumes/active');
      setActiveResume(resume);
    } catch {
      setActiveResume(null);
    }
  };

  const handleAddRole = (e: React.KeyboardEvent | React.MouseEvent) => {
    if ('key' in e && e.key !== 'Enter') return;
    e.preventDefault();
    if (!newRoleInput.trim()) return;
    if (!targetRolesList.includes(newRoleInput.trim())) {
      setTargetRolesList([...targetRolesList, newRoleInput.trim()]);
    }
    setNewRoleInput('');
  };

  const handleRemoveRole = (roleToRemove: string) => {
    setTargetRolesList(targetRolesList.filter((r) => r !== roleToRemove));
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingProfile(true);
    setUploadMessage(null);
    try {
      await apiFetch('/users/profile', {
        method: 'PUT',
        body: JSON.stringify({
          full_name: fullName,
          target_roles: targetRolesList,
          location_preference: locationPref,
          bio: bio,
        }),
      });
      await refreshUser();
      setUploadMessage({ type: 'success', text: 'User profile preferences updated successfully!' });
      setTimeout(() => setUploadMessage(null), 4000);
    } catch (err: any) {
      setUploadMessage({ type: 'error', text: err.message || 'Failed to update profile.' });
    } finally {
      setSavingProfile(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setUploadMessage(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      await apiFetch<any>('/resumes/upload', {
        method: 'POST',
        body: formData,
      });
      setUploadMessage({ type: 'success', text: 'Resume uploaded and set as active profile document!' });
      setFile(null);
      await fetchActiveResume();
      setTimeout(() => setUploadMessage(null), 4000);
    } catch (err: any) {
      setUploadMessage({ type: 'error', text: err.message || 'Failed to upload resume file.' });
    } finally {
      setUploading(false);
    }
  };

  // Profile Completeness Calculation
  const calculateCompleteness = () => {
    let score = 0;
    if (fullName) score += 20;
    if (user?.email) score += 20;
    if (targetRolesList.length > 0) score += 20;
    if (locationPref) score += 15;
    if (bio) score += 10;
    if (activeResume) score += 15;
    return Math.min(100, score);
  };

  const completenessScore = calculateCompleteness();
  const parsedSkills: any[] = activeResume?.parsed_data_json?.skills || [
    { name: 'Python', category: 'Languages' },
    { name: 'FastAPI', category: 'Frameworks' },
    { name: 'React', category: 'Frameworks' },
    { name: 'PostgreSQL', category: 'Databases' },
    { name: 'Docker', category: 'DevOps' },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fadeIn font-sans text-slate-800 pb-12">
      {/* Top Banner Card */}
      <div className="bg-white rounded-3xl p-8 border border-slate-200/80 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-blue-50 to-indigo-50/20 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center space-x-5">
            <div className="relative">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 p-1 shadow-lg shadow-blue-500/20">
                <img
                  src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200"
                  alt="User Profile Avatar"
                  className="w-full h-full object-cover rounded-xl"
                />
              </div>
              <div className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-emerald-500 ring-2 ring-white flex items-center justify-center text-white text-[10px]" title="Account Verified">
                ✓
              </div>
            </div>

            <div>
              <div className="flex items-center space-x-3">
                <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">{user?.full_name || 'Alex Rivera'}</h1>
                <span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 text-xs font-bold border border-blue-200">
                  Student Account
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium mt-1">{user?.email || 'alex.rivera@scoutsphere.ai'}</p>
              
              <div className="flex flex-wrap gap-2 mt-3">
                {targetRolesList.slice(0, 3).map((role, idx) => (
                  <span key={idx} className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 text-[11px] font-bold border border-slate-200">
                    🎯 {role}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Completeness Gauge */}
          <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-4 min-w-[220px] self-stretch md:self-auto flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs font-bold text-slate-700 mb-2">
              <span className="flex items-center space-x-1.5">
                <Award className="w-4 h-4 text-blue-600" />
                <span>Profile Strength</span>
              </span>
              <span className="text-blue-700 font-extrabold">{completenessScore}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden mb-2">
              <div
                className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${completenessScore}%` }}
              />
            </div>
            <p className="text-[10px] text-slate-500 font-medium">
              {completenessScore >= 90 ? '✨ Profile fully optimized for autonomous AI scanning!' : 'Complete bio & resume to unlock max match scores.'}
            </p>
          </div>
        </div>
      </div>

      {/* Global Status Alert Toast */}
      {uploadMessage && (
        <div
          className={`p-4 rounded-2xl text-xs font-bold flex items-center space-x-3 border shadow-sm ${
            uploadMessage.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
              : 'bg-rose-50 border-rose-200 text-rose-900'
          }`}
        >
          {uploadMessage.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
          )}
          <span>{uploadMessage.text}</span>
        </div>
      )}

      {/* Main Grid: Career Details & Resume Document */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Card 1: User Profile & Career Preferences */}
        <div className="bg-white rounded-3xl p-7 border border-slate-200/80 shadow-sm space-y-6">
          <div className="flex items-center space-x-3 pb-4 border-b border-slate-100">
            <div className="p-2 rounded-xl bg-blue-50 text-blue-600">
              <User className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-slate-900 text-sm">Identity & Target Career Roles</h3>
              <p className="text-[11px] text-slate-500">Configure parameters used by AI agents to scan jobs.</p>
            </div>
          </div>

          <form onSubmit={handleSaveProfile} className="space-y-5 text-xs">
            <div>
              <label className="block font-bold text-slate-700 mb-1.5">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-slate-900 font-medium focus:outline-none focus:border-blue-600 transition"
              />
            </div>

            <div>
              <label className="block font-bold text-slate-700 mb-1.5">Professional Bio & Career Objective</label>
              <textarea
                rows={3}
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                placeholder="Briefly state your technical background, career goals, and domain focus..."
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-slate-900 font-medium focus:outline-none focus:border-blue-600 transition placeholder:text-slate-400"
              />
            </div>

            <div>
              <label className="block font-bold text-slate-700 mb-1.5">Target Job Roles</label>
              <div className="flex flex-wrap gap-2 mb-2 bg-slate-50 p-3 rounded-xl border border-slate-200/80 min-h-[50px]">
                {targetRolesList.map((role) => (
                  <span
                    key={role}
                    className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-blue-600 text-white font-semibold text-[11px] shadow-xs"
                  >
                    <span>{role}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveRole(role)}
                      className="hover:bg-blue-700 rounded p-0.5 transition"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>

              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Add target role (e.g. AI Developer)..."
                  value={newRoleInput}
                  onChange={(e) => setNewRoleInput(e.target.value)}
                  onKeyDown={handleAddRole}
                  className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-slate-900 font-medium focus:outline-none focus:border-blue-600 text-xs"
                />
                <button
                  type="button"
                  onClick={handleAddRole}
                  className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-900 text-white font-bold transition flex items-center space-x-1"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add</span>
                </button>
              </div>
            </div>

            <div>
              <label className="block font-bold text-slate-700 mb-1.5">Location & Work Arrangement</label>
              <div className="relative">
                <MapPin className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
                <select
                  value={locationPref}
                  onChange={(e) => setLocationPref(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2.5 text-slate-900 font-semibold focus:outline-none focus:border-blue-600 transition"
                >
                  <option value="Remote Only">Remote Only</option>
                  <option value="Remote / Hybrid">Remote / Hybrid</option>
                  <option value="Onsite / Hybrid">Onsite / Hybrid</option>
                  <option value="Any Location">Any Location</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={savingProfile}
              className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs transition disabled:opacity-50 shadow-md shadow-blue-500/20 flex items-center justify-center space-x-2"
            >
              {savingProfile ? <RefreshCw className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
              <span>{savingProfile ? 'Saving Changes...' : 'Save Profile Changes'}</span>
            </button>
          </form>
        </div>

        {/* Card 2: Active Resume File & Extracted Vector Skills */}
        <div className="bg-white rounded-3xl p-7 border border-slate-200/80 shadow-sm space-y-6">
          <div className="flex items-center space-x-3 pb-4 border-b border-slate-100 justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-xl bg-purple-50 text-purple-600">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-slate-900 text-sm">Active Resume & Parsed Context</h3>
                <p className="text-[11px] text-slate-500">Document used for automated match scoring.</p>
              </div>
            </div>

            {onNavigateTab && (
              <button
                onClick={() => onNavigateTab('resume-tailor')}
                className="px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-xl text-[11px] font-extrabold transition flex items-center space-x-1.5"
              >
                <Sparkles className="w-3.5 h-3.5 text-purple-600" />
                <span>Tailor Workspace</span>
              </button>
            )}
          </div>

          {/* Active Resume Status */}
          {activeResume ? (
            <div className="bg-gradient-to-r from-emerald-50/80 to-teal-50/40 p-4 rounded-2xl border border-emerald-200 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-3">
                <div className="p-2.5 bg-emerald-600 text-white rounded-xl shadow-xs">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-bold text-emerald-950">Active Resume PDF</div>
                  <div className="text-emerald-700 text-[11px] font-medium">Uploaded: {new Date(activeResume.created_at).toLocaleDateString()}</div>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full bg-emerald-600 text-white text-[10px] font-black tracking-wider uppercase shadow-xs">
                ACTIVE
              </span>
            </div>
          ) : (
            <div className="bg-amber-50/60 p-4 rounded-2xl border border-amber-200 text-xs text-amber-800 font-semibold flex items-center space-x-3">
              <AlertCircle className="w-5 h-5 text-amber-600 shrink-0" />
              <span>No active resume uploaded yet. Upload a PDF/DOCX below to enable AI skill matching.</span>
            </div>
          )}

          {/* Extracted Skills Cloud */}
          <div className="space-y-2">
            <label className="block text-xs font-bold text-slate-700 flex items-center space-x-1.5">
              <Layers className="w-4 h-4 text-blue-600" />
              <span>Parsed Technical Competencies & Skills</span>
            </label>
            <div className="flex flex-wrap gap-2 p-3 bg-slate-50 rounded-2xl border border-slate-200/80 min-h-[90px] items-center">
              {parsedSkills.map((sk: any, i: number) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-slate-800 font-bold text-[11px] shadow-2xs flex items-center space-x-1"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                  <span>{sk.name}</span>
                </span>
              ))}
            </div>
          </div>

          {/* Upload Form */}
          <form onSubmit={handleFileUpload} className="space-y-4 text-xs">
            <div className="border-2 border-dashed border-slate-300 rounded-2xl p-6 text-center hover:border-blue-500 hover:bg-blue-50/30 transition cursor-pointer bg-slate-50/50">
              <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <label className="block text-slate-700 font-bold cursor-pointer mb-1 text-xs">
                {file ? file.name : 'Select or drag & drop Resume PDF/DOCX'}
              </label>
              <p className="text-[10px] text-slate-400 font-medium mb-3">PDF or DOCX files up to 10MB</p>
              <input
                type="file"
                accept=".pdf,.docx,.doc"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
                id="profile-resume-input"
              />
              <label
                htmlFor="profile-resume-input"
                className="inline-block px-4 py-2 rounded-xl bg-white border border-slate-300 text-slate-800 text-[11px] font-bold hover:bg-slate-100 transition cursor-pointer shadow-xs"
              >
                Browse File
              </label>
            </div>

            <button
              type="submit"
              disabled={!file || uploading}
              className="w-full py-3 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs transition disabled:opacity-50 shadow-md shadow-purple-500/20 flex items-center justify-center space-x-2"
            >
              {uploading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
              <span>{uploading ? 'Parsing & Generating Vector Embeddings...' : 'Upload & Process Resume Document'}</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProfileSetupWizard;
