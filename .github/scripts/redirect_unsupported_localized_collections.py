from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / "middleware.js"
text = path.read_text(encoding="utf-8")

anchor = """  // ─── 8. Locale handling (i18n URL rewriting) ───\n"""
block = """  // ─── 8a. Collapse unsupported localized collection routes to English canonicals ───\n  // Genre, era, and playlist pages currently exist only in English. Old indexed URLs\n  // such as /ru/genre/heavy-metal should resolve permanently instead of returning 404.\n  const englishOnlyCollectionMatch = pathname.match(\n    /^\\/(?:es|pt|pt-br|de|fr|it|ja|ko|zh|ru|hi|sv|fi)\\/(genre|era|playlist)\\/(.+)$/\n  );\n  if (englishOnlyCollectionMatch) {\n    const [, collectionType, slug] = englishOnlyCollectionMatch;\n    const canonicalUrl = new URL(`/${collectionType}/${slug}`, request.url);\n    canonicalUrl.search = request.nextUrl.search;\n    return NextResponse.redirect(canonicalUrl, 301);\n  }\n\n"""

if block in text:
    raise SystemExit("Localized collection redirect already present")
if anchor not in text:
    raise SystemExit("Locale handling anchor not found")

text = text.replace(anchor, block + anchor, 1)
path.write_text(text, encoding="utf-8")

updated = path.read_text(encoding="utf-8")
for expected in [
    "englishOnlyCollectionMatch",
    "(genre|era|playlist)",
    "NextResponse.redirect(canonicalUrl, 301)",
]:
    if expected not in updated:
        raise SystemExit(f"Expected redirect fragment missing: {expected}")

print("Unsupported localized collection URLs now redirect to English canonicals.")
