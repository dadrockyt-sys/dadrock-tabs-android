from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(path, old, new, label):
    text = path.read_text(encoding='utf-8')
    if new in text:
        return
    if old not in text:
        raise SystemExit(f'{label}: expected anchor not found in {path}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


# Localized homepage: self-canonical, localized OG/WebPage URL, x-default hreflang.
home = ROOT / 'app/[lang]/page.js'
text = home.read_text(encoding='utf-8')
text = text.replace(
    "  locales.forEach(l => {\n    languages[l] = l === 'en' ? baseUrl : `${baseUrl}/${l}`;\n  });\n",
    "  locales.forEach(l => {\n    languages[l] = l === 'en' ? baseUrl : `${baseUrl}/${l}`;\n  });\n  languages['x-default'] = baseUrl;\n\n  const currentUrl = lang === 'en' ? baseUrl : `${baseUrl}/${lang}`;\n",
    1,
)
text = text.replace("        '@id': `${baseUrl}/#webpage`,\n        'url': baseUrl,", "        '@id': `${currentUrl}/#webpage`,\n        'url': currentUrl,", 1)
text = text.replace("      // ALL locale pages point canonical to the English homepage\n      // This tells Google the English version is the primary page\n      canonical: baseUrl,", "      canonical: currentUrl,", 1)
text = text.replace("      url: baseUrl,\n      siteName: 'DadRock Tabs',", "      url: currentUrl,\n      siteName: 'DadRock Tabs',", 1)
home.write_text(text, encoding='utf-8')

# Localized songs: self-canonical + hreflang and localized OG URL.
song = ROOT / 'app/[lang]/songs/[slug]/page.js'
text = song.read_text(encoding='utf-8')
text = text.replace(
    "      alternates: generateAlternates(`/songs/${slug}`),",
    "      alternates: generateAlternates(`/songs/${slug}`, lang),",
    1,
)
text = text.replace(
    "        url: `https://dadrocktabs.com/songs/${slug}`,\n        siteName: 'DadRock Tabs',",
    "        url: `https://dadrocktabs.com/${lang}/songs/${slug}`,\n        siteName: 'DadRock Tabs',",
    1,
)
song.write_text(text, encoding='utf-8')

# Localized artists: use the shared alternate map rather than canonical-only metadata.
artist = ROOT / 'app/[lang]/artist/[slug]/page.js'
text = artist.read_text(encoding='utf-8')
import_anchor = "import { getSubPageTranslation } from '@/lib/subPageI18n';\n"
if "import { generateAlternates } from '@/lib/seo';" not in text:
    if import_anchor not in text:
        raise SystemExit('artist import anchor missing')
    text = text.replace(import_anchor, import_anchor + "import { generateAlternates } from '@/lib/seo';\n", 1)
text = text.replace(
    "    alternates: {\n  canonical: `https://dadrocktabs.com/${lang}/artist/${slug}`,\n},",
    "    alternates: generateAlternates(`/artist/${slug}`, lang),",
    1,
)
artist.write_text(text, encoding='utf-8')

# Localized coming-soon: convert fixed English metadata into per-locale metadata.
coming = ROOT / 'app/[lang]/coming-soon/page.js'
text = coming.read_text(encoding='utf-8')
start = text.index('// SEO Metadata')
end = text.index('// JSON-LD Schema for SEO')
metadata_block = """// SEO Metadata\nexport async function generateMetadata({ params }) {\n  const resolvedParams = await params;\n  const lang = resolvedParams?.lang || 'en';\n  const pageUrl = lang === 'en'\n    ? 'https://dadrocktabs.com/coming-soon'\n    : `https://dadrocktabs.com/${lang}/coming-soon`;\n\n  return {\n    title: 'Upcoming Guitar Lessons & Bass Tabs Schedule | DadRock Tabs',\n    description: 'Check out the upcoming guitar and bass tab video lessons schedule at DadRock Tabs. See what classic rock, heavy metal, and hair metal songs are coming soon. Free video tutorials for Van Halen, Metallica, AC/DC, Led Zeppelin, and more legendary artists. Never miss a new lesson - view our complete release schedule!',\n    keywords: 'upcoming guitar lessons, bass tabs schedule, new guitar tutorials, classic rock tabs, heavy metal lessons, hair metal guitar, free guitar tabs, DadRock Tabs schedule',\n    openGraph: {\n      title: 'Upcoming Guitar Lessons Schedule | DadRock Tabs',\n      description: 'See what classic rock and metal guitar lessons are coming soon to DadRock Tabs. Free video tutorials for legendary artists.',\n      type: 'website',\n      url: pageUrl,\n    },\n    twitter: {\n      card: 'summary_large_image',\n      title: 'Upcoming Guitar Lessons Schedule | DadRock Tabs',\n      description: 'See what classic rock and metal guitar lessons are coming soon to DadRock Tabs.',\n    },\n    alternates: generateAlternates('/coming-soon', lang),\n  };\n}\n\n"""
text = text[:start] + metadata_block + text[end:]
coming.write_text(text, encoding='utf-8')

# Localized Quickies had no page-level metadata at all. Add a locale-aware version.
quickies = ROOT / 'app/[lang]/quickies/page.js'
text = quickies.read_text(encoding='utf-8')
if "import { generateAlternates } from '@/lib/seo';" not in text:
    text = text.replace(
        "import QuickiesClient from '../../quickies/QuickiesClient';\n",
        "import QuickiesClient from '../../quickies/QuickiesClient';\nimport { generateAlternates } from '@/lib/seo';\n",
        1,
    )
if 'export async function generateMetadata' not in text:
    insert = """\nexport async function generateMetadata({ params }) {\n  const resolvedParams = await params;\n  const lang = resolvedParams?.lang || 'en';\n  const pageUrl = lang === 'en'\n    ? 'https://dadrocktabs.com/quickies'\n    : `https://dadrocktabs.com/${lang}/quickies`;\n\n  return {\n    title: 'DadRock Tabs Quickies - Quick Guitar & Bass Lessons | DadRock Tabs',\n    description: 'Quick guitar and bass tab lessons from DadRock Tabs. Short, focused tutorials that get you playing classic rock and heavy metal riffs fast.',\n    openGraph: {\n      title: 'DadRock Tabs Quickies - Quick Guitar & Bass Lessons',\n      description: 'Quick guitar and bass tab lessons — short, sweet, and straight to the riff!',\n      type: 'website',\n      url: pageUrl,\n      siteName: 'DadRock Tabs',\n    },\n    alternates: generateAlternates('/quickies', lang),\n  };\n}\n\n"""
    text = text.replace("export const dynamic = 'force-dynamic';\n", "export const dynamic = 'force-dynamic';\n" + insert, 1)
quickies.write_text(text, encoding='utf-8')

# Parent learning guides already understand params.lang; give them the full hreflang map.
guide = ROOT / 'app/learn/[slug]/page.js'
text = guide.read_text(encoding='utf-8')
if "import { generateAlternates } from '@/lib/seo';" not in text:
    text = text.replace(
        "import LearnHeader from '@/components/LearnHeader';\n",
        "import LearnHeader from '@/components/LearnHeader';\nimport { generateAlternates } from '@/lib/seo';\n",
        1,
    )
text = text.replace(
    "    alternates: {\n      canonical: pageUrl\n    },",
    "    alternates: generateAlternates(`/learn/${slug}`, lang),",
    1,
)
guide.write_text(text, encoding='utf-8')

# Guards.
checks = {
    'app/[lang]/page.js': ["canonical: currentUrl", "languages['x-default'] = baseUrl"],
    'app/[lang]/songs/[slug]/page.js': ["generateAlternates(`/songs/${slug}`, lang)"],
    'app/[lang]/artist/[slug]/page.js': ["generateAlternates(`/artist/${slug}`, lang)"],
    'app/[lang]/coming-soon/page.js': ["generateAlternates('/coming-soon', lang)"],
    'app/[lang]/quickies/page.js': ["generateAlternates('/quickies', lang)"],
    'app/learn/[slug]/page.js': ["generateAlternates(`/learn/${slug}`, lang)"],
}
for rel, fragments in checks.items():
    data = (ROOT / rel).read_text(encoding='utf-8')
    for fragment in fragments:
        if fragment not in data:
            raise SystemExit(f'{rel}: missing {fragment}')

print('Localized canonical and hreflang metadata aligned.')
