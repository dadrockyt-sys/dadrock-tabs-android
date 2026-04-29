import { ImageResponse } from 'next/og';

export const runtime = 'edge';

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const title = searchParams.get('title') || 'DadRock Tabs';
  const artist = searchParams.get('artist') || '';
  const type = searchParams.get('type') || 'song'; // song, artist, genre, era
  const thumbnail = searchParams.get('thumb') || '';

  // Color schemes based on type
  const colors = {
    song: { bg: '#18181b', accent: '#f59e0b', gradFrom: '#92400e', gradTo: '#dc2626' },
    artist: { bg: '#18181b', accent: '#f59e0b', gradFrom: '#7c2d12', gradTo: '#9333ea' },
    genre: { bg: '#18181b', accent: '#ef4444', gradFrom: '#1e3a5f', gradTo: '#7c2d12' },
    era: { bg: '#18181b', accent: '#a855f7', gradFrom: '#581c87', gradTo: '#be123c' },
  };

  const c = colors[type] || colors.song;

  return new ImageResponse(
    (
      <div
        style={{
          width: '1200px',
          height: '630px',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: c.bg,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Background gradient overlay */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `linear-gradient(135deg, ${c.gradFrom}44 0%, transparent 50%, ${c.gradTo}33 100%)`,
            display: 'flex',
          }}
        />
        
        {/* Decorative circles */}
        <div
          style={{
            position: 'absolute',
            top: '-80px',
            right: '-80px',
            width: '300px',
            height: '300px',
            borderRadius: '50%',
            background: `${c.accent}15`,
            display: 'flex',
          }}
        />
        <div
          style={{
            position: 'absolute',
            bottom: '-60px',
            left: '-60px',
            width: '250px',
            height: '250px',
            borderRadius: '50%',
            background: `${c.gradTo}20`,
            display: 'flex',
          }}
        />
        <div
          style={{
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            padding: '60px',
            flex: 1,
            position: 'relative',
            zIndex: '1',
          }}
        >
          {/* Left: Text content */}
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              flex: 1,
              paddingRight: thumbnail ? '40px' : '0',
            }}
          >
            {/* Type badge */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                marginBottom: '16px',
              }}
            >
              <div
                style={{
                  padding: '6px 16px',
                  borderRadius: '20px',
                  backgroundColor: `${c.accent}22`,
                  border: `2px solid ${c.accent}`,
                  color: c.accent,
                  fontSize: '16px',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '2px',
                  display: 'flex',
                }}
              >
                {type === 'song' ? '🎸 Guitar & Bass Tab' : type === 'artist' ? '🎵 Artist Collection' : type === 'genre' ? '🔥 Genre' : '📀 Era'}
              </div>
            </div>

            {/* Title */}
            <div
              style={{
                fontSize: title.length > 30 ? '42px' : '52px',
                fontWeight: 900,
                color: '#ffffff',
                lineHeight: 1.1,
                marginBottom: '16px',
                display: 'flex',
                flexWrap: 'wrap',
              }}
            >
              {title}
            </div>

            {/* Artist name */}
            {artist && (
              <div
                style={{
                  fontSize: '28px',
                  fontWeight: 600,
                  color: c.accent,
                  marginBottom: '24px',
                  display: 'flex',
                }}
              >
                by {artist}
              </div>
            )}

            {/* Tagline */}
            <div
              style={{
                fontSize: '18px',
                color: '#a1a1aa',
                display: 'flex',
              }}
            >
              Free video lesson with synchronized tablature
            </div>
          </div>

          {/* Right: Thumbnail */}
          {thumbnail && (
            <div
              style={{
                width: '320px',
                height: '320px',
                borderRadius: '24px',
                overflow: 'hidden',
                border: `3px solid ${c.accent}55`,
                boxShadow: `0 25px 50px ${c.gradFrom}66`,
                display: 'flex',
                flexShrink: 0,
              }}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={thumbnail}
                alt=""
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                }}
              />
            </div>
          )}
        </div>

        {/* Bottom bar - branding */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '20px 60px',
            borderTop: `1px solid ${c.accent}33`,
            position: 'relative',
            zIndex: '1',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
            }}
          >
            <div
              style={{
                fontSize: '24px',
                fontWeight: 800,
                color: c.accent,
                display: 'flex',
              }}
            >
              DadRock Tabs
            </div>
          </div>
          <div
            style={{
              fontSize: '16px',
              color: '#71717a',
              display: 'flex',
            }}
          >
            dadrocktabs.com
          </div>
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
    }
  );
}
