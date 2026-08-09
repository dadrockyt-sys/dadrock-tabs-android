from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Dedicated song pages: YouTube is an embedded player, not a raw content file.
for rel in ['app/songs/[slug]/page.js', 'app/[lang]/songs/[slug]/page.js']:
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    text = text.replace(
        "        'uploadDate': song.publishedAt || new Date().toISOString(),\n        'contentUrl': `https://www.youtube.com/watch?v=${song.videoId}`,\n        'embedUrl': `https://www.youtube.com/embed/${song.videoId}`,",
        "        'uploadDate': song.publishedAt || undefined,\n        'embedUrl': `https://www.youtube.com/embed/${song.videoId}`,",
        1,
    )
    if "'contentUrl': `https://www.youtube.com/watch?v=${song.videoId}`" in text:
        raise SystemExit(f'{rel}: YouTube watch URL still used as contentUrl')
    path.write_text(text, encoding='utf-8')

# Localized artist collection VideoObjects: expose the YouTube embed player when the
# stored video_id is valid; don't label a YouTube watch page as raw video content.
artist = ROOT / 'app/[lang]/artist/[slug]/page.js'
text = artist.read_text(encoding='utf-8')
old = """              'thumbnailUrl': video.thumbnail,\n              'uploadDate': video.created_at,\n              'contentUrl': video.youtube_url,\n              'publisher': { '@id': 'https://dadrocktabs.com/#organization' }\n"""
new = """              'thumbnailUrl': video.thumbnail,\n              'uploadDate': video.created_at || undefined,\n              'embedUrl': /^[a-zA-Z0-9_-]{11}$/.test(video.video_id || '')\n                ? `https://www.youtube.com/embed/${video.video_id}`\n                : undefined,\n              'publisher': { '@id': 'https://dadrocktabs.com/#organization' }\n"""
if old not in text:
    raise SystemExit('localized artist VideoObject block not found')
text = text.replace(old, new, 1)
artist.write_text(text, encoding='utf-8')

checks = {
    'app/songs/[slug]/page.js': ["'uploadDate': song.publishedAt || undefined", "'embedUrl': `https://www.youtube.com/embed/${song.videoId}`"],
    'app/[lang]/songs/[slug]/page.js': ["'uploadDate': song.publishedAt || undefined", "'embedUrl': `https://www.youtube.com/embed/${song.videoId}`"],
    'app/[lang]/artist/[slug]/page.js': ["'embedUrl': /^[a-zA-Z0-9_-]{11}$/.test(video.video_id || '')", "'uploadDate': video.created_at || undefined"],
}
for rel, fragments in checks.items():
    data = (ROOT / rel).read_text(encoding='utf-8')
    for fragment in fragments:
        if fragment not in data:
            raise SystemExit(f'{rel}: missing {fragment}')

print('Video structured data now uses embed URLs and real publication dates only.')
