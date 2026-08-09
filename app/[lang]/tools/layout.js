import { generateAlternates, generateCanonical } from '@/lib/seo';

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams?.lang || 'en';
  const pageUrl = generateCanonical('/tools', lang);

  return {
    title: 'Free Guitar Practice Tools | DadRock Tabs',
    description: 'Use free guitar practice tools from DadRock Tabs, including timing and practice utilities built for guitar and bass players.',
    alternates: generateAlternates('/tools', lang),
    openGraph: {
      title: 'Free Guitar Practice Tools | DadRock Tabs',
      description: 'Free practice utilities for guitar and bass players.',
      type: 'website',
      url: pageUrl,
      siteName: 'DadRock Tabs',
    },
  };
}

export default function LocalizedToolsLayout({ children }) {
  return children;
}
