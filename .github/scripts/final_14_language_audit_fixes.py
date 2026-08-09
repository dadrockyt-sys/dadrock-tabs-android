from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 1) Shared language selector: when a page doesn't supply a route-aware callback,
# preserve the current route for route families that genuinely exist in all locales.
path = ROOT / 'components/LanguageSelector.js'
text = path.read_text(encoding='utf-8')
anchor = "const LANG_STORAGE_KEY = 'dadrock_language';\n"
addition = """const LANG_STORAGE_KEY = 'dadrock_language';

const LOCALIZED_ROUTE_ROOTS = new Set([
  'artist',
  'songs',
  'coming-soon',
  'difficulty',
  'learn',
  'partners',
  'quickies',
  'tools',
  'top-lessons',
  'whats-new',
]);
"""
if anchor not in text:
    raise SystemExit('LanguageSelector storage anchor missing')
text = text.replace(anchor, addition, 1)
old = """ const handleLanguageChange = (newLang) => {
  setIsOpen(false);
  changeLang(newLang);

  if (onLanguageChange) {
    onLanguageChange(newLang);
  }
};
"""
new = """ const handleLanguageChange = (newLang) => {
  setIsOpen(false);
  changeLang(newLang);

  if (onLanguageChange) {
    onLanguageChange(newLang);
    return;
  }

  const parts = window.location.pathname.split('/').filter(Boolean);
  if (parts[0] && locales.includes(parts[0])) {
    parts.shift();
  }

  const routeRoot = parts[0] || '';
  if (routeRoot && !LOCALIZED_ROUTE_ROOTS.has(routeRoot)) {
    return;
  }

  const basePath = parts.length ? `/${parts.join('/')}` : '/';
  window.location.href = newLang === 'en'
    ? basePath
    : `/${newLang}${basePath === '/' ? '' : basePath}`;
};
"""
if old not in text:
    raise SystemExit('LanguageSelector handler anchor missing')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')

# 2) Song page: keep search and every internal discovery link in the active locale.
path = ROOT / 'app/songs/[slug]/SongPageClient.js'
text = path.read_text(encoding='utf-8')
replacements = {
    "const shareUrl = `https://dadrocktabs.com/songs/${song.slug}`;": "const shareUrl = lang === 'en'\n    ? `https://dadrocktabs.com/songs/${song.slug}`\n    : `https://dadrocktabs.com/${lang}/songs/${song.slug}`;",
    "<SearchBar variant=\"compact\" placeholder={t.searchPlaceholder || 'Search artists & songs...'} />": "<SearchBar variant=\"compact\" placeholder={t.searchPlaceholder || 'Search artists & songs...'} currentLang={lang} />",
    "href={`/artist/${artistSlug}`}": "href={lang === 'en' ? `/artist/${artistSlug}` : `/${lang}/artist/${artistSlug}`}",
    "href={`/songs/${s.slug}`}": "href={lang === 'en' ? `/songs/${s.slug}` : `/${lang}/songs/${s.slug}`}",
    "<Link href=\"/top-lessons\" className=\"text-amber-400 hover:text-amber-300 transition-colors font-medium\">": "<Link href={lang === 'en' ? '/top-lessons' : `/${lang}/top-lessons`} className=\"text-amber-400 hover:text-amber-300 transition-colors font-medium\">",
    "<Link href=\"/coming-soon\" className=\"text-purple-400 hover:text-purple-300 transition-colors font-medium\">": "<Link href={lang === 'en' ? '/coming-soon' : `/${lang}/coming-soon`} className=\"text-purple-400 hover:text-purple-300 transition-colors font-medium\">",
    "<Link href=\"/\" className=\"text-zinc-400 hover:text-white transition-colors font-medium\">": "<Link href={lang === 'en' ? '/' : `/${lang}`} className=\"text-zinc-400 hover:text-white transition-colors font-medium\">",
}
for old_text, new_text in replacements.items():
    if old_text not in text:
        raise SystemExit(f'SongPageClient anchor missing: {old_text[:80]}')
    text = text.replace(old_text, new_text)
path.write_text(text, encoding='utf-8')

# 3) Coming Soon: preserve locale for artist discovery, shares, and footer home link.
path = ROOT / 'app/coming-soon/ComingSoonClient.js'
text = path.read_text(encoding='utf-8')
old = "const shareUrl = 'https://dadrocktabs.com/coming-soon';"
new = "const shareUrl = lang === 'en'\n    ? 'https://dadrocktabs.com/coming-soon'\n    : `https://dadrocktabs.com/${lang}/coming-soon`;"
if old not in text:
    raise SystemExit('ComingSoon share URL anchor missing')
text = text.replace(old, new, 1)
old = "href={`/artist/${artistSlug}`}"
new = "href={lang === 'en' ? `/artist/${artistSlug}` : `/${lang}/artist/${artistSlug}`}"
if old not in text:
    raise SystemExit('ComingSoon artist link anchor missing')
text = text.replace(old, new)
old = '<Link href="/" className="text-zinc-400 hover:text-white transition-colors">'
new = '<Link href={lang === \'en\' ? \'/\' : `/${lang}`} className="text-zinc-400 hover:text-white transition-colors">'
if old not in text:
    raise SystemExit('ComingSoon footer link anchor missing')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')

# 4) RSS: only real dates, and point to an asset that actually exists.
path = ROOT / 'app/api/rss/route.js'
text = path.read_text(encoding='utf-8')
old = """  const items = songs.map(song => {
    const pubDate = song.created_at ? new Date(song.created_at).toUTCString() : now;
    return `
    <item>
      <title>${escapeXml(song.title)} - ${escapeXml(song.artist)}</title>
      <link>${baseUrl}/songs/${song.slug}</link>
      <guid isPermaLink=\"true\">${baseUrl}/songs/${song.slug}</guid>
      <description>Learn to play ${escapeXml(song.title)} by ${escapeXml(song.artist)} with guitar tabs and video tutorial on DadRock Tabs.</description>
      <pubDate>${pubDate}</pubDate>
      <category>${song.difficulty || 'Intermediate'}</category>
    </item>`;
  }).join('');
"""
new = """  const items = songs.map(song => {
    const parsedDate = song.created_at ? new Date(song.created_at) : null;
    const pubDate = parsedDate && !Number.isNaN(parsedDate.getTime())
      ? parsedDate.toUTCString()
      : null;
    return `
    <item>
      <title>${escapeXml(song.title)} - ${escapeXml(song.artist)}</title>
      <link>${baseUrl}/songs/${song.slug}</link>
      <guid isPermaLink=\"true\">${baseUrl}/songs/${song.slug}</guid>
      <description>Learn to play ${escapeXml(song.title)} by ${escapeXml(song.artist)} with guitar tabs and video tutorial on DadRock Tabs.</description>
${pubDate ? `      <pubDate>${pubDate}</pubDate>\\n` : ''}      <category>${escapeXml(song.difficulty || 'Intermediate')}</category>
    </item>`;
  }).join('');
"""
if old not in text:
    raise SystemExit('RSS item block anchor missing')
text = text.replace(old, new, 1)
text = text.replace('${baseUrl}/logo.png', '${baseUrl}/DadRock-Tabs-Logo.png')
path.write_text(text, encoding='utf-8')

# Final guards.
checks = {
    'components/LanguageSelector.js': ['LOCALIZED_ROUTE_ROOTS', "window.location.href = newLang === 'en'"],
    'app/songs/[slug]/SongPageClient.js': ['currentLang={lang}', "`/${lang}/songs/${s.slug}`", "`/${lang}/artist/${artistSlug}`"],
    'app/coming-soon/ComingSoonClient.js': ["`https://dadrocktabs.com/${lang}/coming-soon`", "`/${lang}/artist/${artistSlug}`"],
    'app/api/rss/route.js': ['DadRock-Tabs-Logo.png', 'Number.isNaN(parsedDate.getTime())'],
}
for rel, fragments in checks.items():
    data = (ROOT / rel).read_text(encoding='utf-8')
    for fragment in fragments:
        if fragment not in data:
            raise SystemExit(f'{rel}: missing guard fragment {fragment}')

print('Final 14-language discovery audit fixes applied.')
