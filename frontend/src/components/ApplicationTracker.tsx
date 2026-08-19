import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../api/client';
import { Briefcase, Clock } from 'lucide-react';


interface KanbanColumn {
  title: string;
  key: string;
  color: string;
  badgeColor: string;
  items: any[];
}

export const ApplicationTracker: React.FC = () => {
  const { user } = useAuth();
  const [columns, setColumns] = useState<KanbanColumn[]>([
    {
      title: 'Saved',
      key: 'SAVED',
      color: 'border-slate-300 bg-slate-50 text-slate-700',
      badgeColor: 'bg-slate-200 text-slate-800',
      items: [
        { id: '1', title: 'Full Stack Intern', company: 'Meta', updated: '2 days ago' },
      ],
    },
    {
      title: 'Drafting',
      key: 'DRAFTING',
      color: 'border-blue-200 bg-blue-50/50 text-blue-900',
      badgeColor: 'bg-blue-100 text-blue-800',
      items: [],
    },
    {
      title: 'Applied',
      key: 'APPLIED',
      color: 'border-indigo-200 bg-indigo-50/50 text-indigo-900',
      badgeColor: 'bg-indigo-100 text-indigo-800',
      items: [
        { id: '2', title: 'Software Engineering Intern', company: 'Stripe Inc', updated: '16 days ago' },
      ],
    },
    {
      title: 'Interviewing',
      key: 'INTERVIEWING',
      color: 'border-purple-200 bg-purple-50/50 text-purple-900',
      badgeColor: 'bg-purple-100 text-purple-800',
      items: [
        { id: '3', title: 'Associate AI Systems Engineer', company: 'ScoutSphere Inc', updated: 'Yesterday' },
      ],
    },
    {
      title: 'Offer',
      key: 'OFFER',
      color: 'border-emerald-200 bg-emerald-50/50 text-emerald-900',
      badgeColor: 'bg-emerald-100 text-emerald-800',
      items: [],
    },
    {
      title: 'Rejected',
      key: 'REJECTED',
      color: 'border-rose-200 bg-rose-50/50 text-rose-900',
      badgeColor: 'bg-rose-100 text-rose-800',
      items: [],
    },
  ]);

  const loadApplications = async () => {
    if (!user) return;
    try {
      const data = await apiFetch<any>(`/applications/users/${user.id}/applications`);
      if (data?.kanban_columns) {
        setColumns((prev) =>
          prev.map((col) => {
            const fetched = data.kanban_columns[col.key] || [];
            return fetched.length > 0
              ? {
                  ...col,
                  items: fetched.map((item: any) => ({
                    id: item.id,
                    title: item.opportunity_title || item.title || 'Backend Engineer',
                    company: item.company_name || item.company || 'Stripe',
                    updated: 'Just now',
                  })),

                }
              : col;
          })
        );
      }
    } catch (err) {
      console.error('Failed to load Kanban applications:', err);
    }
  };

  useEffect(() => {
    loadApplications();
  }, [user]);

  const moveItem = async (itemId: string, targetKey: string) => {
    setColumns((prev) => {
      let foundItem: any = null;
      const nextCols = prev.map((col) => {
        const filtered = col.items.filter((item) => {
          if (item.id === itemId) {
            foundItem = item;
            return false;
          }
          return true;
        });
        return { ...col, items: filtered };
      });

      if (foundItem) {
        return nextCols.map((col) => {
          if (col.key === targetKey) {
            return { ...col, items: [...col.items, { ...foundItem, updated: 'Just now' }] };
          }
          return col;
        });
      }
      return prev;
    });

    try {
      await apiFetch<any>(`/applications/${itemId}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ new_status: targetKey, notes: `Updated status to ${targetKey}` }),
      });
    } catch {
      // Graceful fallback for mock item IDs
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="unstop-card p-6 flex items-center justify-between border-l-4 border-l-blue-600 shadow-sm">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900 flex items-center space-x-2">
            <Briefcase className="w-5 h-5 text-blue-600" />
            <span>Application Tracker</span>
          </h2>
          <p className="text-xs text-slate-500 font-medium">Track application state transitions and audit status history</p>
        </div>
      </div>

      {/* Kanban Board Columns */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 overflow-x-auto pb-4">
        {columns.map((col) => (
          <div key={col.key} className={`unstop-card p-4 border ${col.color} space-y-3 min-w-[200px] shadow-sm`}>
            <div className="flex items-center justify-between border-b border-slate-200/80 pb-2">
              <span className="text-xs font-black uppercase tracking-wider text-slate-900">{col.title}</span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-black font-mono ${col.badgeColor}`}>
                {col.items.length}
              </span>
            </div>

            <div className="space-y-3">
              {col.items.map((item) => (
                <div
                  key={item.id}
                  className="p-3.5 rounded-xl bg-white border border-slate-200 space-y-2 hover:border-blue-400 transition shadow-sm"
                >
                  <span className="text-xs font-bold text-slate-900 block leading-snug">{item.title}</span>
                  <span className="text-[11px] text-slate-500 font-semibold block">{item.company}</span>
                  <span className="text-[10px] text-slate-400 font-medium block flex items-center space-x-1">
                    <Clock className="w-3 h-3 text-slate-400" />
                    <span>{item.updated}</span>
                  </span>

                  <div className="pt-2 flex items-center space-x-1 overflow-x-auto">
                    {['SAVED', 'APPLIED', 'INTERVIEWING', 'OFFER'].map((st) => (
                      <button
                        key={st}
                        onClick={() => moveItem(item.id, st)}
                        className="px-2 py-0.5 rounded text-[9px] font-bold bg-slate-100 hover:bg-blue-600 hover:text-white text-slate-700 transition"
                        title={`Move to ${st}`}
                      >
                        {st[0]}
                      </button>
                    ))}
                  </div>
                </div>
              ))}

              {col.items.length === 0 && (
                <div className="p-4 rounded-xl border border-dashed border-slate-300 text-[11px] text-slate-400 text-center font-medium">
                  No applications
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
