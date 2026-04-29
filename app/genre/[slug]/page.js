import { GENRES } from '@/lib/genreData';
import { notFound } from 'next/navigation';
import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';
import GenrePageClient from './GenrePageClient';

export async function generateMetadata({ params }) {
  const { slug } = await params;
  const genre = GENRES[slug];
  if (!genre) return {};
  
  const title = `${genre.name} Guitar Tabs - Free Lessons for ${genre.artists.slice(0, 3).join(', ')} & More | DadRock Tabs`;
  const description = `${genre.longDescription.substring(0, 150)}... Learn ${genre.artists.length}+ ${genre.name.toLowerCase()} bands with free guitar and bass tab video lessons.`;
  
  return {
    title,
    description,
    keywords: `${genre.name.toLowerCase()} guitar tabs, ${genre.name.toLowerCase()} bass tabs, ${genre.artists.map(a => `${a} tabs`).join(', ')}, learn ${genre.name.toLowerCase()} guitar, free rock tabs`,
    openGraph: {
      title: `${genre.name} Guitar & Bass Tabs - Free Video Lessons`,
      description,
      type: 'website',
      url: `https://dadrocktabs.com/genre/${slug}`,
      siteName: 'DadRock Tabs',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
    },
  };
}

// Generate static params for all genres
export function generateStaticParams() {
  return Object.keys(GENRES).map(slug => ({ slug }));
}

export default async function GenrePage({ params }) {
  const { slug } = await params;
  const genre = GENRES[slug];
  
  if (!genre) {
    notFound();
  }
  
  // Get video counts for each artist in this genre
  const db = await getDb();
  const artistData = [];
  
  for (const artistName of genre.artists) {
    const artistSlug = artistToSlug(artistName);
    const escapedName = artistName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    
    const count = await db.collection('videos').countDocuments({
      artist: { $regex: new RegExp(`^${escapedName}`, 'i') }
    });
    
    // Get a thumbnail
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
  
  // Sort by lesson count descending
  artistData.sort((a, b) => b.lessonCount - a.lessonCount);
  
  // JSON-LD Schema
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    'name': `${genre.name} Guitar Tabs`,
    'description': genre.longDescription,
    'url': `https://dadrocktabs.com/genre/${slug}`,
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
          'genre': genre.name,
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
      <GenrePageClient genre={genre} slug={slug} artists={artistData} type="genre" />
    </>
  );
}
