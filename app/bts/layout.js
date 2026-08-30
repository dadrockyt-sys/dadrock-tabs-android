const baseUrl =
  process.env.NEXT_PUBLIC_BASE_URL ||
  'https://dadrocktabs.com';

export const metadata = {
  title:
    'AI Backing Track Maker – Remove Guitar or Bass | DadRock Tabs',
  description:
    'Create custom guitar and bass backing tracks online. Upload audio, remove guitar, bass, or both with AI stem separation, and download an MP3 for practice.',
  keywords: [
    'backing track maker',
    'AI backing track maker',
    'remove guitar from song',
    'remove bass from song',
    'guitar backing track',
    'bass backing track',
    'AI stem separation',
    'guitar practice tracks',
    'bass practice tracks',
  ],
  alternates: {
    canonical: `${baseUrl}/bts`,
  },
  openGraph: {
    title:
      'AI Backing Track Maker – Remove Guitar or Bass | DadRock Tabs',
    description:
      'Create custom practice tracks by removing guitar, bass, or both with AI stem separation.',
    url: `${baseUrl}/bts`,
    siteName: 'DadRock Tabs',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title:
      'AI Backing Track Maker | DadRock Tabs',
    description:
      'Remove guitar, bass, or both from audio and build a custom MP3 practice track with AI stem separation.',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function BTSLayout({ children }) {
  return children;
}
