import { permanentRedirect } from 'next/navigation';

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const slug = resolvedParams.slug;

  return {
    alternates: {
      canonical: `https://dadrocktabs.com/en/artist/${slug}`,
    },
  };
}

export default async function ArtistRedirectPage({ params }) {
  const resolvedParams = await params;
  const slug = resolvedParams.slug;

  permanentRedirect(`/en/artist/${slug}`);
}
