import { generateAlternates } from '@/lib/seo';

export const metadata = {
  title: 'Partners & Sponsorships | DadRock Tabs',
  description: 'Partner with DadRock Tabs for guitar and bass lesson sponsorships, product reviews, affiliate campaigns, website placements, and creator collaborations.',
  alternates: generateAlternates('/partners'),
  openGraph: {
    title: 'Partners & Sponsorships | DadRock Tabs',
    description: 'Partnership and sponsorship opportunities with DadRock Tabs.',
    type: 'website',
    url: 'https://dadrocktabs.com/partners',
    siteName: 'DadRock Tabs',
  },
};

export default function PartnersLayout({ children }) {
  return children;
}
