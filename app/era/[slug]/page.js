import { ERAS } from '@/lib/genreData';
import { notFound } from 'next/navigation';
import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';
import GenrePageClient from '@/app/genre/[slug]/GenrePageClient';

export async function generateMetadata({ params }) {
  const { slug } = await params;
  const era = ERAS[slug];
  if (!era) return {};
  
  const title = `${era.name} Guitar Tabs - Free Lessons for ${era.artists.slice(0, 3).join(', ')} & More | DadRock Tabs`;
  const description = `${era.longDescription.substring(0, 150)}... Learn ${era.artists.length}+ ${era.name.toLowerCase()} bands with free guitar and bass tab video lessons.`;
  
  return {
    title,
    description,
    keywords: `${era.name.toLowerCase()} guitar tabs, ${era.name.toLowerCase()} bass tabs, ${era.artists.map(a => `${a} tabs`).join(', ')}, learn ${era.name.toLowerCase()} guitar`,
    openGraph: {
      title: `${era.name} Guitar & Bass Tabs - Free Video Lessons`,
      description,
      type: 'website',
      url: `https://dadrocktabs.com/era/${slug}`,
      siteName: 'DadRock Tabs',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
    },
  };
}

export function generateStaticParams() {
  return Object.keys(ERAS).map(slug => ({ slug }));
}

export default async function EraPage({ params }) {
  const { slug } = await params;
  const era = ERAS[slug];
  
  if (!era) {
    notFound();
  }
  
  const db = await getDb();
  const artistData = [];
  
  for (const artistName of era.artists) {
    const artistSlug = artistToSlug(artistName);
    const escapedName = artistName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    
    const count = await db.collection('videos').countDocuments({
      artist: { $regex: new RegExp(`^${escapedName}`, 'i') }
    });
    
    const video = await db.collection('videos').findOne(
      { artist: { $regex: new RegExp(`^${escapedName}`, 'i') } },
      { projection: { thumbnail: 1 } }
    );
    
    if (count > 0) {
      artistData.push({
        name: artistName,
        slug: artistSlug,
        lessonCount: count,
        thumbnail: video?.thumbnail || null,
      });
    }
  }
  
  artistData.sort((a, b) => b.lessonCount - a.lessonCount);
  
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    'name': `${era.name} Guitar Tabs`,
    'description': era.longDescription,
    'url': `https://dadrocktabs.com/era/${slug}`,
    'isPartOf': { '@id': 'https://dadrocktabs.com/#website' },
    'mainEntity': {
      '@type': 'ItemList',
      'numberOfItems': artistData.length,
      'itemListElement': artistData.map((artist, i) => ({
        '@type': 'ListItem',
        'position': i + 1,
        'item': {
          '@type': 'MusicGroup',
          'name': artist.name,
          'url': `https://dadrocktabs.com/artist/${artist.slug}`,
        }
      }))
    }
  };
  
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <GenrePageClient genre={era} slug={slug} artists={artistData} type="era" />
    </>
  );
}
