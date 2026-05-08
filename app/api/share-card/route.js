import { ImageResponse } from '@vercel/og';

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const song = searchParams.get('song') || 'Amazing Song';
  const artist = searchParams.get('artist') || 'Great Artist';
  const type = searchParams.get('type') || 'learned'; // learned, streak, badge
  const value = searchParams.get('value') || '';

  let headline = '';
  let subtext = '';

  switch (type) {
    case 'learned':
      headline = `I just learned`;
      subtext = `${song} by ${artist}`;
      break;
    case 'streak':
      headline = `${value} Day Streak!`;
      subtext = `Practicing guitar daily on DadRock Tabs`;
      break;
    case 'badge':
      headline = `Achievement Unlocked!`;
      subtext = value || 'Guitar Hero';
      break;
    case 'progress':
      headline = `${value} Songs Learned!`;
      subtext = `on DadRock Tabs`;
      break;
    default:
      headline = song;
      subtext = artist;
  }

  return new ImageResponse(
    (
      <div
        style={{
          width: '1200px',
          height: '630px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #1a0a00 0%, #2d1200 30%, #1a0a00 70%, #0d0500 100%)',
          fontFamily: 'sans-serif',
          position: 'relative',
        }}
      >
        {/* Fire border top */}
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '8px', background: 'linear-gradient(90deg, #ff4500, #ff8c00, #ffd700, #ff8c00, #ff4500)', display: 'flex' }} />
        {/* Fire border bottom */}
        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '8px', background: 'linear-gradient(90deg, #ff4500, #ff8c00, #ffd700, #ff8c00, #ff4500)', display: 'flex' }} />
        
        {/* Logo */}
        <div style={{ fontSize: '36px', color: '#ff8c00', fontWeight: 'bold', marginBottom: '20px', display: 'flex' }}>DADROCK TABS</div>
        
        {/* Main content */}
        <div style={{ fontSize: '52px', color: '#ffffff', fontWeight: 'bold', textAlign: 'center', marginBottom: '16px', display: 'flex', maxWidth: '900px' }}>{headline}</div>
        <div style={{ fontSize: '38px', color: '#ffd700', textAlign: 'center', display: 'flex', maxWidth: '900px' }}>{subtext}</div>
        
        {/* CTA */}
        <div style={{ marginTop: '40px', padding: '12px 32px', background: '#ff4500', borderRadius: '8px', fontSize: '24px', color: '#fff', fontWeight: 'bold', display: 'flex' }}>Learn Guitar Tabs Free →</div>
      </div>
    ),
    { width: 1200, height: 630 }
  );
}
