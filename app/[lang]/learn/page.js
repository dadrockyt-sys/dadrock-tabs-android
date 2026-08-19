import LearnPage from '../../learn/page';
import { generateAlternates, generateCanonical } from '@/lib/seo';
import { getSubPageTranslation } from '@/lib/subPageI18n';

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams?.lang || 'en';
  const pageUrl = generateCanonical('/learn', lang);
  const t = getSubPageTranslation(lang);
  const title = `${t.learn || 'Learn'} ${t.guitar || 'Guitar'} - DadRock Tabs`;
  const description =
    t.learnSubtitle ||
    'Free guitar learning guides covering techniques, theory, and practice tips for rock and metal players.';

  return {
    title,
    description,
    alternates: generateAlternates('/learn', lang),
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

export default LearnPage;
