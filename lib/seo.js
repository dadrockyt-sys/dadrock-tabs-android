const SITE_URL = 'https://dadrocktabs.com';

/**
 * Generate canonical URL for a given page path.
 * All pages now point canonical to the English version only.
 * Locale-prefixed URLs are no longer generated as alternates
 * to prevent "Alternate page with proper canonical tag" GSC errors.
 * 
 * @param {string} path - The page path
 * @returns {string} canonical URL
 */
export function generateCanonical(path = '') {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${SITE_URL}${cleanPath}`;
}

/**
 * Generate alternates metadata for Next.js pages.
 * Only includes canonical (English). No hreflang alternates for subpages
 * since locale-prefixed subpages (e.g., /de/songs/...) don't exist as routes.
 * 
 * @param {string} path - The page path
 * @returns {object} alternates object for metadata
 */
export function generateAlternates(path = '') {
  return {
    canonical: generateCanonical(path),
  };
}

/**
 * @deprecated Use generateAlternates instead. Hreflang links removed to fix GSC errors.
 */
export function generateHreflangLinks(path = '') {
  // No longer generating hreflang for subpages
  return {};
}
