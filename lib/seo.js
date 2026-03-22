import { locales } from './i18n';

const SITE_URL = 'https://dadrocktabs.com';

/**
 * Generate hreflang alternate links for all supported languages.
 * Used in Next.js metadata.alternates.languages
 * @param {string} path - The page path (e.g., '/quickies', '/artist/led-zeppelin')
 * @returns {object} languages object for metadata.alternates
 */
export function generateHreflangLinks(path = '') {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  const languages = {};
  
  for (const locale of locales) {
    if (locale === 'en') {
      languages[locale] = `${SITE_URL}${cleanPath}`;
    } else {
      languages[locale] = `${SITE_URL}/${locale}${cleanPath}`;
    }
  }
  
  // x-default points to the English version
  languages['x-default'] = `${SITE_URL}${cleanPath}`;
  
  return languages;
}

/**
 * Generate canonical URL for a given page path
 * @param {string} path - The page path
 * @returns {string} canonical URL
 */
export function generateCanonical(path = '') {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${SITE_URL}${cleanPath}`;
}

/**
 * Generate full alternates metadata object for Next.js
 * @param {string} path - The page path
 * @returns {object} alternates object for metadata
 */
export function generateAlternates(path = '') {
  return {
    canonical: generateCanonical(path),
    languages: generateHreflangLinks(path),
  };
}
