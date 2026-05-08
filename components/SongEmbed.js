'use client';

import { useState } from 'react';

export default function SongEmbed({ song }) {
  const [showCode, setShowCode] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!song) return null;

  const baseUrl = typeof window !== 'undefined' ? window.location.origin : '';
  const embedUrl = `${baseUrl}/embed/${song.slug}`;
  const embedCode = `<iframe src="${embedUrl}" width="420" height="200" frameborder="0" style="border-radius:12px;border:2px solid #ff4500;"></iframe>`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(embedCode).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="mt-4">
      <button
        onClick={() => setShowCode(!showCode)}
        className="text-sm text-orange-400 hover:text-orange-300 flex items-center gap-1 transition-colors"
      >
        <span>{'</>'}</span> {showCode ? 'Hide' : 'Get'} Embed Code
      </button>

      {showCode && (
        <div className="mt-3 bg-gray-800/80 border border-gray-700 rounded-lg p-4">
          <p className="text-xs text-gray-400 mb-2">Share this song on your blog or forum:</p>
          <div className="relative">
            <pre className="text-xs text-green-400 bg-gray-900 p-3 rounded overflow-x-auto">
              {embedCode}
            </pre>
            <button
              onClick={copyToClipboard}
              className="absolute top-2 right-2 px-2 py-1 bg-orange-600 hover:bg-orange-500 text-white text-xs rounded transition-colors"
            >
              {copied ? '✓ Copied!' : 'Copy'}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">This widget links back to DadRock Tabs, helping others discover your favorite tabs.</p>
        </div>
      )}
    </div>
  );
}
