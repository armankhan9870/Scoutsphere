import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { AuthModal } from './AuthModal';
import { ShieldCheck, LogIn, Mail } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireVerification?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireVerification = false,
}) => {
  const { user, loading } = useAuth();
  const [authModalOpen, setAuthModalOpen] = useState<boolean>(false);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="glass-panel p-8 rounded-2xl text-center max-w-md mx-auto my-12 border border-slate-800 space-y-4">
        <div className="p-4 rounded-full bg-indigo-500/10 text-indigo-400 w-16 h-16 mx-auto flex items-center justify-center">
          <ShieldCheck className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-bold text-white">Authentication Required</h3>
        <p className="text-xs text-slate-400">
          Please log in or create an account to access AI career agents, resume tailoring, and job application tracking.
        </p>
        <button
          onClick={() => setAuthModalOpen(true)}
          className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold text-xs transition shadow-lg shadow-indigo-500/25 flex items-center justify-center gap-2 mx-auto"
        >
          <LogIn className="w-4 h-4" />
          Sign In / Register
        </button>

        <AuthModal
          isOpen={authModalOpen}
          onClose={() => setAuthModalOpen(false)}
          onSuccess={() => setAuthModalOpen(false)}
        />
      </div>
    );
  }

  if (requireVerification && user.is_verified === false) {
    return (
      <div className="glass-panel p-8 rounded-2xl text-center max-w-md mx-auto my-12 border border-amber-500/30 space-y-4">
        <div className="p-4 rounded-full bg-amber-500/10 text-amber-400 w-16 h-16 mx-auto flex items-center justify-center">
          <Mail className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-bold text-white">Email Verification Required</h3>
        <p className="text-xs text-slate-400">
          Please verify your email address ({user.email}) to unlock full feature access.
        </p>
        <button
          onClick={() => setAuthModalOpen(true)}
          className="px-6 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs transition shadow-lg shadow-amber-500/25 flex items-center justify-center gap-2 mx-auto"
        >
          Enter Verification Token
        </button>

        <AuthModal
          isOpen={authModalOpen}
          onClose={() => setAuthModalOpen(false)}
          onSuccess={() => setAuthModalOpen(false)}
        />
      </div>
    );
  }

  return <>{children}</>;
};
