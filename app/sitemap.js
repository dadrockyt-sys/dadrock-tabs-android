import { locales } from '@/lib/i18n';
import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';
import { GENRES, ERAS } from '@/lib/genreData';

// Use non-www as canonical (matches your redirect setup)
const baseUrl = 'https://dadrocktabs.com';

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

  // Add Genre browse pages
  for (const slug of Object.keys(GENRES)) {
    routes.push({
      url: `${baseUrl}/genre/${slug}`,
      lastModified: currentDate,
      changeFrequency: 'monthly',
      priority: 0.7,
    });
  }

  // Add Era browse pages
  for (const slug of Object.keys(ERAS)) {
    routes.push({
      url: `${baseUrl}/era/${slug}`,
      lastModified: currentDate,
      changeFrequency: 'monthly',
      priority: 0.7,
    });
  }


  // Add artist pages (with hreflang alternates)
  // IMPORTANT: Deduplicate by slug and filter out junk entries
  // (hashtag content, "Coming Soon" teasers, promotional videos, etc.)
  try {
    const db = await getDb();
    const artists = await db.collection('videos').distinct('artist');
    
    // Junk patterns — these are not real artist pages
    const junkPatterns = [
      '#',                    // Hashtag content (e.g., "George Lynch  #Electric")
      'Coming Soon',          // Coming soon teasers
      'coming soon',
      'Memorial Video',       // Memorial/tribute content
      'Original Song',        // Original songs, not artist pages
      'Greatest Drummers',    // Compilation/list videos
      'Lead Singers',         // Compilation videos
      'Welcome To The Jungle 2022', // One-off videos
      'Highway To Hell',      // Song used as artist name
      'Hold On Loosely',      // Song used as artist name
      'Cities On Flame',      // Song used as artist name
      'Face The Slayer',      // Non-artist content
      'The Great 80',         // Non-artist content
      'The DadRock',          // Channel self-reference
      'DadRock Tabs',         // Channel self-reference
      'Steppenwolf Be The First', // Discussion/debate video
      'Children Of The Grave', // Song used as artist name
      '80\'s Fretmasters',    // Compilation content
    ];
    
    const seenSlugs = new Set();
    
    artists.forEach(artist => {
      if (!artist) return;
      
      // Skip junk entries
      const isJunk = junkPatterns.some(pattern => artist.includes(pattern));
      if (isJunk) return;
      
      // Skip standalone non-artist entries
      if (artist === 'Lead' || artist === 'Danger Danger' || artist === 'Kimg Diamond') {
        // Keep these — they're real artists (Danger Danger, King Diamond typo)
      }
      
      const slug = artistToSlug(artist);
      if (!slug) return;
      
      // Deduplicate — only add each slug once
      if (seenSlugs.has(slug)) return;
      seenSlugs.add(slug);
      
      routes.push({
        url: `${baseUrl}/artist/${slug}`,
        lastModified: currentDate,
        changeFrequency: 'weekly',
        priority: 0.8,
        alternates: generateLanguageAlternates(`/artist/${slug}`),
      });
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
