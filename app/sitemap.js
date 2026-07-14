import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';
import { GENRES, ERAS } from '@/lib/genreData';
import { GUIDES } from '@/lib/guidesData';
import { DIFFICULTY_LEVELS } from '@/lib/difficultyData';
import { PLAYLISTS } from '@/lib/playlistData';

const baseUrl = 'https://dadrocktabs.com';

const locales = [
  'en',
  'es',
  'pt',
  'pt-br',
  'de',
  'fr',
  'it',
  'ja',
  'ko',
  'zh',
  'ru',
  'hi',
  'sv',
  'fi',
];

function getLocalizedUrl(path, locale) {
  const cleanPath = path === '/' ? '' : path;

  if (locale === 'en') {
    return `${baseUrl}${cleanPath}`;
  }

  return `${baseUrl}/${locale}${cleanPath}`;
}

function getLanguageAlternates(path) {
  const languages = {};

  for (const locale of locales) {
    languages[locale] = getLocalizedUrl(path, locale);
  }

  languages['x-default'] = getLocalizedUrl(path, 'en');

  return languages;
}

function addLocalizedRoutes(routes, path, options = {}) {
  for (const locale of locales) {
    const route = {
      url: getLocalizedUrl(path, locale),
      alternates: {
        languages: getLanguageAlternates(path),
      },
    };

    if (options.lastModified) {
      route.lastModified = options.lastModified;
    }

    routes.push(route);
  }
}
function addEnglishRoute(routes, path, options = {}) {
  const route = {
    url: `${baseUrl}${path === '/' ? '' : path}`,
  };

  if (options.lastModified) {
    route.lastModified = options.lastModified;
  }

  routes.push(route);
}

const localizedStaticPaths = [
  '/',
  '/coming-soon',
  '/top-lessons',
  '/quickies',
  '/tools',
  '/whats-new',
  '/partners',
  '/learn',
];

export default async function sitemap() {
  const routes = [];

  // Main pages available in all 14 languages
  for (const path of localizedStaticPaths) {
    addLocalizedRoutes(routes, path);
  }

  // Individual learning guides
  for (const slug of Object.keys(GUIDES)) {
    addLocalizedRoutes(routes, `/learn/${slug}`);
  }

  // Difficulty pages
  for (const level of Object.keys(DIFFICULTY_LEVELS)) {
    addLocalizedRoutes(routes, `/difficulty/${level}`);
  }

  // Genre pages are currently English-only
  for (const slug of Object.keys(GENRES)) {
    addEnglishRoute(routes, `/genre/${slug}`);
  }

  // Era pages are currently English-only
  for (const slug of Object.keys(ERAS)) {
    addEnglishRoute(routes, `/era/${slug}`);
  }

  // Playlist pages are currently English-only
  for (const slug of Object.keys(PLAYLISTS)) {
    addEnglishRoute(routes, `/playlist/${slug}`);
  }

  const highPrioritySongs = new Set([
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
    'acdc-back-in-black',
    'metallica-fade-to-black',
    'slayer-raining-blood',
  ]);

  const artistSlugOverrides = {
    'ac-dc': 'acdc',
  };

  try {
    const db = await getDb();

    const artists = await db
      .collection('videos')
      .distinct('artist');

    const junkPatterns = [
      '#',
      'Coming Soon',
      'coming soon',
      'Memorial Video',
      'Original Song',
      'Greatest Drummers',
      'Lead Singers',
      'Welcome To The Jungle 2022',
      'Highway To Hell',
      'Hold On Loosely',
      'Cities On Flame',
      'Face The Slayer',
      'The Great 80',
      'The DadRock',
      'DadRock Tabs',
      'Steppenwolf Be The First',
      'Children Of The Grave',
      "80's Fretmasters",
    ];

    const seenArtistSlugs = new Set();

    for (const artist of artists) {
      if (!artist) continue;

      const isJunk = junkPatterns.some((pattern) =>
        artist.includes(pattern)
      );

      if (isJunk) continue;
            let slug = artistToSlug(artist);

      if (!slug) continue;

      slug = artistSlugOverrides[slug] || slug;

      if (seenArtistSlugs.has(slug)) continue;

      seenArtistSlugs.add(slug);

      addLocalizedRoutes(routes, `/artist/${slug}`);
    }

    const songPages = await db
      .collection('song_pages')
      .find(
        {},
        {
          projection: {
            slug: 1,
            updated_at: 1,
          },
        }
      )
      .toArray();

    for (const song of songPages) {
      if (!song.slug) continue;

      const options = {};

      if (song.updated_at) {
        options.lastModified = song.updated_at;
      }

      addLocalizedRoutes(
        routes,
        `/songs/${song.slug}`,
        options
      );
    }
  } catch (error) {
    console.error(
      'Error generating database sitemap routes:',
      error
    );
  }

  return routes;
}
