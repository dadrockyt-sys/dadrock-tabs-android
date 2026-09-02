const SITE_URL = 'https://dadrocktabs.com';

const locales = [
  'en',
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

function normalizePath(path = '') {
  if (!path || path === '/') return '';
  return path.startsWith('/') ? path : `/${path}`;
}

export function generateLocalizedUrl(path = '', locale = 'en') {
  const cleanPath = normalizePath(path);

  if (!locale || locale === 'en') {
    return `${SITE_URL}${cleanPath}`;
  }

  return `${SITE_URL}/${locale}${cleanPath}`;
}

/**
 * Canonical policy for non-homepage routes:
 *
 * - English is the single search canonical for artist, song, learn, tools,
 *   quickies, top-lessons and other subpage route families.
 * - Locale-prefixed subpages remain available for visitors, but they are UI
 *   variants and must not declare themselves as separate search canonicals.
 * - Language homepages are the exception. app/[lang]/page.js owns their
 *   self-canonical + hreflang metadata because those homepages are intended
 *   to be independently indexable.
 */
export function generateCanonical(path = '') {
  return generateLocalizedUrl(path, 'en');
}

/**
 * Return the canonical metadata used by subpages. Deliberately do not emit
 * hreflang here: translated subpages are not part of the indexable URL set.
 * Keeping only the English canonical also aligns the HTML signal with the
 * XML sitemap instead of asking Google to choose between conflicting URLs.
 */
export function generateAlternates(path = '') {
  return {
    canonical: generateCanonical(path),
  };
}

/**
 * Explicit hreflang helper for route families that really are indexable in
 * every language. At present this should only be used for the homepage.
 */
export function generateHreflangLinks(path = '') {
  const languages = {};

  for (const supportedLocale of locales) {
    languages[supportedLocale] = generateLocalizedUrl(
      path,
      supportedLocale
    );
  }

  languages['x-default'] = generateLocalizedUrl(path, 'en');
  return languages;
}
