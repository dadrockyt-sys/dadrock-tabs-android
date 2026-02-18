import { locales } from '@/lib/i18n';

const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://dadrocktabs.com';

export default function sitemap() {
  const routes = [];
  
  // Add language routes
  locales.forEach(lang => {
    routes.push({
      url: lang === 'en' ? baseUrl : `${baseUrl}/${lang}`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: lang === 'en' ? 1 : 0.9,
      alternates: {
        languages: Object.fromEntries(
          locales.map(l => [l, l === 'en' ? baseUrl : `${baseUrl}/${l}`])
        ),
      },
    });
  });

  return routes;
}
