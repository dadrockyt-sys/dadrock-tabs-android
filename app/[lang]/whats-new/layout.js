import { generateAlternates, generateCanonical } from '@/lib/seo';

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams?.lang || 'en';
  const pageUrl = generateCanonical('/whats-new', lang);

  return {
    title: "What's New - Latest Guitar & Bass Lessons | DadRock Tabs",
    description: 'See the latest guitar and bass tab lessons, tutorials, and newly added songs on DadRock Tabs.',
    alternates: generateAlternates('/whats-new', lang),
    openGraph: {
      title: "What's New | DadRock Tabs",
      description: 'Fresh guitar and bass tab lessons and tutorials from DadRock Tabs.',
      type: 'website',
      url: pageUrl,
      siteName: 'DadRock Tabs',
    },
  };
}

export default function LocalizedWhatsNewLayout({ children }) {
  return children;
}
