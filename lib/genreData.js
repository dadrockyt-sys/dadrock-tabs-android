// Genre and Era data for browse pages
// Maps genre/era slugs to artist lists and metadata

export const GENRES = {
  'thrash-metal': {
    name: 'Thrash Metal',
    description: 'Fast, aggressive guitar riffs and shredding solos. Learn the foundational riffs of thrash metal.',
    longDescription: 'Thrash metal emerged in the early 1980s combining the speed of hardcore punk with the heaviness of heavy metal. Known for its fast tempos, aggressive picking patterns, complex guitar solos, and low-register riffs. Master the art of downpicking, palm muting, and speed picking with these legendary thrash bands.',
    artists: ['Metallica', 'Megadeth', 'Slayer', 'Anthrax', 'Pantera', 'Testament', 'Exodus', 'Overkill'],
    icon: '⚡',
    color: 'from-red-600 to-orange-600',
  },
  'hair-metal': {
    name: 'Hair Metal / Glam',
    description: 'Catchy hooks, flashy solos, and arena-ready riffs from the Sunset Strip era.',
    longDescription: 'Hair metal (also called glam metal) defined the 1980s rock scene with its blend of hard rock riffs, pop hooks, and flashy guitar solos. These bands brought guitar theatrics to the mainstream with memorable melodies and crowd-pleasing choruses. Learn iconic riffs that filled arenas across the world.',
    artists: ['Motley Crue', 'Poison', 'Ratt', 'Def Leppard', 'Cinderella', 'Warrant', 'Winger', 'Dokken', 'Skid Row', 'White Lion', 'Firehouse', 'Slaughter', 'Great White', 'LA Guns', 'Twisted Sister', 'Quiet Riot'],
    icon: '🎸',
    color: 'from-pink-600 to-purple-600',
  },
  'classic-hard-rock': {
    name: 'Classic Hard Rock',
    description: 'The foundations of rock guitar. Powerful riffs that shaped generations of guitarists.',
    longDescription: 'Classic hard rock represents the golden era of guitar-driven music. These bands defined the genre with powerful chord progressions, blues-influenced solos, and unforgettable riffs. Perfect for developing a solid rock guitar foundation and learning techniques that every guitarist should know.',
    artists: ['AC/DC', 'Van Halen', 'Led Zeppelin', 'Deep Purple', 'Aerosmith', 'Kiss', 'ZZ Top', 'Bad Company', 'Thin Lizzy', 'Scorpions', 'Foreigner', 'Boston', 'Styx', 'Journey', 'Whitesnake'],
    icon: '🔥',
    color: 'from-amber-600 to-red-600',
  },
  'heavy-metal': {
    name: 'Heavy Metal',
    description: 'Dark, powerful riffs and technical solos from the masters of metal.',
    longDescription: 'Heavy metal originated in the late 1960s and 1970s with bands pushing rock to heavier extremes. Characterized by distorted guitars, emphatic rhythms, dense bass-and-drum sound, and extended guitar solos. These are the bands that built the metal genre from the ground up.',
    artists: ['Black Sabbath', 'Iron Maiden', 'Judas Priest', 'Dio', 'Ozzy Osbourne', 'Accept', 'Rainbow', 'Motorhead'],
    icon: '🤘',
    color: 'from-zinc-600 to-zinc-800',
  },
  'grunge-alternative': {
    name: 'Grunge & Alternative',
    description: 'Raw, emotional riffs that changed music in the 1990s.',
    longDescription: 'Grunge emerged from Seattle in the late 1980s, combining punk\'s raw energy with metal\'s heaviness and emotional vulnerability. Alternative rock bands expanded on this formula with diverse guitar techniques. Learn the down-tuned riffs, haunting chord progressions, and powerful dynamics that defined a generation.',
    artists: ['Soundgarden', 'Alice In Chains', 'Stone Temple Pilots', 'Foo Fighters', 'Audioslave', 'Rage Against The Machine', 'Tool', 'Bush'],
    icon: '🌧️',
    color: 'from-teal-700 to-emerald-800',
  },
  'blues-rock': {
    name: 'Blues Rock',
    description: 'Soul-stirring guitar work rooted in the blues tradition.',
    longDescription: 'Blues rock combines the emotional expression of the blues with rock\'s energy and volume. These guitarists are masters of tone, feel, and phrasing. Learn bending, vibrato, and the pentatonic scale patterns that form the backbone of rock guitar through these legendary players.',
    artists: ['Eric Clapton', 'Stevie Ray Vaughan', 'Joe Bonamassa', 'Gary Moore', 'Cream', 'Jimi Hendrix', 'Santana', 'ZZ Top'],
    icon: '🎵',
    color: 'from-blue-700 to-indigo-800',
  },
  'guitar-shred': {
    name: 'Guitar Shred / Virtuoso',
    description: 'Mind-blowing speed and technique from the world\'s greatest guitarists.',
    longDescription: 'Shred guitar represents the pinnacle of electric guitar technique. These virtuoso players push the instrument to its limits with sweep picking, tapping, legato runs, and blistering speed. Perfect for advanced players looking to develop their technical abilities and musical vocabulary.',
    artists: ['Joe Satriani', 'Steve Vai', 'Yngwie Malmsteen', 'Eric Johnson', 'Racer X', 'Mr. Big', 'Extreme'],
    icon: '⚡',
    color: 'from-violet-600 to-fuchsia-600',
  },
  'southern-rock': {
    name: 'Southern Rock',
    description: 'Swampy grooves and dual-guitar harmonies from the American South.',
    longDescription: 'Southern rock blends rock with country, blues, and boogie influences, creating a distinctively American sound. Known for extended guitar jams, dual-guitar harmonies, and groove-driven riffs. Learn the laid-back feel and powerful rhythm playing that defines this genre.',
    artists: ['Lynyrd Skynyrd', 'Allman Brothers', 'Molly Hatchet', 'Bad Company', '38 Special', 'Blackfoot'],
    icon: '🦅',
    color: 'from-orange-700 to-amber-800',
  },
};

export const ERAS = {
  '70s-rock': {
    name: '70s Rock',
    description: 'The decade that invented hard rock and heavy metal guitar.',
    longDescription: 'The 1970s was the golden age of rock guitar innovation. From the blues-soaked riffs of Led Zeppelin to the proto-metal of Black Sabbath, this decade laid the foundation for everything that followed. Learn the riffs that started it all — many consider these the greatest guitar songs ever written.',
    artists: ['Led Zeppelin', 'Black Sabbath', 'Deep Purple', 'AC/DC', 'Aerosmith', 'Kiss', 'Thin Lizzy', 'ZZ Top', 'Rainbow', 'Rush', 'Boston', 'Lynyrd Skynyrd', 'Bad Company', 'Cream', 'The Who', 'Jimi Hendrix'],
    icon: '🕺',
    color: 'from-orange-500 to-yellow-600',
  },
  '80s-rock': {
    name: '80s Rock',
    description: 'The decade of guitar heroes, shred solos, and arena rock anthems.',
    longDescription: 'The 1980s was the decade of the guitar hero. From Eddie Van Halen\'s tapping revolution to the rise of thrash metal, the 80s produced some of the most iconic guitar riffs and solos in history. Hair metal ruled MTV, arena rock filled stadiums, and guitar technique reached new heights.',
    artists: ['Van Halen', 'Metallica', 'Def Leppard', 'Guns N Roses', 'Motley Crue', 'Iron Maiden', 'Judas Priest', 'Scorpions', 'Bon Jovi', 'Whitesnake', 'Dokken', 'Ratt', 'Poison', 'Megadeth', 'Slayer', 'Ozzy Osbourne', 'Joe Satriani', 'Dio', 'Cinderella', 'Skid Row'],
    icon: '📼',
    color: 'from-fuchsia-500 to-pink-600',
  },
  '90s-rock': {
    name: '90s Rock',
    description: 'Grunge, alternative, and the raw guitar revolution.',
    longDescription: 'The 1990s brought a seismic shift in rock guitar. Grunge stripped away the excess of the 80s in favor of raw emotion and heavy, drop-tuned riffs. Alternative rock expanded the sonic palette while maintaining guitar-driven intensity. These bands proved that feel and attitude matter as much as technique.',
    artists: ['Soundgarden', 'Alice In Chains', 'Stone Temple Pilots', 'Pantera', 'Tool', 'Rage Against The Machine', 'Foo Fighters', 'Audioslave', 'Bush', 'Extreme', 'Mr. Big'],
    icon: '📀',
    color: 'from-emerald-500 to-teal-600',
  },
};

export function getAllBrowsePages() {
  const pages = [];
  for (const [slug, data] of Object.entries(GENRES)) {
    pages.push({ type: 'genre', slug, ...data });
  }
  for (const [slug, data] of Object.entries(ERAS)) {
    pages.push({ type: 'era', slug, ...data });
  }
  return pages;
}
