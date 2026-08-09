import { generateAlternates } from '@/lib/seo';

export const metadata = {
  title: "What's New - Latest Guitar & Bass Lessons | DadRock Tabs",
  description: 'See the latest guitar and bass tab lessons, tutorials, and newly added songs on DadRock Tabs.',
  alternates: generateAlternates('/whats-new'),
  openGraph: {
    title: "What's New | DadRock Tabs",
    description: 'Fresh guitar and bass tab lessons and tutorials from DadRock Tabs.',
    type: 'website',
    url: 'https://dadrocktabs.com/whats-new',
    siteName: 'DadRock Tabs',
  },
};

export default function WhatsNewLayout({ children }) {
  return children;
}
