import {
  GUIDES,
  GUIDE_CONTENT_TRANSLATIONS
} from '@/lib/guidesData';
import generatedGuideContentTranslations from '@/lib/generatedGuideContentTranslations.json';
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
  function getArtistSlug(slug) {
  const slugMap = {
    'ac-dc': 'acdc'
  };

  return slugMap[slug] || slug;
  }
}

function getGuideContent(guide, slug, lang) {
  const translatedContent =
  generatedGuideContentTranslations?.[lang]?.[slug] ||
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
      <div className="min-h-screen bg-zinc-950 text-white">
        <LearnHeader />

        <main className="container mx-auto max-w-3xl px-4 py-8">
          <nav className="mb-6 text-sm text-zinc-400">
            <Link
              href={homePath}
              className="transition-colors hover:text-amber-500"
            >
              {labels.home}
            </Link>

            <span className="mx-2">/</span>

            <Link
              href={learnPath}
              className="transition-colors hover:text-amber-500"
            >
              {labels.learn}
            </Link>
            <span className="mx-2">/</span>

            <span className="text-white">{guideTitle}</span>
          </nav>

          <article>
            <header className="mb-8">
              <div className="mb-4 flex items-center gap-3">
                <span
                  className={`rounded-lg px-3 py-1 text-xs font-semibold ${
                    guide.category === 'Beginner'
                      ? 'bg-green-500/20 text-green-400'
                      : guide.category === 'Technique'
                        ? 'bg-amber-500/20 text-amber-400'
                        : 'bg-purple-500/20 text-purple-400'
                  }`}
                >
                  {categoryLabel}
                </span>

                <span className="text-sm text-zinc-500">
                  {guideReadTime}
                </span>
              </div>

              <h1 className="mb-4 text-3xl font-bold leading-tight sm:text-4xl lg:text-5xl">
                {guideTitle}
              </h1>
              <p className="text-xl leading-relaxed text-zinc-400">
                {guideDescription}
              </p>
            </header>

            <div
              className="prose prose-invert prose-zinc max-w-none
                prose-headings:text-white prose-headings:font-bold
                prose-h2:text-2xl prose-h2:mt-10 prose-h2:mb-4 prose-h2:text-amber-500
                prose-h3:text-xl prose-h3:mt-6 prose-h3:mb-3
                prose-p:text-zinc-300 prose-p:leading-relaxed prose-p:mb-4
                prose-li:text-zinc-300
                prose-strong:text-white
                prose-pre:bg-zinc-900 prose-pre:border prose-pre:border-zinc-700 prose-pre:rounded-xl
                prose-a:text-amber-500 prose-a:no-underline hover:prose-a:underline"
              dangerouslySetInnerHTML={{
                __html: guideContent
              }}
            />
            {guide.relatedArtists?.length > 0 && (
              <section className="mt-12 rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6">
                <h2 className="mb-4 text-xl font-bold text-amber-500">
                  {labels.relatedArtists}
                </h2>

                <div className="flex flex-wrap gap-3">
                  {guide.relatedArtists.map((artistSlug) => (
                    <Link
                      key={artistSlug}
                      href={getLocalizedPath(`/artist/${artistSlug}`, lang)}
                      className="rounded-full border border-zinc-700 bg-zinc-800 px-4 py-2 text-sm font-medium transition-all hover:border-amber-500 hover:bg-amber-500 hover:text-black"
                    >
                      {artistSlug
                        .replace(/-/g, ' ')
                        .replace(/\b\w/g, c => c.toUpperCase())}
                    </Link>
                  ))}
                </div>
              </section>
            )}

          </article>

          <section className="mt-12">
            <h2 className="mb-4 text-xl font-bold">
              {labels.moreGuides}
            </h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                            {Object.values(GUIDES)
                .filter((item) => item.slug !== guide.slug)
                .slice(0, 4)
                .map((item) => (
                  <Link
                    key={item.slug}
                    href={getLocalizedPath(`/learn/${item.slug}`, lang)}
                    className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 transition-all hover:border-amber-500 hover:bg-zinc-900"
                  >
                    <h3 className="mb-2 font-bold text-white">
                      {getLocalizedValue(item.title, lang)}
                    </h3>

                    <p className="text-sm text-zinc-400">
                      {getLocalizedValue(item.description, lang)}
                    </p>
                  </Link>
                ))}
            </div>
          </section>
        </main>

        <footer className="border-t border-zinc-800 py-8">
          <div className="container mx-auto max-w-3xl px-4 text-center text-sm text-zinc-500">
            <p>{labels.freeLessons}</p>

            <Link
              href={learnPath}
              className="mt-4 inline-block text-amber-500 transition-colors hover:text-amber-400"
            >
              ← {labels.allGuides}
            </Link>
          </div>
        </footer>
      </div>
    </>
  );
}






