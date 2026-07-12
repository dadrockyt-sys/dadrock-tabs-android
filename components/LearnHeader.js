'use client';

import Link from 'next/link';
import LanguageSelector, { useLanguage } from '@/components/LanguageSelector';

export default function LearnHeader() {
  const { lang } = useLanguage();

  return (
    <header className="sticky top-0 z-50 border-b border-zinc-800 bg-zinc-950/95 backdrop-blur">
      <div className="container mx-auto flex items-center justify-between px-4 py-4 max-w-5xl">
        <Link href={lang === 'en' ? '/' : `/${lang}`} className="flex items-center">
          <img
            src="https://customer-assets.emergentagent.com/job_tabs-guitar/artifacts/j2jx9l1j_dadrock-logo.png"
            alt="DadRock Tabs"
            className="h-9 w-auto"
          />
        </Link>

        <div className="flex items-center gap-3">
          <LanguageSelector />

          <Link
            href={lang === 'en' ? '/' : `/${lang}`}
            className="rounded-xl bg-zinc-800 px-5 py-3 font-medium hover:bg-zinc-700 transition-colors"
          >
            Home
          </Link>
        </div>
      </div>
    </header>
  );
}
