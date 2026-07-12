'use client';

import Link from 'next/link';
import LanguageSelector from '@/components/LanguageSelector';
import { usePathname } from 'next/navigation';
const headerT = {
  en: {
    home: 'Home'
  },
  es: {
    home: 'Inicio'
  }
};

export default function DifficultyHeader({ level }) {
  const pathname = usePathname();
  const pathLocale = pathname.split('/')[1];

  const supportedLocales = [
    'es', 'pt', 'pt-br', 'de', 'fr', 'it',
    'ja', 'ko', 'zh', 'ru', 'hi', 'sv', 'fi'
  ];

  const currentLang = supportedLocales.includes(pathLocale)
    ? pathLocale
    : 'en';
  const t = headerT[currentLang] || headerT.en;
  const homeHref = currentLang === 'en'
  ? '/'
  : `/${currentLang}`;

  return (
    <header className="sticky top-0 z-50 bg-zinc-950/95 border-b border-zinc-800">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between gap-4">
        <Link
          href={homeHref}
          className="flex items-center gap-3 hover:opacity-80 transition-opacity"
        >
          <img
            src="https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png"
            alt="DadRock Tabs"
            className="h-9 w-auto"
          />
          <span className="text-lg font-bold text-amber-500 hidden sm:block">
            DadRock Tabs
          </span>
        </Link>

        <div className="flex items-center gap-3">
          <LanguageSelector
            onLanguageChange={(newLang) => {
              window.location.href =
                newLang === 'en'
                  ? `/difficulty/${level}`
                  : `/${newLang}/difficulty/${level}`;
            }}
          />

          <Link
            href={homeHref}
            className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-full transition-colors"
          >
            {t.home}
          </Link>
        </div>
      </div>
    </header>
  );
}
