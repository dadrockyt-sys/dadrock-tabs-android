import {
  GUIDES,
  GUIDE_CONTENT_TRANSLATIONS
} from '@/lib/guidesData';
import { getSubPageTranslation } from '@/lib/subPageI18n';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import LearnHeader from '@/components/LearnHeader';

function getLocalizedValue(value, lang) {
  if (value && typeof value === 'object') {
    return value[lang] || value.en || '';
  }

  return value || '';
}

function getLocalizedPath(path, lang) {
  return lang === 'en' ? path : `/${lang}${path}`;
}

function getGuideContent(guide, slug, lang) {
  const translatedContent =
    GUIDE_CONTENT_TRANSLATIONS?.[lang]?.[slug];

  if (translatedContent) {
    return translatedContent;
  }

  return getLocalizedValue(guide.content, lang);
}

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const slug = resolvedParams?.slug;
  const lang = resolvedParams?.lang || 'en';
  const guide = GUIDES[slug];

  if (!guide) {
    return {
      title: 'Guide Not Found | DadRock Tabs'
    };
  }

  const guideTitle = getLocalizedValue(guide.title, lang);
  const guideDescription = getLocalizedValue(
    guide.description,
    lang
  );

  const localizedPath = getLocalizedPath(
    `/learn/${slug}`,
    lang
  );

  const pageUrl = `https://dadrocktabs.com${localizedPath}`;

  return {
    title: `${guideTitle} | DadRock Tabs`,
    description: guideDescription,
    keywords: guide.keywords,
    alternates: {
      canonical: pageUrl
    },
    openGraph: {
      title: guideTitle,
      description: guideDescription,
      type: 'article',
      url: pageUrl,
      siteName: 'DadRock Tabs',
      images: [
        {
          url: `https://dadrocktabs.com/api/og?title=${encodeURIComponent(
            guideTitle
          )}&type=genre`,
          width: 1200,
          height: 630
        }
      ]
    },
    twitter: {
      card: 'summary_large_image',
      title: guideTitle,
      description: guideDescription
    }
  };
}
export function generateStaticParams() {
  return Object.keys(GUIDES).map((slug) => ({ slug }));
}

export default async function GuidePage({ params }) {
  const resolvedParams = await params;
  const slug = resolvedParams?.slug;
  const lang = resolvedParams?.lang || 'en';
  const guide = GUIDES[slug];

  if (!guide) {
    notFound();
  }

  const t = getSubPageTranslation(lang);

  const guideTitle = getLocalizedValue(guide.title, lang);
  const guideDescription = getLocalizedValue(
    guide.description,
    lang
  );
  const guideContent = getGuideContent(guide, slug, lang);
  const guideReadTime = getLocalizedValue(
    guide.readTime,
    lang
  );

  const homePath = getLocalizedPath('/', lang);
  const learnPath = getLocalizedPath('/learn', lang);
  const guidePath = getLocalizedPath(
    `/learn/${slug}`,
    lang
  );

  const labels = {
    home: t.home || 'Home',
    learn: t.learn || 'Learn',
    allGuides: t.allGuides || 'All Guides',
    moreGuides: t.moreGuides || 'More Guides',
    relatedArtists:
      t.relatedArtists || 'Related Artists on DadRock Tabs',
    freeLessons:
      t.freeLessons || 'Free guitar & bass lessons.'
  };

  const categoryLabel =
    guide.category === 'Beginner'
      ? t.beginner || 'Beginner'
      : guide.category === 'Technique'
        ? t.technique || 'Technique'
        : guide.category === 'Intermediate'
          ? t.intermediate || 'Intermediate'
          : guide.category === 'Advanced'
            ? t.advanced || 'Advanced'
            : t.theory || guide.category;

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: guideTitle,
    description: guideDescription,
    url: `https://dadrocktabs.com${guidePath}`,
    author: {
      '@type': 'Organization',
      name: 'DadRock Tabs',
      url: 'https://dadrocktabs.com'
    },
    publisher: {
      '@type': 'Organization',
      name: 'DadRock Tabs',
      url: 'https://dadrocktabs.com',
      logo: {
        '@type': 'ImageObject',
        url: 'https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png'
      }
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': `https://dadrocktabs.com${guidePath}`
    },
    articleSection: categoryLabel,
    keywords: guide.keywords
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd)
        }}
      />



