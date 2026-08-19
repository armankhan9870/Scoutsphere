import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { X, Lock, Mail, User as UserIcon, Sparkles, KeyRound, CheckCircle2, ShieldAlert } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

type AuthTab = 'login' | 'signup' | 'forgot' | 'verify' | 'reset';

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const { login, signup, googleLogin, forgotPassword, resetPassword, verifyEmail, resendVerification } = useAuth();
  const [activeTab, setActiveTab] = useState<AuthTab>('login');

  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [fullName, setFullName] = useState<string>('');
  const [targetRoles, setTargetRoles] = useState<string>('Backend Engineer, AI Developer');

  const [verifyToken, setVerifyToken] = useState<string>('');
  const [resetToken, setResetToken] = useState<string>('');
  const [newPassword, setNewPassword] = useState<string>('');

  const [error, setError] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setInfoMessage(null);
    setSubmitting(true);

    try {
      if (activeTab === 'login') {
        await login(email, password);
        if (onSuccess) onSuccess();
        else onClose();
      } else if (activeTab === 'signup') {
        const rolesList = targetRoles.split(',').map((r) => r.trim()).filter(Boolean);
        await signup(email, password, fullName, rolesList);
        if (onSuccess) onSuccess();
        else onClose();
      } else if (activeTab === 'forgot') {
        const msg = await forgotPassword(email);
        setInfoMessage(msg);
      } else if (activeTab === 'reset') {
        const msg = await resetPassword(resetToken, newPassword);
        setInfoMessage(msg);
        setTimeout(() => setActiveTab('login'), 2000);
      } else if (activeTab === 'verify') {
        const msg = await verifyEmail(verifyToken);
        setInfoMessage(msg);
        setTimeout(() => {
          if (onSuccess) onSuccess();
          else onClose();
        }, 1500);
      }
    } catch (err: any) {
      setError(err.message || 'Authentication operation failed.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError(null);
    setSubmitting(true);
    try {
      // Trigger Google OAuth ID token authentication
      const mockGoogleCredential = `mock_google_token_${(email || 'user').split('@')[0]}`;
      await googleLogin(mockGoogleCredential);
      if (onSuccess) onSuccess();
      else onClose();
    } catch (err: any) {
      setError(err.message || 'Google OAuth Sign-In failed.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleResendVerification = async () => {
    if (!email) {
      setError('Please provide your email address to resend verification link.');
      return;
    }
    setError(null);
    try {
      const msg = await resendVerification(email);
      setInfoMessage(msg);
    } catch (err: any) {
      setError(err.message || 'Failed to resend verification email.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800/90 p-7 rounded-3xl shadow-2xl text-slate-100 overflow-hidden">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="text-center mb-6">
          <div className="inline-flex p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 mb-3">
            <Sparkles className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold text-white">
            {activeTab === 'login' && 'Welcome Back to ScoutSphere'}
            {activeTab === 'signup' && 'Create Your Career Account'}
            {activeTab === 'forgot' && 'Reset Your Password'}
            {activeTab === 'verify' && 'Verify Email Address'}
            {activeTab === 'reset' && 'Set New Password'}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {activeTab === 'login' && 'Enter credentials to access AI agents, resume tailoring & sessions'}
            {activeTab === 'signup' && 'Sign up with Argon2 protection & email verification'}
            {activeTab === 'forgot' && 'We will send a password reset token link'}
            {activeTab === 'verify' && 'Enter the verification token sent to your email'}
            {activeTab === 'reset' && 'Enter reset token and your new strong password'}
          </p>
        </div>

        {/* Tab Switcher */}
        {(activeTab === 'login' || activeTab === 'signup') && (
          <div className="flex bg-slate-900/80 p-1 rounded-xl mb-6 border border-slate-800 text-xs font-semibold">
            <button
              onClick={() => { setActiveTab('login'); setError(null); setInfoMessage(null); }}
              className={`flex-1 py-2 rounded-lg transition ${activeTab === 'login' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            >
              Log In
            </button>
            <button
              onClick={() => { setActiveTab('signup'); setError(null); setInfoMessage(null); }}
              className={`flex-1 py-2 rounded-lg transition ${activeTab === 'signup' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            >
              Sign Up
            </button>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-start gap-2">
            <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Info / Success Alert */}
        {infoMessage && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <span>{infoMessage}</span>
          </div>
        )}

        <form onSubmit={handleAuthSubmit} className="space-y-4 text-xs">
          {activeTab === 'signup' && (
            <div>
              <label className="block font-medium text-slate-300 mb-1">Full Name</label>
              <div className="relative">
                <UserIcon className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  required
                  placeholder="Jane Doe"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          )}

          {(activeTab === 'login' || activeTab === 'signup' || activeTab === 'forgot') && (
            <div>
              <label className="block font-medium text-slate-300 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  required
                  placeholder="student@scoutsphere.ai"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          )}

          {(activeTab === 'login' || activeTab === 'signup') && (
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="font-medium text-slate-300">Password</label>
                {activeTab === 'login' && (
                  <button
                    type="button"
                    onClick={() => { setActiveTab('forgot'); setError(null); setInfoMessage(null); }}
                    className="text-xs text-indigo-400 hover:underline font-medium"
                  >
                    Forgot Password?
                  </button>
                )}
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          )}

          {activeTab === 'signup' && (
            <div>
              <label className="block font-medium text-slate-300 mb-1">Target Roles (comma separated)</label>
              <input
                type="text"
                placeholder="Backend Engineer, AI Developer"
                value={targetRoles}
                onChange={(e) => setTargetRoles(e.target.value)}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-4 py-2.5 text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500"
              />
            </div>
          )}

          {activeTab === 'verify' && (
            <div>
              <label className="block font-medium text-slate-300 mb-1">Verification Token</label>
              <div className="relative">
                <KeyRound className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  required
                  placeholder="Paste verification token string"
                  value={verifyToken}
                  onChange={(e) => setVerifyToken(e.target.value)}
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <button
                type="button"
                onClick={handleResendVerification}
                className="mt-2 text-xs text-indigo-400 hover:underline font-medium"
              >
                Resend verification token email
              </button>
            </div>
          )}

          {activeTab === 'reset' && (
            <>
              <div>
                <label className="block font-medium text-slate-300 mb-1">Reset Token</label>
                <input
                  type="text"
                  required
                  placeholder="Paste password reset token"
                  value={resetToken}
                  onChange={(e) => setResetToken(e.target.value)}
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-4 py-2.5 text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block font-medium text-slate-300 mb-1">New Password</label>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-4 py-2.5 text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold transition shadow-lg shadow-indigo-500/25 disabled:opacity-50 mt-2"
          >
            {submitting
              ? 'Processing...'
              : activeTab === 'login'
              ? 'Sign In'
              : activeTab === 'signup'
              ? 'Create Account'
              : activeTab === 'forgot'
              ? 'Send Reset Token'
              : activeTab === 'verify'
              ? 'Verify Email'
              : 'Reset Password'}
          </button>
        </form>

        {/* Divider */}
        {(activeTab === 'login' || activeTab === 'signup') && (
          <div className="mt-6">
            <div className="relative flex items-center justify-center mb-4">
              <div className="border-t border-slate-800 w-full" />
              <span className="bg-slate-900 px-3 text-[10px] uppercase tracking-wider text-slate-500 font-semibold absolute">
                Or Continue With
              </span>
            </div>

            {/* Google OAuth Button */}
            <button
              onClick={handleGoogleSignIn}
              disabled={submitting}
              type="button"
              className="w-full flex items-center justify-center gap-3 py-2.5 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800/80 text-white text-xs font-semibold transition disabled:opacity-50"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"
                />
                <path
                  fill="#34A853"
                  d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.27v3.15C3.25 21.3 7.31 24 12 24z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.27C.46 8.2 0 10.04 0 12s.46 3.8 1.27 5.42l4.01-3.15z"
                />
                <path
                  fill="#EA4335"
                  d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.31 0 3.25 2.7 1.27 6.58l4.01 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
                />
              </svg>
              Google Sign-In
            </button>
          </div>
        )}

        {(activeTab === 'forgot' || activeTab === 'verify' || activeTab === 'reset') && (
          <div className="mt-4 text-center">
            <button
              onClick={() => { setActiveTab('login'); setError(null); setInfoMessage(null); }}
              className="text-xs text-slate-400 hover:text-white transition underline"
            >
              Back to Login
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
