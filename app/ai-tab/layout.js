export const metadata = {
  title: 'AI Guitar & Bass Tab Generator | DadRock Tabs',
  description:
    'Upload your own audio and generate AI-assisted lead guitar, rhythm guitar, or bass tablature with a preview before download.',
  alternates: {
    canonical: 'https://dadrocktabs.com/ai-tab',
  },
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    title: 'AI Guitar & Bass Tab Generator | DadRock Tabs',
    description:
      'Upload your own audio and generate AI-assisted lead guitar, rhythm guitar, or bass tablature.',
    url: 'https://dadrocktabs.com/ai-tab',
    siteName: 'DadRock Tabs',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Guitar & Bass Tab Generator | DadRock Tabs',
    description:
      'Upload your own audio and generate AI-assisted lead guitar, rhythm guitar, or bass tablature.',
  },
};

export default function AiTabLayout({ children }) {
  return children;
}
