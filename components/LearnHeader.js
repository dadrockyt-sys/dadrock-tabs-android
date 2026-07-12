'use client';

import Link from 'next/link';
import LanguageSelector, { useLanguage } from '@/components/LanguageSelector';
import { getSubPageTranslation } from '@/lib/subPageI18n';

export default function LearnHeader() {
  const { lang } = useLanguage();
  const currentLang = lang || 'en';
  const t = getSubPageTranslation(currentLang);

  const homeHref =
    currentLang === 'en'
      ? '/'
      : `/${currentLang}`;

  const handleLanguageChange = (newLang) => {
    localStorage.setItem('dadrock-language', newLang);
    window.location.href = '/learn';
  };

  return (
    <header className="border-b border-zinc-800 bg-zinc-950">
      <div className="container mx-auto flex max-w-5xl items-center justify-between px-4 py-5">
        <Link
          href={homeHref}
          className="flex items-center gap-2 text-zinc-300 transition-colors hover:text-white"
        >
          <span className="text-xl">⌂</span>
          <span>{t.backToHome}</span>
        </Link>

        <LanguageSelector onLanguageChange={handleLanguageChange} />
      </div>
    </header>
  );
}
