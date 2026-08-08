from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / "app/api/admin/sync-songs/route.js"
text = path.read_text(encoding="utf-8")

old = """    // Remove songs not in top 100 anymore\n    const top100VideoIds = top100.map(v => v.id);\n    const removeResult = await db.collection('song_pages').deleteMany({\n      videoId: { $nin: top100VideoIds }\n    });\n\n    return NextResponse.json({\n      success: true,\n      message: `Synced top ${top100.length} songs. Added ${addedCount} new, updated ${updatedCount}. Removed ${removeResult.deletedCount} old entries.`,\n      total_scanned: allVideos.length,\n      shorts_filtered: allVideos.length - regularVideos.length,\n      songs_synced: top100.length,\n      added: addedCount,\n      updated: updatedCount,\n      removed: removeResult.deletedCount\n    });\n"""

new = """    // Preserve previously published song pages even when they fall out of the current\n    // top 100. These URLs may already be indexed, bookmarked, or internally linked.\n    // Ranking changes must never turn a valid permanent song URL into a 404.\n    const top100VideoIds = top100.map(v => v.id);\n    const preservedCount = await db.collection('song_pages').countDocuments({\n      videoId: { $nin: top100VideoIds }\n    });\n\n    return NextResponse.json({\n      success: true,\n      message: `Synced top ${top100.length} songs. Added ${addedCount} new, updated ${updatedCount}. Preserved ${preservedCount} existing song pages outside the current top 100.`,\n      total_scanned: allVideos.length,\n      shorts_filtered: allVideos.length - regularVideos.length,\n      songs_synced: top100.length,\n      added: addedCount,\n      updated: updatedCount,\n      removed: 0,\n      preserved: preservedCount\n    });\n"""

if old not in text:
    raise SystemExit("Expected destructive top-100 cleanup block not found")

path.write_text(text.replace(old, new, 1), encoding="utf-8")

updated = path.read_text(encoding="utf-8")
if "db.collection('song_pages').deleteMany" in updated:
    raise SystemExit("A destructive song_pages deleteMany still remains in sync-songs")
if "preserved: preservedCount" not in updated:
    raise SystemExit("Preservation result was not added")

print("Song pages are now preserved when rankings change.")
