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

// Helper: generate hreflang alternates for a given path
function generateLanguageAlternates(path = '') {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  const languages = {};
  for (const lang of locales) {
    if (lang === 'en') {
      languages[lang] = `${baseUrl}${cleanPath}`;
    } else {
      languages[lang] = `${baseUrl}/${lang}${cleanPath}`;
    }
  }
  languages['x-default'] = `${baseUrl}${cleanPath}`;
  return { languages };
}

export default async function sitemap() {
  const routes = [];
  const currentDate = new Date().toISOString();
  
  // Add language routes (homepage in all languages)
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

  // Add Coming Soon page (with hreflang alternates)
  routes.push({
    url: `${baseUrl}/coming-soon`,
    lastModified: currentDate,
    changeFrequency: 'daily',
    priority: 0.9,
    alternates: generateLanguageAlternates('/coming-soon'),
  });

  // Add Top Lessons page (with hreflang alternates)
  routes.push({
    url: `${baseUrl}/top-lessons`,
    lastModified: currentDate,
    changeFrequency: 'weekly',
    priority: 0.9,
    alternates: generateLanguageAlternates('/top-lessons'),
  });

  // Add Quickies page (with hreflang alternates)
  routes.push({
    url: `${baseUrl}/quickies`,
    lastModified: currentDate,
    changeFrequency: 'weekly',
    priority: 0.9,
    alternates: generateLanguageAlternates('/quickies'),
  });

  // Add artist pages (with hreflang alternates)
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
          alternates: generateLanguageAlternates(`/artist/${slug}`),
        });
      }
    });
  } catch (error) {
    console.error('Error fetching artists for sitemap:', error);
  }

  // Add song pages (with hreflang alternates)
  try {
    const db = await getDb();
    const songPages = await db.collection('song_pages').find({}, { projection: { slug: 1, updated_at: 1 } }).toArray();
    
    songPages.forEach(song => {
      if (song.slug) {
        routes.push({
          url: `${baseUrl}/songs/${song.slug}`,
          lastModified: song.updated_at || currentDate,
          changeFrequency: 'monthly',
          priority: 0.7,
          alternates: generateLanguageAlternates(`/songs/${song.slug}`),
        });
      }
    });
  } catch (error) {
    console.error('Error fetching song pages for sitemap:', error);
  }

  return routes;
}
