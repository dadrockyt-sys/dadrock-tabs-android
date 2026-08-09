from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Localized song structured data should describe the localized page itself.
song = ROOT / 'app/[lang]/songs/[slug]/page.js'
text = song.read_text(encoding='utf-8')
anchor = """  // JSON-LD Schema — MusicRecording + VideoObject + BreadcrumbList + HowTo\n  const durationMinutes = song.duration ? Math.floor(song.duration / 60) : 5;\n"""
replacement = """  // JSON-LD Schema — MusicRecording + VideoObject + BreadcrumbList + HowTo\n  const durationMinutes = song.duration ? Math.floor(song.duration / 60) : 5;\n  const localizedHomeUrl = `https://dadrocktabs.com/${lang}`;\n  const localizedArtistUrl = `https://dadrocktabs.com/${lang}/artist/${artistToSlug(cleanArtist)}`;\n  const localizedSongUrl = `https://dadrocktabs.com/${lang}/songs/${slug}`;\n"""
if anchor not in text:
    raise SystemExit('localized song schema anchor missing')
text = text.replace(anchor, replacement, 1)
text = text.replace("'item': 'https://dadrocktabs.com'", "'item': localizedHomeUrl", 1)
text = text.replace("'item': `https://dadrocktabs.com/artist/${artistToSlug(cleanArtist)}`", "'item': localizedArtistUrl", 1)
text = text.replace("'item': `https://dadrocktabs.com/songs/${slug}`", "'item': localizedSongUrl", 1)
text = text.replace("'url': `https://dadrocktabs.com/artist/${artistToSlug(cleanArtist)}`", "'url': localizedArtistUrl", 1)
# Replace MusicRecording + HowTo/steps song URLs, but not YouTube URLs.
text = text.replace("'url': `https://dadrocktabs.com/songs/${slug}`", "'url': localizedSongUrl")
song.write_text(text, encoding='utf-8')

# Localized Coming Soon CollectionPage should use the localized route URL.
coming = ROOT / 'app/[lang]/coming-soon/page.js'
text = coming.read_text(encoding='utf-8')
text = text.replace(
    "function generateSchema(upcomingCount) {\n  return {",
    "function generateSchema(upcomingCount, lang = 'en') {\n  const pageUrl = lang === 'en'\n    ? 'https://dadrocktabs.com/coming-soon'\n    : `https://dadrocktabs.com/${lang}/coming-soon`;\n\n  return {",
    1,
)
text = text.replace("    url: 'https://dadrocktabs.com/coming-soon',", "    url: pageUrl,", 1)
page_anchor = """export default async function ComingSoonPage({ params }) {\n  // Fetch upcoming videos on the server for SEO\n"""
page_replacement = """export default async function ComingSoonPage({ params }) {\n  const resolvedParams = await params;\n  const lang = resolvedParams?.lang || 'en';\n\n  // Fetch upcoming videos on the server for SEO\n"""
if page_anchor not in text:
    raise SystemExit('coming-soon page anchor missing')
text = text.replace(page_anchor, page_replacement, 1)
text = text.replace('JSON.stringify(generateSchema(total))', 'JSON.stringify(generateSchema(total, lang))', 1)
text = text.replace('currentLang={params?.lang || \'en\'}', 'currentLang={lang}', 1)
coming.write_text(text, encoding='utf-8')

# Localized Artist breadcrumb roots should remain in the current language family.
artist = ROOT / 'app/[lang]/artist/[slug]/page.js'
text = artist.read_text(encoding='utf-8')
artist_anchor = """  // JSON-LD structured data for SEO — MusicGroup + BreadcrumbList + CollectionPage\n  const jsonLd = {\n"""
artist_replacement = """  // JSON-LD structured data for SEO — MusicGroup + BreadcrumbList + CollectionPage\n  const localizedHomeUrl = `https://dadrocktabs.com/${lang}`;\n  const localizedArtistUrl = `https://dadrocktabs.com/${lang}/artist/${slug}`;\n  const jsonLd = {\n"""
if artist_anchor not in text:
    raise SystemExit('localized artist schema anchor missing')
text = text.replace(artist_anchor, artist_replacement, 1)
text = text.replace("'item': `https://dadrocktabs.com`", "'item': localizedHomeUrl", 1)
text = text.replace("'item': `https://dadrocktabs.com`", "'item': localizedHomeUrl", 1)
text = text.replace("`https://dadrocktabs.com/${lang}/artist/${slug}`", "localizedArtistUrl")
artist.write_text(text, encoding='utf-8')

checks = {
    'app/[lang]/songs/[slug]/page.js': [
        'const localizedSongUrl',
        "'item': localizedSongUrl",
        "'url': localizedSongUrl",
        "'url': localizedArtistUrl",
    ],
    'app/[lang]/coming-soon/page.js': [
        'generateSchema(upcomingCount, lang',
        'JSON.stringify(generateSchema(total, lang))',
        'url: pageUrl',
    ],
    'app/[lang]/artist/[slug]/page.js': [
        'const localizedHomeUrl',
        'const localizedArtistUrl',
        "'item': localizedHomeUrl",
    ],
}
for rel, fragments in checks.items():
    data = (ROOT / rel).read_text(encoding='utf-8')
    for fragment in fragments:
        if fragment not in data:
            raise SystemExit(f'{rel}: missing {fragment}')

print('Localized JSON-LD URLs aligned with localized canonicals.')
