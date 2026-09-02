import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';
import { locales } from '@/lib/i18n';
import { GENRES, ERAS } from '@/lib/genreData';
import { GUIDES } from '@/lib/guidesData';
import { DIFFICULTY_LEVELS } from '@/lib/difficultyData';
import { PLAYLISTS } from '@/lib/playlistData';

const baseUrl = 'https://dadrocktabs.com';

function getLocalizedUrl(path, locale) {
  const cleanPath = path === '/' ? '' : path;

  if (locale === 'en') {
    return `${baseUrl}${cleanPath}`;
  }

  return `${baseUrl}/${locale}${cleanPath}`;
}

function getHomepageLanguageAlternates() {
  const languages = {};

  for (const locale of locales) {
    languages[locale] = getLocalizedUrl('/', locale);
  }

  languages['x-default'] = getLocalizedUrl('/', 'en');
  return languages;
}

function addLocalizedHomepages(routes) {
  const languages = getHomepageLanguageAlternates();

  for (const locale of locales) {
    routes.push({
      url: getLocalizedUrl('/', locale),
      alternates: { languages },
    });
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

const englishStaticPaths = [
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

  // Only the language homepages are independent multilingual search URLs.
  // Their self-canonicals + hreflang metadata are handled by app/[lang]/page.js.
  addLocalizedHomepages(routes);

  // All subpage families use the English URL as the search canonical.
  // Locale-prefixed variants remain available to visitors but stay out of the sitemap.
  for (const path of englishStaticPaths) {
    addEnglishRoute(routes, path);
  }

  // Backing Track Studio is English-only.
  addEnglishRoute(routes, '/bts');

  // Individual learning guides: English canonical URLs only.
  for (const slug of Object.keys(GUIDES)) {
    addEnglishRoute(routes, `/learn/${slug}`);
  }

  // Difficulty pages: English canonical URLs only.
  for (const level of Object.keys(DIFFICULTY_LEVELS)) {
    addEnglishRoute(routes, `/difficulty/${level}`);
  }

  // Genre pages are English-only.
  for (const slug of Object.keys(GENRES)) {
    addEnglishRoute(routes, `/genre/${slug}`);
  }

  // Era pages are English-only.
  for (const slug of Object.keys(ERAS)) {
    addEnglishRoute(routes, `/era/${slug}`);
  }

  // Playlist pages are English-only.
  for (const slug of Object.keys(PLAYLISTS)) {
    addEnglishRoute(routes, `/playlist/${slug}`);
  }

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
      addEnglishRoute(routes, `/artist/${slug}`);
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

      addEnglishRoute(
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
