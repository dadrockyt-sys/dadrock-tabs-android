from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Root metadata: match sitemap/page hreflang convention with x-default.
layout = ROOT / 'app/layout.js'
text = layout.read_text(encoding='utf-8')
old = """  languages: Object.fromEntries(\n    locales.map(lang => [lang, lang === 'en' ? baseUrl : `${baseUrl}/${lang}`])\n  ),\n"""
new = """  languages: {\n    ...Object.fromEntries(\n      locales.map(lang => [lang, lang === 'en' ? baseUrl : `${baseUrl}/${lang}`])\n    ),\n    'x-default': baseUrl,\n  },\n"""
if old not in text:
    raise SystemExit('root hreflang anchor not found')
text = text.replace(old, new, 1)
layout.write_text(text, encoding='utf-8')

# Difficulty pages: localized canonical, hreflang, OG URL, and top-level schema URL.
difficulty = ROOT / 'app/difficulty/[level]/page.js'
text = difficulty.read_text(encoding='utf-8')
headers_import = "import { headers } from 'next/headers';\n"
seo_import = "import { generateAlternates, generateCanonical } from '@/lib/seo';\n"
if seo_import not in text:
    if headers_import not in text:
        raise SystemExit('difficulty import anchor missing')
    text = text.replace(headers_import, headers_import + seo_import, 1)

start = text.index('export async function generateMetadata({ params }) {')
end = text.index('export function generateStaticParams()', start)
metadata_block = """export async function generateMetadata({ params }) {\n  const { level, lang } = await params;\n  const difficulty = DIFFICULTY_LEVELS[level];\n\n  if (!difficulty) {\n    return { title: 'Difficulty Not Found | DadRock Tabs' };\n  }\n\n  const currentLang = lang || 'en';\n  const t = difficultyT[currentLang] || difficultyT.en;\n  const localizedLevel = t.levels?.[level] || {};\n  const title = `${localizedLevel.title || `${difficulty.name} Guitar Tabs`} | DadRock Tabs`;\n  const longDescription = localizedLevel.longDescription || difficulty.longDescription || '';\n  const description = longDescription.length > 155\n    ? `${longDescription.slice(0, 155)}...`\n    : longDescription;\n  const pageUrl = generateCanonical(`/difficulty/${level}`, currentLang);\n\n  return {\n    title,\n    description,\n    keywords: `${difficulty.name.toLowerCase()} guitar tabs, easy guitar songs, ${difficulty.name.toLowerCase()} rock songs, learn guitar ${difficulty.name.toLowerCase()}, free guitar tabs`,\n    alternates: generateAlternates(`/difficulty/${level}`, currentLang),\n    openGraph: {\n      title: localizedLevel.title || `${difficulty.name} Guitar & Bass Tabs`,\n      description,\n      type: 'website',\n      url: pageUrl,\n      siteName: 'DadRock Tabs',\n    },\n  };\n}\n\n"""
text = text[:start] + metadata_block + text[end:]

page_anchor = """const difficulty = DIFFICULTY_LEVELS[level];\n\n  if (!difficulty) {\n    notFound();\n  }\n"""
page_replacement = """const difficulty = DIFFICULTY_LEVELS[level];\n\n  if (!difficulty) {\n    notFound();\n  }\n\n  const pageUrl = generateCanonical(`/difficulty/${level}`, currentLang);\n"""
if page_anchor not in text:
    raise SystemExit('difficulty page anchor missing')
text = text.replace(page_anchor, page_replacement, 1)
text = text.replace("    'name': `${difficulty.name} Guitar Tabs`,\n    'description': difficulty.longDescription,\n    'url': `https://dadrocktabs.com/difficulty/${level}`,", "    'name': t.levels?.[level]?.title || `${difficulty.name} Guitar Tabs`,\n    'description': t.levels?.[level]?.longDescription || difficulty.longDescription,\n    'url': pageUrl,", 1)
difficulty.write_text(text, encoding='utf-8')

localized_difficulty = ROOT / 'app/[lang]/difficulty/[level]/page.js'
localized_difficulty.write_text(
    "export { default, generateMetadata } from '../../../difficulty/[level]/page';\n",
    encoding='utf-8',
)

# Learn hub: replace fixed English metadata with params-aware metadata.
learn = ROOT / 'app/learn/page.js'
text = learn.read_text(encoding='utf-8')
learn_header_import = "import LearnHeader from '@/components/LearnHeader';\n"
if seo_import not in text:
    if learn_header_import not in text:
        raise SystemExit('learn import anchor missing')
    text = text.replace(learn_header_import, learn_header_import + seo_import, 1)
start = text.index('export const metadata = {')
end = text.index('export default async function LearnPage', start)
learn_metadata = """export async function generateMetadata({ params }) {\n  const resolvedParams = await params;\n  const lang = resolvedParams?.lang || 'en';\n  const pageUrl = generateCanonical('/learn', lang);\n\n  return {\n    title: 'Learn Guitar - Free Guides, Tips & Techniques | DadRock Tabs',\n    description: 'Free guitar learning guides covering techniques, theory, and practice tips. Learn palm muting, read tabs, build speed, and master your favorite rock songs.',\n    keywords: 'learn guitar, guitar techniques, guitar tips, how to play guitar, rock guitar guide, guitar lessons, guitar tutorial, free guitar guides',\n    alternates: generateAlternates('/learn', lang),\n    openGraph: {\n      title: 'Learn Guitar - Free Guides & Techniques',\n      description: 'Free guitar learning guides covering techniques, tips, and practice methods for rock and metal guitarists.',\n      type: 'website',\n      url: pageUrl,\n      siteName: 'DadRock Tabs',\n    },\n  };\n}\n\n"""
text = text[:start] + learn_metadata + text[end:]
lang_anchor = """  const lang = resolvedParams?.lang || 'en';\n  const t = getSubPageTranslation(lang);\n"""
lang_replacement = """  const lang = resolvedParams?.lang || 'en';\n  const pageUrl = generateCanonical('/learn', lang);\n  const t = getSubPageTranslation(lang);\n"""
if lang_anchor not in text:
    raise SystemExit('learn lang anchor missing')
text = text.replace(lang_anchor, lang_replacement, 1)
text = text.replace("    'url': 'https://dadrocktabs.com/learn',", "    'url': pageUrl,", 1)
text = text.replace("          'url': `https://dadrocktabs.com/learn/${guide.slug}`,", "          'url': `https://dadrocktabs.com${getLocalizedPath(`/learn/${guide.slug}`, lang)}`,", 1)
learn.write_text(text, encoding='utf-8')

localized_learn = ROOT / 'app/[lang]/learn/page.js'
localized_learn.write_text(
    "export { default, generateMetadata } from '../../learn/page';\n",
    encoding='utf-8',
)

# Top Lessons: params-aware metadata + schema URL and localized wrapper export.
top = ROOT / 'app/top-lessons/page.js'
text = top.read_text(encoding='utf-8')
text = text.replace(
    "import { generateAlternates } from '@/lib/seo';",
    "import { generateAlternates, generateCanonical } from '@/lib/seo';",
    1,
)
start = text.index('// SEO Metadata')
end = text.index('// JSON-LD Schema for SEO', start)
top_metadata = """// SEO Metadata\nexport async function generateMetadata({ params }) {\n  const resolvedParams = await params;\n  const lang = resolvedParams?.lang || 'en';\n  const pageUrl = generateCanonical('/top-lessons', lang);\n\n  return {\n    title: 'Top 10 Most Viewed Guitar Lessons | DadRock Tabs',\n    description: 'Discover the most popular guitar and bass tab video lessons at DadRock Tabs. Our top 10 most-watched tutorials feature classic rock, heavy metal, and hair metal songs from legendary artists.',\n    keywords: 'most viewed guitar lessons, popular bass tabs, top guitar tutorials, best rock lessons, classic rock tabs, heavy metal guitar, free guitar lessons, DadRock Tabs',\n    alternates: generateAlternates('/top-lessons', lang),\n    openGraph: {\n      title: 'Top 10 Most Viewed Guitar Lessons | DadRock Tabs',\n      description: 'Discover the most popular guitar lessons at DadRock Tabs. Learn the songs everyone loves!',\n      type: 'website',\n      url: pageUrl,\n    },\n    twitter: {\n      card: 'summary_large_image',\n      title: 'Top 10 Most Viewed Guitar Lessons | DadRock Tabs',\n      description: 'Discover the most popular guitar lessons at DadRock Tabs.',\n    },\n  };\n}\n\n"""
text = text[:start] + top_metadata + text[end:]
text = text.replace(
    "function generateSchema() {\n  return {",
    "function generateSchema(lang = 'en') {\n  const pageUrl = generateCanonical('/top-lessons', lang);\n  return {",
    1,
)
text = text.replace("    url: 'https://dadrocktabs.com/top-lessons',", "    url: pageUrl,", 1)
text = text.replace(
    "export default async function TopLessonsPage() {\n  // Fetch top videos on the server for SEO",
    "export default async function TopLessonsPage({ params } = {}) {\n  const resolvedParams = params ? await params : {};\n  const lang = resolvedParams?.lang || 'en';\n\n  // Fetch top videos on the server for SEO",
    1,
)
text = text.replace('JSON.stringify(generateSchema())', 'JSON.stringify(generateSchema(lang))', 1)
top.write_text(text, encoding='utf-8')

localized_top = ROOT / 'app/[lang]/top-lessons/page.js'
localized_top.write_text(
    "export { default, generateMetadata } from '../../top-lessons/page';\n",
    encoding='utf-8',
)

# Guards.
checks = {
    'app/layout.js': ["'x-default': baseUrl"],
    'app/difficulty/[level]/page.js': ["generateAlternates(`/difficulty/${level}`, currentLang)", "'url': pageUrl"],
    'app/[lang]/difficulty/[level]/page.js': ['generateMetadata'],
    'app/learn/page.js': ["generateAlternates('/learn', lang)", "'url': pageUrl"],
    'app/[lang]/learn/page.js': ['generateMetadata'],
    'app/top-lessons/page.js': ["generateAlternates('/top-lessons', lang)", 'generateSchema(lang)'],
    'app/[lang]/top-lessons/page.js': ['generateMetadata'],
}
for rel, fragments in checks.items():
    data = (ROOT / rel).read_text(encoding='utf-8')
    for fragment in fragments:
        if fragment not in data:
            raise SystemExit(f'{rel}: missing {fragment}')

print('Remaining localized metadata coverage completed.')
