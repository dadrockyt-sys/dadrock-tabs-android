import { generateAlternates, generateCanonical } from '@/lib/seo';

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams?.lang || 'en';
  const pageUrl = generateCanonical('/partners', lang);

  return {
    title: 'Partners & Sponsorships | DadRock Tabs',
    description: 'Partner with DadRock Tabs for guitar and bass lesson sponsorships, product reviews, affiliate campaigns, website placements, and creator collaborations.',
    alternates: generateAlternates('/partners', lang),
    openGraph: {
      title: 'Partners & Sponsorships | DadRock Tabs',
      description: 'Partnership and sponsorship opportunities with DadRock Tabs.',
      type: 'website',
      url: pageUrl,
      siteName: 'DadRock Tabs',
    },
  };
}

export default function LocalizedPartnersLayout({ children }) {
  return children;
}
