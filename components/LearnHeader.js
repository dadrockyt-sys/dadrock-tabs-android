'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import LanguageSelector from '@/components/LanguageSelector';
import { getSubPageTranslation } from '@/lib/subPageI18n';
import LanguageSelector, { useLanguage } from '@/components/LanguageSelector';

const supportedLanguages = [
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
  'fi'
];

export default function LearnHeader() {
  const pathname = usePathname();
  const { lang } = useLanguage();
  const pathLanguage = pathname.split('/')[1];

  const currentLang = supportedLanguages.includes(pathLanguage)
    ? pathLanguage
    : 'en';

  const t = getSubPageTranslation(currentLang);

  const homeHref =
    currentLang === 'en'
      ? '/'
      : `/${currentLang}`;

  const handleLanguageChange = (newLang) => {
  localStorage.setItem('dadrock-language', newLang);

  const parts = pathname.split('/').filter(Boolean);

  if (supportedLanguages.includes(parts[0])) {
    parts.shift();
  }

  if (parts[0] === 'learn') {
    parts.shift();
  }

  const basePath = `/learn/${slug}`;

  window.location.href =
    newLang === 'en'
      ? basePath
      : `/${newLang}${basePath}`;
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
