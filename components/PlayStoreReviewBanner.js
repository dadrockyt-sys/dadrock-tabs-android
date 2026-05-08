'use client';

import { useState, useEffect } from 'react';
import { Star, X } from 'lucide-react';

const PLAY_STORE_URL = 'https://play.google.com/store/apps/details?id=com.dadrocktabs.app';
const VISITS_BEFORE_PROMPT = 3;
const COOLDOWN_DAYS = 30;

/**
 * PlayStoreReviewBanner — Shows a subtle banner prompting mobile web users
 * to rate the app on Google Play after their 3rd visit.
 * Dismissible, with a 30-day cooldown after dismissal.
 */
export default function PlayStoreReviewBanner() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    // Only show on mobile devices (not in Android WebView — the app handles reviews natively)
    const ua = navigator.userAgent || '';
    const isMobile = /Android|iPhone|iPad|iPod|Mobile/i.test(ua);
    const isWebView = /wv\)|; wv\)/i.test(ua);
    if (!isMobile || isWebView) return;

    try {
      const now = Date.now();
      const visitCount = parseInt(localStorage.getItem('dadrock_visit_count') || '0', 10) + 1;
      const dismissed = parseInt(localStorage.getItem('dadrock_review_dismissed') || '0', 10);

      // Save updated visit count
      localStorage.setItem('dadrock_visit_count', String(visitCount));

      // Check cooldown (30 days since last dismissal)
      if (dismissed && (now - dismissed) < COOLDOWN_DAYS * 24 * 60 * 60 * 1000) return;

      // Show after Nth visit
      if (visitCount >= VISITS_BEFORE_PROMPT) {
        // Delay showing by 5 seconds so it doesn't interrupt initial page load
        const timer = setTimeout(() => setShow(true), 5000);
        return () => clearTimeout(timer);
      }
    } catch (e) {
      // localStorage might be unavailable
    }
  }, []);

  const handleDismiss = () => {
    setShow(false);
    try {
      localStorage.setItem('dadrock_review_dismissed', String(Date.now()));
    } catch (e) {}
  };

  if (!show) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 animate-in slide-in-from-bottom duration-500">
      <div className="max-w-lg mx-auto bg-zinc-900 border border-amber-500/30 rounded-2xl p-4 shadow-2xl shadow-amber-500/10">
        <button
          onClick={handleDismiss}
          className="absolute top-3 right-3 text-zinc-500 hover:text-white transition-colors"
          aria-label="Dismiss"
        >
          <X className="w-5 h-5" />
        </button>
        
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-12 h-12 bg-amber-500/20 rounded-xl flex items-center justify-center">
            <Star className="w-7 h-7 text-amber-400" fill="currentColor" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white font-bold text-sm">Enjoying DadRock Tabs?</p>
            <p className="text-zinc-400 text-xs mt-1">
              Help us out with a quick rating on Google Play — it really helps other guitarists find us!
            </p>
            <div className="flex items-center gap-3 mt-3">
              <a
                href={PLAY_STORE_URL}
                target="_blank"
                rel="noopener noreferrer"
                onClick={handleDismiss}
                className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs rounded-full transition-colors"
              >
                ⭐ Rate Us
              </a>
              <button
                onClick={handleDismiss}
                className="px-4 py-2 text-zinc-400 hover:text-white text-xs transition-colors"
              >
                Maybe Later
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
