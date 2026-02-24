import { locales } from '@/lib/i18n';

// Use non-www as canonical (matches your redirect setup)
const baseUrl = 'https://dadrocktabs.com';

export default function sitemap() {
  const routes = [];
  const currentDate = new Date().toISOString();
  
  // Add language routes
  locales.forEach(lang => {
    routes.push({
      url: lang === 'en' ? baseUrl : `${baseUrl}/${lang}`,
      lastModified: currentDate,
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
