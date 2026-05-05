'use client';

import { useState } from 'react';

export default function ShareCard({ song, type = 'learned', value = '' }) {
  const [showShare, setShowShare] = useState(false);

  if (!song && type === 'learned') return null;

  const baseUrl = typeof window !== 'undefined' ? window.location.origin : '';
  const cardUrl = `${baseUrl}/api/share-card?song=${encodeURIComponent(song?.title || '')}&artist=${encodeURIComponent(song?.artist || '')}&type=${type}&value=${encodeURIComponent(value)}`;
  const pageUrl = song ? `${baseUrl}/songs/${song.slug}` : baseUrl;

  const shareText = type === 'learned'
    ? `I just learned "${song?.title}" by ${song?.artist} on DadRock Tabs! 🎸🔥`
    : type === 'streak'
      ? `${value} day guitar practice streak! 🔥🎸 @DadRockTabs`
      : `Achievement unlocked: ${value}! 🤘 @DadRockTabs`;

  const shareLinks = {
    twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(pageUrl)}`,
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(pageUrl)}&quote=${encodeURIComponent(shareText)}`,
    reddit: `https://www.reddit.com/submit?url=${encodeURIComponent(pageUrl)}&title=${encodeURIComponent(shareText)}`,
  };

  return (
    <div className="inline-block">
      <button
        onClick={() => setShowShare(!showShare)}
        className="text-sm bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white px-3 py-1.5 rounded-lg font-semibold flex items-center gap-1.5 transition-all"
      >
        <span>📤</span> Share
      </button>

      {showShare && (
        <div className="mt-2 bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-xl min-w-[280px]">
          <p className="text-xs text-gray-400 mb-3">Share your achievement:</p>
          <div className="flex gap-2 mb-3">
            <a
              href={shareLinks.twitter}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 py-2 bg-blue-500 hover:bg-blue-600 text-white text-xs font-bold rounded text-center transition-colors"
            >
              𝕏 Twitter
            </a>
            <a
              href={shareLinks.facebook}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 py-2 bg-blue-700 hover:bg-blue-800 text-white text-xs font-bold rounded text-center transition-colors"
            >
              Facebook
            </a>
            <a
              href={shareLinks.reddit}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 py-2 bg-orange-700 hover:bg-orange-800 text-white text-xs font-bold rounded text-center transition-colors"
            >
              Reddit
            </a>
          </div>
          {/* Preview card image */}
          <div className="border border-gray-600 rounded overflow-hidden">
            <img src={cardUrl} alt="Share card preview" className="w-full h-auto" loading="lazy" />
          </div>
        </div>
      )}
    </div>
  );
}
