from pathlib import Path
import re

# One-use cleanup for the retired per-song AI Tab launcher.
ROOT = Path(__file__).resolve().parents[2]

FILES = [
    "app/page.js",
    "components/SearchBar.js",
    "app/playlist/[slug]/page.js",
    "app/whats-new/page.js",
    "app/quickies/QuickiesClient.js",
    "app/coming-soon/ComingSoonClient.js",
    "app/top-lessons/TopLessonsClient.js",
    "app/songs/[slug]/SongPageClient.js",
    "app/artist/[slug]/ArtistPageClient.js",
    "app/[lang]/artist/[slug]/ArtistPageClient.js",
]

IMPORT_RE = re.compile(
    r"^import\s+AiTabButton\s+from\s+['\"]@/components/AiTabButton['\"];?\s*\n",
    re.MULTILINE,
)
JSX_RE = re.compile(r"\n[ \t]*<AiTabButton\b[^>]*/>[ \t]*", re.DOTALL)

changed = []

for rel in FILES:
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f"Expected file missing: {rel}")
    original = path.read_text(encoding="utf-8")
    updated = IMPORT_RE.sub("", original)
    updated = JSX_RE.sub("\n", updated)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        changed.append(rel)

# Add a permanent redirect for legacy song-prefilled AI Tab URLs that Google still knows.
# The standalone /ai-tab page remains untouched; only obsolete song/artist query parameters are removed.
middleware = ROOT / "middleware.js"
text = middleware.read_text(encoding="utf-8")
marker = "  // ─── 2. Block known vulnerability scanners ───\n"
block = """  // ─── 1b. Retire legacy song-prefilled AI Tab URLs ───\n  // Old per-song buttons linked to /ai-tab?song=...&artist=.... The product now\n  // has one canonical entry point at /ai-tab, so permanently collapse those URLs.\n  if (pathname === '/ai-tab' && (\n    request.nextUrl.searchParams.has('song') ||\n    request.nextUrl.searchParams.has('artist')\n  )) {\n    const cleanUrl = request.nextUrl.clone();\n    cleanUrl.searchParams.delete('song');\n    cleanUrl.searchParams.delete('artist');\n    return NextResponse.redirect(cleanUrl, 301);\n  }\n\n"""
if block not in text:
    if marker not in text:
        raise SystemExit("Could not find middleware insertion marker")
    text = text.replace(marker, block + marker, 1)
    middleware.write_text(text, encoding="utf-8")
    changed.append("middleware.js")

# Make sure all production references are gone before deleting the dead component.
remaining = []
for base in (ROOT / "app", ROOT / "components"):
    for path in base.rglob("*.js"):
        if path.name == "AiTabButton.js":
            continue
        data = path.read_text(encoding="utf-8", errors="ignore")
        if "AiTabButton" in data:
            remaining.append(str(path.relative_to(ROOT)))

if remaining:
    raise SystemExit("Remaining AiTabButton references: " + ", ".join(remaining))

component = ROOT / "components/AiTabButton.js"
if component.exists():
    component.unlink()
    changed.append("components/AiTabButton.js (deleted)")

# Guard against accidentally retaining a crawlable legacy URL generator.
legacy_generators = []
for base in (ROOT / "app", ROOT / "components", ROOT / "lib"):
    for path in base.rglob("*.js"):
        data = path.read_text(encoding="utf-8", errors="ignore")
        if "/ai-tab?" in data:
            legacy_generators.append(str(path.relative_to(ROOT)))

if legacy_generators:
    raise SystemExit("Legacy /ai-tab? generators remain: " + ", ".join(legacy_generators))

print("Legacy AI Tab housekeeping complete.")
for item in changed:
    print(f"  - {item}")
