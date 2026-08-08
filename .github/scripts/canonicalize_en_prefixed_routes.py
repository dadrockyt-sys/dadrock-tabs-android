from pathlib import Path

# One-use SEO housekeeping patch: English-prefixed routes collapse to default canonicals.
ROOT = Path(__file__).resolve().parents[2]
path = ROOT / "middleware.js"
text = path.read_text(encoding="utf-8")

anchor = """  // ─── 6. Handle /zn → redirect to /zh (common typo) ───\n"""
block = """  // ─── 5b. Canonicalize all English-prefixed routes ───\n  // English is the default locale, so /en/... is always a duplicate of /....\n  // Redirect in one hop and preserve the query string.\n  if (pathname.startsWith('/en/')) {\n    const canonicalPath = pathname.slice(3) || '/';\n    const canonicalUrl = new URL(canonicalPath, request.url);\n    canonicalUrl.search = request.nextUrl.search;\n    return NextResponse.redirect(canonicalUrl, 301);\n  }\n\n"""

if block in text:
    raise SystemExit("English-prefixed canonical redirect already present")
if anchor not in text:
    raise SystemExit("Expected middleware anchor not found")

text = text.replace(anchor, block + anchor, 1)
path.write_text(text, encoding="utf-8")

updated = path.read_text(encoding="utf-8")
for expected in ["pathname.startsWith('/en/')", "pathname.slice(3)", "NextResponse.redirect(canonicalUrl, 301)"]:
    if expected not in updated:
        raise SystemExit(f"Missing expected fragment: {expected}")

print("All /en/... duplicates now canonicalize to unprefixed English URLs.")
