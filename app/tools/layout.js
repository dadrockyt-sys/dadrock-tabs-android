import { generateAlternates } from '@/lib/seo';

export const metadata = {
  title: 'Free Guitar Practice Tools | DadRock Tabs',
  description: 'Use free guitar practice tools from DadRock Tabs, including timing and practice utilities built for guitar and bass players.',
  alternates: generateAlternates('/tools'),
  openGraph: {
    title: 'Free Guitar Practice Tools | DadRock Tabs',
    description: 'Free practice utilities for guitar and bass players.',
    type: 'website',
    url: 'https://dadrocktabs.com/tools',
    siteName: 'DadRock Tabs',
  },
};

export default function ToolsLayout({ children }) {
  return children;
}
