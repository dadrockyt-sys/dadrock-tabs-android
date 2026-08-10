from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 1) Middleware: collapse any locale-prefixed legacy AI Tab route to canonical /ai-tab.
path = ROOT / 'middleware.js'
text = path.read_text(encoding='utf-8')
anchor = "  // ─── 1b. Retire legacy song-prefilled AI Tab URLs ───\n"
insert = """  // ─── 1a. Collapse localized AI Tab URLs to the single canonical tool ───
  // AI Tab is intentionally a single global entry point, not a localized route.
  // Old links like /pt-br/ai-tab?song=...&artist=... should never 404.
  const localizedAiTabMatch = pathname.match(
    /^\/(?:es|pt|pt-br|de|fr|it|ja|ko|zh|ru|hi|sv|fi|en)\/ai-tab$/
  );
  if (localizedAiTabMatch) {
    return NextResponse.redirect(new URL('/ai-tab', request.url), 301);
  }

"""
if anchor not in text:
    raise SystemExit('middleware anchor missing')
text = text.replace(anchor, insert + anchor, 1)
path.write_text(text, encoding='utf-8')

# Shared missing-song recovery block.
old_english = """    if (savedRedirect?.target?.startsWith('/')) {
      permanentRedirect(savedRedirect.target);
    }

    // Unknown missing URLs should remain real 404s.
    notFound();
"""
new_english = """    if (savedRedirect?.target?.startsWith('/')) {
      permanentRedirect(savedRedirect.target);
    }

    // Historical song pages may predate the redirect registry. If the old slug
    // begins with a real current artist slug, preserve user/Google value by
    // redirecting to that artist page. Truly unknown garbage remains a 404.
    const artistSlug = await findArtistFromSongSlug(db, slug);
    if (artistSlug) {
      permanentRedirect(`/artist/${artistSlug}`);
    }

    notFound();
"""

path = ROOT / 'app/songs/[slug]/page.js'
text = path.read_text(encoding='utf-8')
if old_english not in text:
    raise SystemExit('English song missing block not found')
text = text.replace(old_english, new_english, 1)
path.write_text(text, encoding='utf-8')

old_local = """    if (savedRedirect?.target?.startsWith('/')) {
      const localizedTarget =
        lang && lang !== 'en'
          ? `/${lang}${savedRedirect.target}`
          : savedRedirect.target;
      permanentRedirect(localizedTarget);
    }

    // Unknown missing URLs should remain real 404s.
    notFound();
"""
new_local = """    if (savedRedirect?.target?.startsWith('/')) {
      const localizedTarget =
        lang && lang !== 'en'
          ? `/${lang}${savedRedirect.target}`
          : savedRedirect.target;
      permanentRedirect(localizedTarget);
    }

    // Historical song pages may predate the redirect registry. Recover only
    // when the slug prefix matches a real current artist, preserving locale.
    const artistSlug = await findArtistFromSongSlug(db, slug);
    if (artistSlug) {
      const target = lang && lang !== 'en'
        ? `/${lang}/artist/${artistSlug}`
        : `/artist/${artistSlug}`;
      permanentRedirect(target);
    }

    notFound();
"""
path = ROOT / 'app/[lang]/songs/[slug]/page.js'
text = path.read_text(encoding='utf-8')
if old_local not in text:
    raise SystemExit('Localized song missing block not found')
text = text.replace(old_local, new_local, 1)
path.write_text(text, encoding='utf-8')

print('GSC 404 cleanup applied')
