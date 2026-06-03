const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://dadrocktabs.com';

// All supported non-English locales
const blockedLocales = ['es', 'pt', 'pt-br', 'de', 'fr', 'it', 'ja', 'ko', 'zh', 'ru', 'hi', 'sv', 'fi'];

export default function robots() {
  // Generate disallow rules for all locale-prefixed paths
  // This prevents Google from wasting crawl budget on non-existent locale subpages
  const localeDisallows = blockedLocales.flatMap(locale => [
    `/${locale}/artist/`,
    `/${locale}/songs/`,
    `/${locale}/coming-soon`,
    `/${locale}/top-lessons`,
    `/${locale}/quickies`,
    `/${locale}/learn/`,
    `/${locale}/genre/`,
    `/${locale}/era/`,
    `/${locale}/difficulty/`,
    `/${locale}/playlist/`,
    `/${locale}/tools`,
    `/${locale}/whats-new`,
    `/${locale}/embed/`,
  ]);

  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: [
          '/api/',
          '/admin',
          '/search',
          '/sitemap-*.xml',
          '/embed/',
          '/*?search=',
          '/*?utm_',
          '/*?q=',
          ...localeDisallows,
        ],
      },
    ],
    sitemap: [
      `${baseUrl}/sitemap.xml`,
      `${baseUrl}/video-sitemap.xml`,
    ],
  };
}
