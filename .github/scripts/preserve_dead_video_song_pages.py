from pathlib import Path

# One-use housekeeping patch: dead source videos must not delete permanent DadRock URLs.
ROOT = Path(__file__).resolve().parents[2]

# 1) Legacy YouTube cleanup: mark matching song pages unavailable instead of deleting them.
catchall = ROOT / "app/api/[[...path]]/route.js"
text = catchall.read_text(encoding="utf-8")
old = """        // Also remove from song_pages if any dead videos exist there\n        if (deadYtIds.length > 0) {\n          for (const deadId of deadYtIds) {\n            await db.collection('song_pages').deleteMany({ videoId: deadId });\n          }\n        }\n"""
new = """        // Preserve permanent DadRock song URLs even if the source YouTube video dies.\n        // Mark the source as unavailable rather than turning an indexed song page into a 404.\n        if (deadYtIds.length > 0) {\n          for (const deadId of deadYtIds) {\n            await db.collection('song_pages').updateMany(\n              { videoId: deadId },\n              {\n                $set: {\n                  videoUnavailable: true,\n                  videoUnavailableAt: new Date().toISOString(),\n                  updated_at: new Date().toISOString(),\n                }\n              }\n            );\n          }\n        }\n"""
if old not in text:
    raise SystemExit("Legacy YouTube cleanup deletion block not found")
catchall.write_text(text.replace(old, new, 1), encoding="utf-8")

# 2) Health cleanup: this block attempted to delete song_pages using internal UUIDs rather than
# YouTube IDs. Remove it entirely so health maintenance can never destroy permanent song URLs.
health = ROOT / "app/api/admin/health/route.js"
text = health.read_text(encoding="utf-8")
old = """      // Also clean up from song_pages\n      for (const vid of video_ids) {\n        await db.collection('song_pages').deleteMany({ videoId: vid });\n      }\n\n"""
new = """      // Keep song_pages permanent. Removing a dead source video must not turn an\n      // already-indexed DadRock song URL into a 404.\n\n"""
if old not in text:
    raise SystemExit("Health cleanup song-page deletion block not found")
health.write_text(text.replace(old, new, 1), encoding="utf-8")

# Guards
for rel in ["app/api/[[...path]]/route.js", "app/api/admin/health/route.js"]:
    data = (ROOT / rel).read_text(encoding="utf-8")
    if "collection('song_pages').deleteMany" in data:
        raise SystemExit(f"Destructive song_pages deleteMany remains in {rel}")

print("Dead-video cleanup now preserves permanent song pages.")
