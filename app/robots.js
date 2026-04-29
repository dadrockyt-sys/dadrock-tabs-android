const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://dadrocktabs.com';

export default function robots() {
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
          '/zn',
          '/zn/',
        ],
      },
    ],
    sitemap: [
      `${baseUrl}/sitemap.xml`,
      `${baseUrl}/video-sitemap.xml`,
    ],
  };
}
