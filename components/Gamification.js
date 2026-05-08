'use client';

import { useState, useEffect, useCallback } from 'react';

const BADGES = [
  { id: 'first_song', name: 'First Riff', desc: 'Learn your first song', icon: '🎸', requirement: 1 },
  { id: 'five_songs', name: 'Jam Session', desc: 'Learn 5 songs', icon: '🎶', requirement: 5 },
  { id: 'ten_songs', name: 'Rock Solid', desc: 'Learn 10 songs', icon: '🤘', requirement: 10 },
  { id: 'twenty_songs', name: 'Guitar Hero', desc: 'Learn 20 songs', icon: '⚡', requirement: 20 },
  { id: 'fifty_songs', name: 'Legend', desc: 'Learn 50 songs', icon: '🏆', requirement: 50 },
  { id: 'streak_3', name: 'On Fire', desc: '3-day streak', icon: '🔥', requirement: 3, type: 'streak' },
  { id: 'streak_7', name: 'Unstoppable', desc: '7-day streak', icon: '💪', requirement: 7, type: 'streak' },
  { id: 'streak_30', name: 'Iron Will', desc: '30-day streak', icon: '🦾', requirement: 30, type: 'streak' },
];

const XP_PER_SONG = 50;
const XP_PER_VISIT = 10;
const XP_PER_STREAK_DAY = 25;

function getLevel(xp) {
  if (xp < 100) return { level: 1, title: 'Beginner', next: 100 };
  if (xp < 300) return { level: 2, title: 'Novice', next: 300 };
  if (xp < 600) return { level: 3, title: 'Intermediate', next: 600 };
  if (xp < 1000) return { level: 4, title: 'Advanced', next: 1000 };
  if (xp < 1500) return { level: 5, title: 'Expert', next: 1500 };
  if (xp < 2500) return { level: 6, title: 'Master', next: 2500 };
  if (xp < 4000) return { level: 7, title: 'Virtuoso', next: 4000 };
  return { level: 8, title: 'Rock God', next: null };
}

export function useGamification() {
  const [stats, setStats] = useState({ xp: 0, streak: 0, songsLearned: 0, badges: [], lastVisit: null });

  useEffect(() => {
    const saved = localStorage.getItem('dadrock_gamification');
    if (saved) {
      const data = JSON.parse(saved);
      setStats(data);
      // Check streak on load
      updateStreak(data);
    } else {
      // First visit
      const initial = { xp: XP_PER_VISIT, streak: 1, songsLearned: 0, badges: [], lastVisit: new Date().toDateString() };
      setStats(initial);
      localStorage.setItem('dadrock_gamification', JSON.stringify(initial));
    }
  }, []);

  const updateStreak = useCallback((data) => {
    const today = new Date().toDateString();
    if (data.lastVisit === today) return; // Already visited today

    const yesterday = new Date(Date.now() - 86400000).toDateString();
    let newStreak = data.lastVisit === yesterday ? data.streak + 1 : 1;
    let newXp = data.xp + XP_PER_VISIT + (newStreak > 1 ? XP_PER_STREAK_DAY : 0);

    const updated = { ...data, streak: newStreak, xp: newXp, lastVisit: today };
    // Check streak badges
    const newBadges = checkBadges(updated);
    updated.badges = [...new Set([...(data.badges || []), ...newBadges])];

    setStats(updated);
    localStorage.setItem('dadrock_gamification', JSON.stringify(updated));
  }, []);

  const addSongLearned = useCallback((songTitle) => {
    setStats(prev => {
      const updated = {
        ...prev,
        xp: prev.xp + XP_PER_SONG,
        songsLearned: prev.songsLearned + 1,
      };
      const newBadges = checkBadges(updated);
      updated.badges = [...new Set([...(prev.badges || []), ...newBadges])];
      localStorage.setItem('dadrock_gamification', JSON.stringify(updated));
      return updated;
    });
  }, []);

  return { stats, addSongLearned, getLevel: () => getLevel(stats.xp), BADGES };
}

function checkBadges(stats) {
  const earned = [];
  BADGES.forEach(badge => {
    if (badge.type === 'streak') {
      if (stats.streak >= badge.requirement) earned.push(badge.id);
    } else {
      if (stats.songsLearned >= badge.requirement) earned.push(badge.id);
    }
  });
  return earned;
}

export default function GamificationPanel({ compact = false }) {
  const { stats, getLevel: getLevelInfo, BADGES: allBadges } = useGamification();
  const levelInfo = getLevelInfo();
  const progressPercent = levelInfo.next ? ((stats.xp % (levelInfo.next - (levelInfo.level > 1 ? [0,0,100,300,600,1000,1500,2500][levelInfo.level-1] : 0))) / (levelInfo.next - (levelInfo.level > 1 ? [0,0,100,300,600,1000,1500,2500][levelInfo.level-1] : 0))) * 100 : 100;

  if (compact) {
    return (
      <div className="flex items-center gap-3 bg-gradient-to-r from-orange-900/30 to-red-900/30 border border-orange-500/30 rounded-lg px-4 py-2">
        <span className="text-orange-400 font-bold text-sm">Lv.{levelInfo.level}</span>
        <span className="text-xs text-gray-400">{levelInfo.title}</span>
        <span className="text-orange-300 text-xs">{stats.xp} XP</span>
        {stats.streak > 1 && <span className="text-xs">🔥 {stats.streak} day streak</span>}
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-orange-500/30 rounded-xl p-6 shadow-lg shadow-orange-900/10">
      {/* Level & XP */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-orange-400 font-bold text-lg">Level {levelInfo.level}: {levelInfo.title}</h3>
          <p className="text-gray-400 text-sm">{stats.xp} XP total</p>
        </div>
        <div className="text-right">
          {stats.streak > 0 && (
            <div className="text-orange-300">
              <span className="text-2xl">🔥</span>
              <span className="font-bold text-lg ml-1">{stats.streak}</span>
              <span className="text-xs text-gray-400 block">day streak</span>
            </div>
          )}
        </div>
      </div>

      {/* XP Progress Bar */}
      {levelInfo.next && (
        <div className="mb-4">
          <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-orange-500 to-yellow-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, progressPercent)}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">{stats.xp} / {levelInfo.next} XP to next level</p>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="text-center p-2 bg-gray-800/50 rounded-lg">
          <div className="text-xl font-bold text-yellow-400">{stats.songsLearned}</div>
          <div className="text-xs text-gray-400">Songs Learned</div>
        </div>
        <div className="text-center p-2 bg-gray-800/50 rounded-lg">
          <div className="text-xl font-bold text-orange-400">{stats.streak}</div>
          <div className="text-xs text-gray-400">Day Streak</div>
        </div>
        <div className="text-center p-2 bg-gray-800/50 rounded-lg">
          <div className="text-xl font-bold text-red-400">{(stats.badges || []).length}</div>
          <div className="text-xs text-gray-400">Badges</div>
        </div>
      </div>

      {/* Badges */}
      <div>
        <h4 className="text-sm font-semibold text-gray-300 mb-2">Badges</h4>
        <div className="flex flex-wrap gap-2">
          {allBadges.map(badge => {
            const earned = (stats.badges || []).includes(badge.id);
            return (
              <div
                key={badge.id}
                className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
                  earned
                    ? 'bg-orange-900/50 border border-orange-500/50 text-orange-200'
                    : 'bg-gray-800 border border-gray-700 text-gray-500'
                }`}
                title={badge.desc}
              >
                <span className={earned ? '' : 'grayscale opacity-40'}>{badge.icon}</span>
                <span>{badge.name}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
