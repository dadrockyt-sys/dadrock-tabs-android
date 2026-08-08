from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / "middleware.js"
text = path.read_text(encoding="utf-8")

# 1) www canonicalization should also remove the default /en prefix in the same hop.
old = """    // Handle /en → /\n    if (cleanPath === '/en') cleanPath = '/';\n"""
new = """    // Handle default English locale in the same www canonicalization hop.\n    if (cleanPath === '/en') cleanPath = '/';\n    else if (cleanPath.startsWith('/en/')) cleanPath = cleanPath.slice(3) || '/';\n"""
if old not in text:
    raise SystemExit("www /en redirect anchor not found")
text = text.replace(old, new, 1)

# 2) Trailing-dash cleanup should preserve supported non-English locales, but strip /en.
old = """  // ─── 4b. Strip trailing dashes from artist/song slugs ───\n  // GSC indexes URLs like /artist/rush- or /de/artist/rush- \n  // Always redirect to English canonical (strip locale + trailing dash in one hop)\n  const trailingDashMatch = pathname.match(/^\\/((?:[a-z]{2}(?:-[a-z]{2})?\\/)?(?:artist|songs))\\/(.+)-$/);\n  if (trailingDashMatch) {\n    const prefix = trailingDashMatch[1];\n    const cleanSlug = trailingDashMatch[2];\n    // Strip locale prefix if present to avoid redirect chain\n    const cleanPrefix = prefix.replace(/^[a-z]{2}(?:-[a-z]{2})?\\//,'');\n    const cleanUrl = new URL(`/${cleanPrefix}/${cleanSlug}`, request.url);\n    cleanUrl.search = request.nextUrl.search;\n    return NextResponse.redirect(cleanUrl, 301);\n  }\n"""
new = """  // ─── 4b. Strip trailing dashes from artist/song slugs ───\n  // Preserve supported translated routes such as /de/artist/rush-, while default\n  // English /en/... collapses directly to the unprefixed canonical.\n  const trailingDashMatch = pathname.match(\n    /^\\/(?:(es|pt|pt-br|de|fr|it|ja|ko|zh|ru|hi|sv|fi|en)\\/)?(artist|songs)\\/(.+)-$/\n  );\n  if (trailingDashMatch) {\n    const [, locale, routeType, cleanSlug] = trailingDashMatch;\n    const localePrefix = locale && locale !== 'en' ? `/${locale}` : '';\n    const cleanUrl = new URL(`${localePrefix}/${routeType}/${cleanSlug}`, request.url);\n    cleanUrl.search = request.nextUrl.search;\n    return NextResponse.redirect(cleanUrl, 301);\n  }\n"""
if old not in text:
    raise SystemExit("trailing-dash block not found")
text = text.replace(old, new, 1)

# 3) Known missing-song redirects should collapse /en to default English in the same hop.
old = """      // Extract locale prefix if present\n      const localePrefix = pathname.match(/^(\\/[a-z]{2}(?:-[a-z]{2})?)\\/songs\\//);\n      const prefix = localePrefix ? localePrefix[1] : '';\n      return NextResponse.redirect(new URL(`${prefix}/artist/${artistSlug}`, request.url), 301);\n"""
new = """      // Preserve translated locales, but collapse default /en directly to English canonical.\n      const localePrefix = pathname.match(\n        /^\\/(es|pt|pt-br|de|fr|it|ja|ko|zh|ru|hi|sv|fi|en)\\/songs\\//\n      );\n      const locale = localePrefix?.[1];\n      const prefix = locale && locale !== 'en' ? `/${locale}` : '';\n      return NextResponse.redirect(new URL(`${prefix}/artist/${artistSlug}`, request.url), 301);\n"""
if old not in text:
    raise SystemExit("known missing-song redirect block not found")
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")

updated = path.read_text(encoding="utf-8")
for expected in [
    "cleanPath.startsWith('/en/')",
    "locale && locale !== 'en'",
    "const prefix = locale && locale !== 'en'",
]:
    if expected not in updated:
        raise SystemExit(f"Expected chain-collapse fragment missing: {expected}")

print("Legacy redirect chains now collapse to single-hop canonicals.")
