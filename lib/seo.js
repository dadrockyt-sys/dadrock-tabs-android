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
 * - English is the single search canonical for artist, song, tools, quickies,
 *   top-lessons and most other subpage route families.
 * - Locale-prefixed versions of those routes remain available to visitors but
 *   are not separate search canonicals.
 * - Localized homepages and individual localized Learn guides are exceptions:
 *   they are independently indexable and use self-canonicals + hreflang.
 */
export function generateCanonical(path = '') {
  return generateLocalizedUrl(path, 'en');
}

/**
 * Return the canonical metadata used by subpages that remain English-only in
 * search. Localized Learn guides do not use this helper; they explicitly use
 * generateLocalizedUrl() + generateHreflangLinks() because they are indexable.
 */
export function generateAlternates(path = '') {
  return {
    canonical: generateCanonical(path),
  };
}

/**
 * Explicit hreflang helper for route families that are indexable in every
 * language, currently the homepage and individual Learn guides.
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
