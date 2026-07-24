'use client';

import Link from 'next/link';

export default function AiTabButton({
  song,
  artist,
  lang = 'en',
  stopPropagation = true,
}) {
  const basePath = lang && lang !== 'en' ? `/${lang}/ai-tab` : '/ai-tab';

  const href =
    `${basePath}?song=${encodeURIComponent(song || 'Selected Song')}` +
    `&artist=${encodeURIComponent(artist || 'Unknown Artist')}`;

  return (
    <Link
      href={href}
      onClick={(event) => {
        if (stopPropagation) {
          event.stopPropagation();
        }
      }}
      className="mt-4 block w-full rounded-xl border border-amber-400/70 bg-gradient-to-r from-amber-500 via-orange-500 to-red-600 px-4 py-3 text-left text-white shadow-lg shadow-orange-500/20 transition-all hover:scale-[1.02] hover:shadow-orange-500/40"
    >
      <span className="block text-base font-bold">
        🎸 AI Tab Generator
      </span>

      <span className="mt-1 block text-xs text-white/90">
        Create a printable PDF of this song using AI.
      </span>
    </Link>
  );
}
