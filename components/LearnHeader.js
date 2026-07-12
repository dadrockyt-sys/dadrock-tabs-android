'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import LanguageSelector from '@/components/LanguageSelector';
import { getSubPageTranslation } from '@/lib/subPageI18n';

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
  const pathLanguage = pathname.split('/')[1];

  const currentLang = supportedLanguages.includes(pathLanguage)
    ? pathLanguage
    : 'en';

  const t = getSubPageTranslation(currentLang);

  const homeHref = currentLang === 'en'
    ? '/'
    : `/${currentLang}`;

  const handleLanguageChange = (newLang) => {
    window.location.href =
      newLang === 'en'
        ? '/learn'
        : `/${newLang}/learn`;
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
