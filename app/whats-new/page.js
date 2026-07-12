'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import LanguageSelector, { useLanguage } from '@/components/LanguageSelector';

export default function WhatsNewPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const { lang } = useLanguage();
  const pathname = usePathname();
  const pathLocale = pathname.split('/')[1];

  const supportedLocales = [
    'es',
    'pt',
    'pt-br',
    'de',
    'fr',
    'it',
    'ja',
    'ko',
    'zh',
    'ru',
    'hi',
    'sv',
    'fi',
  ];

  const currentLang = supportedLocales.includes(pathLocale)
    ? pathLocale
    : 'en';

  const whatsNewT = {
    en: {
      backHome: '← Back to Home',
      pageTitle: "🆕 What's New",
      latestAdditions: 'Latest Additions',
      subtitle: 'Fresh tabs and tutorials added to DadRock Tabs',
      totalSongs: 'Total Songs',
      communityReviews: 'Community Reviews',
      loading: 'Loading...',
      recentlyAdded: 'Recently added',
      stayUpdated: 'Stay updated with new additions:',
      rss: '📡 Subscribe to RSS Feed',
    },

    es: {
      backHome: '← Volver al inicio',
      pageTitle: '🆕 Novedades',
      latestAdditions: 'Últimas incorporaciones',
      subtitle: 'Nuevas tablaturas y tutoriales añadidos a DadRock Tabs',
      totalSongs: 'Canciones totales',
      communityReviews: 'Reseñas de la comunidad',
      loading: 'Cargando...',
      recentlyAdded: 'Añadido recientemente',
      stayUpdated: 'Mantente al día con las nuevas incorporaciones:',
      rss: '📡 Suscribirse al canal RSS',
    },
  };

  const t = whatsNewT[currentLang] || whatsNewT.en;
  const homeHref = currentLang === 'en' ? '/' : `/${currentLang}`;

  useEffect(() => {
    fetch('/api/whats-new')
      .then((r) => r.json())
      .then((d) => setData(d))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const formatDate = (dateStr) => {
    if (!dateStr) return t.recentlyAdded;

    const localeMap = {
  en: 'en-US',
  es: 'es-ES',
  pt: 'pt-PT',
  'pt-br': 'pt-BR',
  de: 'de-DE',
  fr: 'fr-FR',
  it: 'it-IT',
  ja: 'ja-JP',
  ko: 'ko-KR',
  zh: 'zh-CN',
  ru: 'ru-RU',
  hi: 'hi-IN',
  sv: 'sv-SE',
  fi: 'fi-FI',
};
    };

    const d = new Date(dateStr);

    return d.toLocaleDateString(localeMap[currentLang] || 'en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="border-b border-gray-800 py-4 px-6">
        <div className="max-w-4xl mx-auto flex items-center justify-between gap-4">
          <Link
            href={homeHref}
            className="text-orange-400 hover:text-orange-300 flex items-center gap-2"
          >
            {t.backHome}
          </Link>

          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-orange-400">
              {t.pageTitle}
            </h1>

            <LanguageSelector
              onLanguageChange={(newLang) => {
                window.location.href =
                  newLang === 'en'
                    ? '/whats-new'
                    : `/${newLang}/whats-new`;
              }}
            />
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-white mb-2">
            {t.latestAdditions}
          </h2>

          <p className="text-gray-400">{t.subtitle}</p>

          {data?.stats && (
            <div className="flex justify-center gap-6 mt-4">
              <div className="text-center">
                          <div className="text-center">
                <span className="text-2xl font-bold text-orange-400">
                  {data.stats.totalSongs}
                </span>
                <span className="text-gray-500 text-sm block">
                  {t.totalSongs}
                </span>
              </div>

              <div className="text-center">
                <span className="text-2xl font-bold text-yellow-400">
                  {data.stats.totalComments}
                </span>
                <span className="text-gray-500 text-sm block">
                  {t.communityReviews}
                </span>
              </div>
            </div>
          )}
        </div>

        {loading ? (
          <div className="text-center text-gray-500">
            {t.loading}
          </div>
        ) : (
          <div className="space-y-3">
            {(data?.recentSongs || []).map((song, i) => (
              <Link
                key={song.slug || i}
                href={
                  currentLang === 'en'
                    ? `/songs/${song.slug}`
                    : `/${currentLang}/songs/${song.slug}`
                }
                className="block bg-gray-900/50 hover:bg-gray-800/50 border border-gray-700/50 hover:border-orange-500/30 rounded-xl p-4 transition-all"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-orange-400 font-bold text-lg w-8">
                      #{i + 1}
                    </span>

                    <div>
                      <h3 className="font-semibold text-white">
                        {song.title}
                      </h3>
                      <p className="text-sm text-gray-400">
                        {song.artist}
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    {song.difficulty && (
                                          {song.difficulty && (
                      <span className="text-xs bg-orange-900/50 text-orange-300 px-2 py-1 rounded">
                        {song.difficulty}
                      </span>
                    )}

                    {song.avgRating && (
                      <div className="text-yellow-400 text-xs mt-1">
                        {'★'.repeat(Math.round(song.avgRating))}
                      </div>
                    )}

                    <p className="text-xs text-gray-500 mt-1">
                      {formatDate(song.created_at)}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        <div className="mt-10 text-center">
          <p className="text-gray-500 text-sm mb-2">
            {t.stayUpdated}
          </p>

          <a
            href="/api/rss"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-500 text-white rounded-lg font-semibold text-sm transition-colors"
          >
            {t.rss}
          </a>
        </div>
      </main>
    </div>
  );
}
