// Shared slug utility — used across the entire app for consistent URL generation
// This MUST be the single source of truth for artist-to-slug conversion

const SPECIAL_SLUGS = {
  'AC/DC': 'acdc',
  "Guns N' Roses": 'guns-n-roses',
  'Guns N Roses': 'guns-n-roses',
  'Mötley Crüe': 'motley-crue',
  'Motley Crue': 'motley-crue',
  'Motörhead': 'motorhead',
  'Motorhead': 'motorhead',
  'Blue Öyster Cult': 'blue-oyster-cult',
  'Blue Oyster Cult': 'blue-oyster-cult',
  "Jane's Addiction": 'janes-addiction',
  "Enuff Z'Nuff": 'enuff-znuff',
  "Drivin' 'N' Cryin'": 'drivin-n-cryin',
  'ZZ Top': 'zz-top',
  'UFO': 'ufo',
  'REO Speedwagon': 'reo-speedwagon',
  'ELO': 'elo',
  'BTO': 'bto',
  'LA Guns': 'la-guns',
  'L.A. Guns': 'la-guns',
  'W.A.S.P.': 'wasp',
  'WASP': 'wasp',
  'Y&T': 'y-and-t',
  'Mr. Big': 'mr-big',
  'Mr Big': 'mr-big',
};

// Reverse mapping: slug → artist name (for page lookups)
const SLUG_TO_ARTIST = {
  'acdc': 'AC/DC',
  'guns-n-roses': 'Guns N Roses',
  'motley-crue': 'Motley Crue',
  'motorhead': 'Motorhead',
  'blue-oyster-cult': 'Blue Oyster Cult',
  'janes-addiction': "Jane's Addiction",
  'enuff-znuff': "Enuff Z'Nuff",
  'drivin-n-cryin': "Drivin' 'N' Cryin'",
  'zz-top': 'ZZ Top',
  'ufo': 'UFO',
  'reo-speedwagon': 'REO Speedwagon',
  'elo': 'ELO',
  'bto': 'BTO',
  'la-guns': 'LA Guns',
  'wasp': 'W.A.S.P.',
  'y-and-t': 'Y&T',
  'mr-big': 'Mr. Big',
};

/**
 * Convert artist name to URL slug
 * This is the CANONICAL slug generation — use everywhere
 */
export function artistToSlug(artist) {
  if (!artist) return '';
  
  // Clean trailing " -" that sometimes appears in DB
  const cleanArtist = artist.replace(/ -$/, '').trim();
  
  // Check special cases first
  if (SPECIAL_SLUGS[cleanArtist]) {
    return SPECIAL_SLUGS[cleanArtist];
  }
  
  // Default: lowercase, replace non-alphanumeric with hyphens, collapse, trim
  return cleanArtist
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

/**
 * Convert slug back to artist name pattern for DB lookup
 * Returns the best-guess artist name from a slug
 */
export function slugToArtistPattern(slug) {
  // Check reverse mapping first
  if (SLUG_TO_ARTIST[slug]) {
    return SLUG_TO_ARTIST[slug];
  }
  
  // Default: split on hyphens, title case each word
  return slug
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export { SPECIAL_SLUGS, SLUG_TO_ARTIST };
