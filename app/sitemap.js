import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';
import { GENRES, ERAS } from '@/lib/genreData';
import { GUIDES } from '@/lib/guidesData';
import { DIFFICULTY_LEVELS } from '@/lib/difficultyData';
import { PLAYLISTS } from '@/lib/playlistData';

// Use non-www as canonical (matches your redirect setup)
const baseUrl = 'https://dadrocktabs.com';

export default async function sitemap() {
  const routes = [];
  const currentDate = new Date().toISOString();
  
  // ─── HOMEPAGE (English only — locale pages are noindexed) ───
  routes.push({
    url: baseUrl,
    lastModified: currentDate,
    changeFrequency: 'daily',
    priority: 1,
  });

  // ─── STATIC PAGES ───
  routes.push({
    url: `${baseUrl}/coming-soon`,
    lastModified: currentDate,
    changeFrequency: 'daily',
    priority: 0.9,
  });

  routes.push({
    url: `${baseUrl}/top-lessons`,
    lastModified: currentDate,
    changeFrequency: 'weekly',
    priority: 0.9,
  });

  routes.push({
    url: `${baseUrl}/quickies`,
    lastModified: currentDate,
    changeFrequency: 'weekly',
    priority: 0.9,
  });

  routes.push({
    url: `${baseUrl}/tools`,
    lastModified: currentDate,
    changeFrequency: 'monthly',
    priority: 0.8,
  });

  routes.push({
    url: `${baseUrl}/whats-new`,
    lastModified: currentDate,
    changeFrequency: 'daily',
    priority: 0.8,
  });

  routes.push({
    url: `${baseUrl}/learn`,
    lastModified: currentDate,
    changeFrequency: 'weekly',
    priority: 0.8,
  });

  // ─── GENRE PAGES ───
  for (const slug of Object.keys(GENRES)) {
    routes.push({
      url: `${baseUrl}/genre/${slug}`,
      lastModified: currentDate,
      changeFrequency: 'monthly',
      priority: 0.7,
    });
  }

  // ─── ERA PAGES ───
  for (const slug of Object.keys(ERAS)) {
    routes.push({
      url: `${baseUrl}/era/${slug}`,
      lastModified: currentDate,
      changeFrequency: 'monthly',
      priority: 0.7,
    });
  }

  // ─── LEARN/GUIDES PAGES ───
  for (const slug of Object.keys(GUIDES)) {
    routes.push({
      url: `${baseUrl}/learn/${slug}`,
      lastModified: currentDate,
      changeFrequency: 'monthly',
      priority: 0.7,
    });
  }

  // ─── DIFFICULTY PAGES ───
  for (const level of Object.keys(DIFFICULTY_LEVELS)) {
    routes.push({
      url: `${baseUrl}/difficulty/${level}`,
      lastModified: currentDate,
      changeFrequency: 'monthly',
      priority: 0.7,
    });
  }

  // ─── PLAYLIST PAGES ───
  for (const slug of Object.keys(PLAYLISTS)) {
    routes.push({
      url: `${baseUrl}/playlist/${slug}`,
      lastModified: currentDate,
      changeFrequency: 'monthly',
      priority: 0.7,
    });
  }

  // ─── ARTIST PAGES (no hreflang — locale artist pages don't exist) ───
  try {
    const db = await getDb();
    const artists = await db.collection('videos').distinct('artist');
    
    const junkPatterns = [
      '#', 'Coming Soon', 'coming soon', 'Memorial Video', 'Original Song',
      'Greatest Drummers', 'Lead Singers', 'Welcome To The Jungle 2022',
      'Highway To Hell', 'Hold On Loosely', 'Cities On Flame', 'Face The Slayer',
      'The Great 80', 'The DadRock', 'DadRock Tabs', 'Steppenwolf Be The First',
      'Children Of The Grave', '80\'s Fretmasters',
    ];
    
    const seenSlugs = new Set();
    
    artists.forEach(artist => {
      if (!artist) return;
      const isJunk = junkPatterns.some(pattern => artist.includes(pattern));
      if (isJunk) return;
      
      const slug = artistToSlug(artist);
      if (!slug) return;
      if (seenSlugs.has(slug)) return;
      seenSlugs.add(slug);
      
      routes.push({
        url: `${baseUrl}/artist/${slug}`,
        lastModified: currentDate,
        changeFrequency: 'weekly',
        priority: 0.8,
      });
    });
  } catch (error) {
    console.error('Error fetching artists for sitemap:', error);
  }

  // ─── SONG PAGES (no hreflang — locale song pages don't exist) ───
  // High-priority songs (best SEO opportunities based on popularity)
  const highPrioritySongs = [
    'metallica-master-of-puppets',
    'metallica-enter-sandman',
    'led-zeppelin-stairway-to-heaven',
    'black-sabbath-war-pigs',
    'metallica-one',
    'pantera-cemetery-gates',
    'slayer-angel-of-death',
    'megadeth-holy-wars-the-punishment-due',
    'black-sabbath-heaven-and-hell',
    'led-zeppelin-dazed-and-confused',
    'metallica-seek-and-destroy',
    'metallica-for-whom-the-bell-tolls',
    'metallica-creeping-death',
    'black-sabbath-iron-man',
    'ozzy-osbourne-crazy-train',
    'van-halen-eruption',
    'ac-dc-back-in-black',
    'metallica-fade-to-black',
    'pantera-walk',
    'slayer-raining-blood',
  ];

  try {
    const db = await getDb();
    const songPages = await db.collection('song_pages').find({}, { projection: { slug: 1, updated_at: 1 } }).toArray();
    
    songPages.forEach(song => {
      if (song.slug) {
        // Boost priority for high-value songs that can rank well
        const isHighPriority = highPrioritySongs.includes(song.slug);
        
        routes.push({
          url: `${baseUrl}/songs/${song.slug}`,
          lastModified: song.updated_at || currentDate,
          changeFrequency: isHighPriority ? 'weekly' : 'monthly',
          priority: isHighPriority ? 0.9 : 0.7,
        });
      }
    });
  } catch (error) {
    console.error('Error fetching song pages for sitemap:', error);
  }

  return routes;
}
