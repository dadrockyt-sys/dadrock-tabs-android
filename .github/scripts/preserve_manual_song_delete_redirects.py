from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# --- Admin manual delete route ---
sync_path = ROOT / "app/api/admin/sync-songs/route.js"
text = sync_path.read_text(encoding="utf-8")

import_anchor = "import { v4 as uuidv4 } from 'uuid';\n"
import_line = "import { artistToSlug } from '@/lib/slugify';\n"
if import_line not in text:
    if import_anchor not in text:
        raise SystemExit("sync-songs import anchor not found")
    text = text.replace(import_anchor, import_anchor + import_line, 1)

old = """    const db = await getDb();\n    const result = await db.collection('song_pages').deleteOne({ videoId });\n\n    if (result.deletedCount === 0) {\n      return NextResponse.json({ error: 'Song page not found' }, { status: 404 });\n    }\n\n    return NextResponse.json({ success: true, message: 'Song page deleted' });\n"""
new = """    const db = await getDb();\n    const song = await db.collection('song_pages').findOne(\n      { videoId },\n      { projection: { slug: 1, artist: 1, title: 1 } }\n    );\n\n    if (!song) {\n      return NextResponse.json({ error: 'Song page not found' }, { status: 404 });\n    }\n\n    const cleanArtist = song.artist?.replace(/\\s*-\\s*$/, '').trim() || '';\n    const artistSlug = artistToSlug(cleanArtist);\n    const redirectTarget = artistSlug ? `/artist/${artistSlug}` : '/';\n\n    if (song.slug) {\n      await db.collection('song_redirects').updateOne(\n        { slug: song.slug },\n        {\n          $set: {\n            target: redirectTarget,\n            reason: 'admin_delete',\n            sourceVideoId: videoId,\n            songTitle: song.title || '',\n            artist: cleanArtist,\n            updated_at: new Date().toISOString(),\n          },\n          $setOnInsert: { created_at: new Date().toISOString() },\n        },\n        { upsert: true }\n      );\n    }\n\n    const result = await db.collection('song_pages').deleteOne({ videoId });\n\n    if (result.deletedCount === 0) {\n      return NextResponse.json({ error: 'Song page could not be deleted' }, { status: 409 });\n    }\n\n    return NextResponse.json({\n      success: true,\n      message: 'Song page deleted and permanent redirect preserved',\n      redirect: song.slug ? { slug: song.slug, target: redirectTarget } : null,\n    });\n"""
if old not in text:
    raise SystemExit("manual delete block not found")
text = text.replace(old, new, 1)
sync_path.write_text(text, encoding="utf-8")

# --- English song route ---
english_path = ROOT / "app/songs/[slug]/page.js"
text = english_path.read_text(encoding="utf-8")
old = """  if (!song) {\n    // Song not found — return proper 404 so Google de-indexes this URL\n    notFound();\n  }\n"""
new = """  if (!song) {\n    const savedRedirect = await db.collection('song_redirects').findOne(\n      { slug },\n      { projection: { target: 1 } }\n    );\n\n    if (savedRedirect?.target?.startsWith('/')) {\n      permanentRedirect(savedRedirect.target);\n    }\n\n    // Unknown missing URLs should remain real 404s.\n    notFound();\n  }\n"""
if old not in text:
    raise SystemExit("English song missing block not found")
english_path.write_text(text.replace(old, new, 1), encoding="utf-8")

# --- Localized song route ---
localized_path = ROOT / "app/[lang]/songs/[slug]/page.js"
text = localized_path.read_text(encoding="utf-8")
old = """  if (!song) {\n    // Song not found — return proper 404 so Google de-indexes this URL\n    notFound();\n  }\n"""
new = """  if (!song) {\n    const savedRedirect = await db.collection('song_redirects').findOne(\n      { slug },\n      { projection: { target: 1 } }\n    );\n\n    if (savedRedirect?.target?.startsWith('/')) {\n      const localizedTarget =\n        lang && lang !== 'en'\n          ? `/${lang}${savedRedirect.target}`\n          : savedRedirect.target;\n      permanentRedirect(localizedTarget);\n    }\n\n    // Unknown missing URLs should remain real 404s.\n    notFound();\n  }\n"""
if old not in text:
    raise SystemExit("Localized song missing block not found")
localized_path.write_text(text.replace(old, new, 1), encoding="utf-8")

# Guards
for rel in [
    "app/api/admin/sync-songs/route.js",
    "app/songs/[slug]/page.js",
    "app/[lang]/songs/[slug]/page.js",
]:
    data = (ROOT / rel).read_text(encoding="utf-8")
    if rel.endswith("sync-songs/route.js") and "collection('song_redirects').updateOne" not in data:
        raise SystemExit("Redirect registry write missing")
    if "songs/[slug]/page.js" in rel and "collection('song_redirects').findOne" not in data:
        raise SystemExit(f"Redirect registry lookup missing from {rel}")

print("Manual song deletions now preserve exact permanent redirects.")
