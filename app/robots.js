const baseUrl =
  process.env.NEXT_PUBLIC_BASE_URL ||
  'https://dadrocktabs.com';

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
          '/embed/',
          '/*?search=',
          '/*?utm_',
          '/*?q=',
        ],
      },
    ],
    sitemap: [
      `${baseUrl}/sitemap.xml`,
      `${baseUrl}/video-sitemap.xml`,
    ],
  };
}
