// Difficulty classification for songs
// Maps patterns/artists to difficulty levels based on playing complexity

export const DIFFICULTY_LEVELS = {
  beginner: {
    name: 'Beginner',
    slug: 'beginner',
    description: 'Easy songs perfect for new guitar players. Simple riffs, basic chords, and slow tempos.',
    longDescription: 'These songs are ideal for guitarists in their first 6 months of playing. They feature simple power chord progressions, slow-to-moderate tempos, basic strumming patterns, and straightforward single-note riffs. Most can be learned in a single practice session.',
    icon: '🌱',
    color: 'from-green-500 to-emerald-600',
    criteria: 'Slow tempo, simple chords, repetitive patterns, minimal technique required.',
  },
  intermediate: {
    name: 'Intermediate',
    slug: 'intermediate',
    description: 'Songs that challenge your technique with faster riffs, barre chords, and moderate solos.',
    longDescription: 'Intermediate songs require comfort with barre chords, palm muting at moderate speeds, basic lead techniques (bending, hammer-ons, pull-offs), and the ability to switch between clean and distorted sections. Expect faster tempos and more complex song structures.',
    icon: '🔥',
    color: 'from-amber-500 to-orange-600',
    criteria: 'Moderate tempo, barre chords, palm muting, basic solos, varied sections.',
  },
  advanced: {
    name: 'Advanced',
    slug: 'advanced',
    description: 'Complex songs featuring fast shredding, intricate solos, and demanding techniques.',
    longDescription: 'Advanced songs demand mastery of speed picking (both alternate and downpicking at high BPM), sweep picking, tapping, complex time signatures, extended solos, and multi-part arrangements. These are the songs that separate serious guitarists from casual players.',
    icon: '⚡',
    color: 'from-red-500 to-rose-600',
    criteria: 'Fast tempo, complex solos, advanced techniques, demanding endurance.',
  },
};

// Artist-to-difficulty mapping (primary difficulty of most of their songs)
// This provides a baseline — individual songs may vary
export const ARTIST_DIFFICULTY = {
  // Beginner-friendly artists
  'ac-dc': 'beginner',
  'deep-purple': 'beginner',
  'black-sabbath': 'beginner',
  'kiss': 'beginner',
  'zz-top': 'beginner',
  'poison': 'beginner',
  'twisted-sister': 'beginner',
  'quiet-riot': 'beginner',
  'firehouse': 'beginner',
  'lynyrd-skynyrd': 'beginner',
  'bad-company': 'beginner',
  'foreigner': 'beginner',
  'styx': 'beginner',
  'def-leppard': 'beginner',
  'bon-jovi': 'beginner',
  'warrant': 'beginner',
  'slaughter': 'beginner',
  'great-white': 'beginner',
  'la-guns': 'beginner',
  '38-special': 'beginner',
  'blackfoot': 'beginner',
  
  // Intermediate artists
  'metallica': 'intermediate',
  'van-halen': 'intermediate',
  'led-zeppelin': 'intermediate',
  'iron-maiden': 'intermediate',
  'judas-priest': 'intermediate',
  'megadeth': 'intermediate',
  'pantera': 'intermediate',
  'motley-crue': 'intermediate',
  'scorpions': 'intermediate',
  'ratt': 'intermediate',
  'dokken': 'intermediate',
  'whitesnake': 'intermediate',
  'thin-lizzy': 'intermediate',
  'aerosmith': 'intermediate',
  'guns-n-roses': 'intermediate',
  'soundgarden': 'intermediate',
  'alice-in-chains': 'intermediate',
  'stone-temple-pilots': 'intermediate',
  'foo-fighters': 'intermediate',
  'audioslave': 'intermediate',
  'rage-against-the-machine': 'intermediate',
  'tool': 'intermediate',
  'skid-row': 'intermediate',
  'winger': 'intermediate',
  'cinderella': 'intermediate',
  'white-lion': 'intermediate',
  'tesla': 'intermediate',
  'dio': 'intermediate',
  'ozzy-osbourne': 'intermediate',
  'rainbow': 'intermediate',
  'motorhead': 'intermediate',
  'testament': 'intermediate',
  'exodus': 'intermediate',
  'overkill': 'intermediate',
  'anthrax': 'intermediate',
  'bush': 'intermediate',
  'boston': 'intermediate',
  'journey': 'intermediate',
  'allman-brothers': 'intermediate',
  'molly-hatchet': 'intermediate',
  'eric-clapton': 'intermediate',
  'gary-moore': 'intermediate',
  'cream': 'intermediate',
  'santana': 'intermediate',
  'jimi-hendrix': 'intermediate',
  
  // Advanced artists
  'slayer': 'advanced',
  'joe-satriani': 'advanced',
  'steve-vai': 'advanced',
  'yngwie-malmsteen': 'advanced',
  'eric-johnson': 'advanced',
  'racer-x': 'advanced',
  'mr-big': 'advanced',
  'extreme': 'advanced',
  'stevie-ray-vaughan': 'advanced',
  'joe-bonamassa': 'advanced',
  'accept': 'advanced',
};

// Get difficulty for an artist slug
export function getArtistDifficulty(artistSlug) {
  return ARTIST_DIFFICULTY[artistSlug] || 'intermediate'; // default to intermediate
}

// Get all artists for a difficulty level
export function getArtistsByDifficulty(level) {
  return Object.entries(ARTIST_DIFFICULTY)
    .filter(([, diff]) => diff === level)
    .map(([slug]) => slug);
}
