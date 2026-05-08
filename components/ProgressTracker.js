'use client';

import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'dadrock_progress';

// Status options: null (not tracked), 'want', 'learning', 'learned'
const STATUS_CONFIG = {
  want: { label: 'Want to Learn', icon: '📌', color: 'bg-blue-500/20 text-blue-400 border-blue-500/50', hoverColor: 'hover:bg-blue-500/30' },
  learning: { label: 'Learning', icon: '🎯', color: 'bg-amber-500/20 text-amber-400 border-amber-500/50', hoverColor: 'hover:bg-amber-500/30' },
  learned: { label: 'Learned', icon: '✅', color: 'bg-green-500/20 text-green-400 border-green-500/50', hoverColor: 'hover:bg-green-500/30' },
};

function getProgress() {
  if (typeof window === 'undefined') return {};
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : {};
  } catch {
    return {};
  }
}

function saveProgress(progress) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  } catch {
    // localStorage full or unavailable
  }
}

export default function ProgressTracker({ songSlug, songTitle, compact = false }) {
  const [status, setStatus] = useState(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const progress = getProgress();
    setStatus(progress[songSlug] || null);
  }, [songSlug]);

  const updateStatus = useCallback((newStatus) => {
    const progress = getProgress();
    if (newStatus === status) {
      // Toggle off
      delete progress[songSlug];
      setStatus(null);
    } else {
      progress[songSlug] = newStatus;
      setStatus(newStatus);
    }
    saveProgress(progress);
    setIsOpen(false);
  }, [songSlug, status]);

  if (compact) {
    // Compact version for song lists
    const config = status ? STATUS_CONFIG[status] : null;
    return (
      <div className="relative">
        <button
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); setIsOpen(!isOpen); }}
          className={`px-2 py-1 rounded-lg text-xs font-medium border transition-all ${
            config 
              ? config.color 
              : 'bg-zinc-800/50 text-zinc-500 border-zinc-700 hover:border-zinc-500'
          }`}
          title="Track progress"
        >
          {config ? `${config.icon} ${config.label}` : '📋'}
        </button>
        
        {isOpen && (
          <div className="absolute right-0 top-full mt-1 z-50 bg-zinc-800 rounded-lg border border-zinc-700 shadow-xl p-1 min-w-[140px]">
            {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
              <button
                key={key}
                onClick={(e) => { e.preventDefault(); e.stopPropagation(); updateStatus(key); }}
                className={`w-full text-left px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  status === key ? cfg.color : `text-zinc-300 ${cfg.hoverColor}`
                }`}
              >
                {cfg.icon} {cfg.label}
              </button>
            ))}
            {status && (
              <button
                onClick={(e) => { e.preventDefault(); e.stopPropagation(); updateStatus(status); }}
                className="w-full text-left px-3 py-1.5 rounded-md text-xs text-zinc-500 hover:text-red-400 hover:bg-red-500/10 transition-all"
              >
                ✕ Remove
              </button>
            )}
          </div>
        )}
      </div>
    );
  }

  // Full version for song detail pages
  const config = status ? STATUS_CONFIG[status] : null;

  return (
    <div className="flex flex-col gap-2">
      <p className="text-xs text-zinc-500 uppercase tracking-wider font-medium">Track Your Progress</p>
      <div className="flex flex-wrap gap-2">
        {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
          <button
            key={key}
            onClick={() => updateStatus(key)}
            className={`px-4 py-2 rounded-xl text-sm font-medium border transition-all ${
              status === key
                ? `${cfg.color} ring-1 ring-offset-1 ring-offset-zinc-900`
                : `bg-zinc-800/50 text-zinc-400 border-zinc-700 ${cfg.hoverColor} hover:text-white`
            }`}
          >
            {cfg.icon} {cfg.label}
          </button>
        ))}
      </div>
      {config && (
        <p className="text-xs text-zinc-500 mt-1">
          {status === 'want' && `"${songTitle}" added to your wish list`}
          {status === 'learning' && `Keep practicing "${songTitle}" — you've got this! 🎸`}
          {status === 'learned' && `Congrats! You've mastered "${songTitle}" 🏆`}
        </p>
      )}
    </div>
  );
}

// Stats component for homepage or profile
export function ProgressStats() {
  const [stats, setStats] = useState({ want: 0, learning: 0, learned: 0, total: 0 });

  useEffect(() => {
    const progress = getProgress();
    const counts = { want: 0, learning: 0, learned: 0, total: 0 };
    for (const status of Object.values(progress)) {
      if (counts[status] !== undefined) {
        counts[status]++;
        counts.total++;
      }
    }
    setStats(counts);
  }, []);

  if (stats.total === 0) return null;

  return (
    <div className="flex items-center gap-4 p-4 bg-zinc-900/50 rounded-xl border border-zinc-800">
      <div className="text-sm font-medium text-zinc-300">Your Progress:</div>
      {stats.learned > 0 && (
        <span className="text-xs px-2 py-1 rounded-lg bg-green-500/20 text-green-400">
          ✅ {stats.learned} learned
        </span>
      )}
      {stats.learning > 0 && (
        <span className="text-xs px-2 py-1 rounded-lg bg-amber-500/20 text-amber-400">
          🎯 {stats.learning} learning
        </span>
      )}
      {stats.want > 0 && (
        <span className="text-xs px-2 py-1 rounded-lg bg-blue-500/20 text-blue-400">
          📌 {stats.want} want to learn
        </span>
      )}
    </div>
  );
}
