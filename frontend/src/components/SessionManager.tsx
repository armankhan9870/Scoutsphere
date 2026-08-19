import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Laptop, Smartphone, ShieldCheck, LogOut, Trash2, RefreshCw, Clock, Globe } from 'lucide-react';

export const SessionManager: React.FC = () => {
  const { sessions, fetchSessions, revokeSession, logoutAll } = useAuth();
  const [loading, setLoading] = useState<boolean>(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setLoading(true);
    try {
      await fetchSessions();
    } catch {
      // Handled in context
    } finally {
      setLoading(false);
    }
  };

  const handleRevoke = async (sessionId: string) => {
    try {
      await revokeSession(sessionId);
      setActionMessage('Device session revoked successfully.');
      setTimeout(() => setActionMessage(null), 3000);
    } catch (e: any) {
      setActionMessage(e.message || 'Failed to revoke session.');
    }
  };

  const handleLogoutAll = async () => {
    if (window.confirm('Are you sure you want to log out from all devices? You will be signed out everywhere.')) {
      await logoutAll();
    }
  };

  const formatTime = (isoString: string) => {
    try {
      return new Date(isoString).toLocaleString();
    } catch {
      return isoString;
    }
  };

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-indigo-400" />
            Active Device Sessions
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Manage your logged-in devices and active security sessions across browsers.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadSessions}
            disabled={loading}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 hover:text-white transition disabled:opacity-50"
            title="Refresh Sessions"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={handleLogoutAll}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 hover:bg-rose-500/20 text-xs font-semibold transition"
          >
            <LogOut className="w-3.5 h-3.5" />
            Revoke All Other Devices
          </button>
        </div>
      </div>

      {actionMessage && (
        <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs">
          {actionMessage}
        </div>
      )}

      <div className="space-y-3">
        {sessions.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs">
            {loading ? 'Loading active sessions...' : 'No active session records found.'}
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              className={`p-4 rounded-xl border transition flex items-center justify-between ${
                session.is_current
                  ? 'bg-indigo-950/20 border-indigo-500/40'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-slate-800 text-indigo-400">
                  {session.device_info.toLowerCase().includes('mobile') ? (
                    <Smartphone className="w-5 h-5" />
                  ) : (
                    <Laptop className="w-5 h-5" />
                  )}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-white">{session.device_info}</span>
                    {session.is_current && (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-[10px] font-bold">
                        This Device
                      </span>
                    )}
                    {!session.is_active && (
                      <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px]">
                        Revoked
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-xs text-slate-400 mt-1">
                    <span className="flex items-center gap-1">
                      <Globe className="w-3.5 h-3.5 text-slate-500" />
                      {session.ip_address}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-slate-500" />
                      Last Active: {formatTime(session.last_active)}
                    </span>
                  </div>
                </div>
              </div>

              {session.is_active && (
                <button
                  onClick={() => handleRevoke(session.id)}
                  className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition"
                  title="Revoke session"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
