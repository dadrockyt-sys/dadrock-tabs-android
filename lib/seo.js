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
 * Generate the canonical URL for the specific language version being served.
 * English is the default locale and therefore has no /en prefix.
 */
export function generateCanonical(path = '', locale = 'en') {
  return generateLocalizedUrl(path, locale);
}

/**
 * Generate consistent canonical + hreflang metadata for route families that
 * exist in every supported language. English is also exposed as x-default.
 */
export function generateAlternates(path = '', locale = 'en') {
  const languages = {};

  for (const supportedLocale of locales) {
    languages[supportedLocale] = generateLocalizedUrl(
      path,
      supportedLocale
    );
  }

  languages['x-default'] = generateLocalizedUrl(path, 'en');

  return {
    canonical: generateCanonical(path, locale),
    languages,
  };
}

export function generateHreflangLinks(path = '') {
  return generateAlternates(path, 'en').languages;
}
