import { generateAlternates, generateCanonical } from '@/lib/seo';
import { getSubPageTranslation } from '@/lib/subPageI18n';

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams?.lang || 'en';
  const pageUrl = generateCanonical('/partners', lang);
  const t = getSubPageTranslation(lang);
  const title = `${t.partnershipOpportunitiesTitle || 'Partnership Opportunities'} | DadRock Tabs`;
  const description =
    t.partnershipOpportunitiesDescription ||
    t.partnerIntro ||
    'Partner with DadRock Tabs for guitar and bass lesson sponsorships, product reviews, affiliate campaigns, website placements, and creator collaborations.';

  return {
    title,
    description,
    alternates: generateAlternates('/partners', lang),
    openGraph: {
      title,
      description,
      type: 'website',
      url: pageUrl,
      siteName: 'DadRock Tabs',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
    },
  };
}

export default function LocalizedPartnersLayout({ children }) {
  return children;
}
