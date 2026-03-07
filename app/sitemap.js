import { locales } from '@/lib/i18n';
import { getDb } from '@/lib/mongodb';

// Use non-www as canonical (matches your redirect setup)
const baseUrl = 'https://dadrocktabs.com';

// Convert artist name to URL slug
function artistToSlug(artistName) {
  const specialCases = {
    'AC/DC': 'acdc',
    "Guns N' Roses": 'guns-n-roses',
    'Motörhead': 'motorhead',
    'Blue Öyster Cult': 'blue-oyster-cult',
    'Mötley Crüe': 'motley-crue',
  };
  
  if (specialCases[artistName]) {
    return specialCases[artistName];
  }
  
  return artistName
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
}

export default async function sitemap() {
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

  // Add artist pages
  try {
    const db = await getDb();
    const artists = await db.collection('videos').distinct('artist');
    
    artists.forEach(artist => {
      if (artist) {
        const slug = artistToSlug(artist);
        routes.push({
          url: `${baseUrl}/artist/${slug}`,
          lastModified: currentDate,
          changeFrequency: 'weekly',
          priority: 0.8,
        });
      }
    });
  } catch (error) {
    console.error('Error fetching artists for sitemap:', error);
  }

  return routes;
}
