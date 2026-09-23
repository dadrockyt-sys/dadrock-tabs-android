export const STAIRWAY2FAST_REFERRAL_CODE = 'dadrock';

const VIDEO_ID_RE = /^[a-zA-Z0-9_-]{11}$/;

export function extractYouTubeVideoId(value) {
  if (!value) return '';

  if (typeof value === 'object') {
    const directId = String(value.videoId || value.video_id || '').trim();
    if (VIDEO_ID_RE.test(directId)) return directId;

    return extractYouTubeVideoId(
      value.youtubeUrl ||
      value.youtube_url ||
      value.url ||
      ''
    );
  }

  const input = String(value).trim();
  if (VIDEO_ID_RE.test(input)) return input;
  if (!input) return '';

  try {
    const url = new URL(input);
    const host = url.hostname.replace(/^www\./, '');

    if (host === 'youtu.be') {
      const id = url.pathname.split('/').filter(Boolean)[0] || '';
      return VIDEO_ID_RE.test(id) ? id : '';
    }

    if (host === 'youtube.com' || host === 'm.youtube.com' || host === 'music.youtube.com') {
      const watchId = url.searchParams.get('v') || '';
      if (VIDEO_ID_RE.test(watchId)) return watchId;

      const parts = url.pathname.split('/').filter(Boolean);
      if (['embed', 'shorts', 'live'].includes(parts[0])) {
        const id = parts[1] || '';
        return VIDEO_ID_RE.test(id) ? id : '';
      }
    }
  } catch {
    // Ignore malformed/non-URL values.
  }

  return '';
}

export function getStairway2FastUrl(value) {
  const videoId = extractYouTubeVideoId(value);
  if (!videoId) return '';

  return `https://stairway2fast.com/app/?v=${encodeURIComponent(videoId)}&ref=${encodeURIComponent(STAIRWAY2FAST_REFERRAL_CODE)}`;
}
