import './globals.css';
import { locales } from '@/lib/i18n';

const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://dadrocktabs.com';

export const metadata = {
  metadataBase: new URL(baseUrl),
  title: {
    default: 'DadRock Tabs - Guitar & Bass Tabs for Classic Rock',
    template: '%s | DadRock Tabs',
  },
  description: 'Free guitar and bass tabs for classic rock hits. Learn to play Led Zeppelin, AC/DC, Van Halen, and more! Your go-to database for dad rock guitar tutorials.',
  keywords: 'guitar tabs, bass tabs, classic rock, dad rock, guitar lessons, Led Zeppelin, AC/DC, Van Halen, Metallica, rock music tutorials',
  authors: [{ name: 'DadRock Tabs' }],
  creator: 'DadRock Tabs',
  publisher: 'DadRock Tabs',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    title: 'DadRock Tabs - Guitar & Bass Tabs for Classic Rock',
    description: 'Free guitar and bass tabs for classic rock hits. Learn to play the songs that defined generations.',
    url: baseUrl,
    siteName: 'DadRock Tabs',
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'DadRock Tabs - Guitar & Bass Tabs for Classic Rock',
    description: 'Free guitar and bass tabs for classic rock hits.',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    // Add your Google Search Console verification code here if you have one
    // google: 'your-verification-code',
  },
};

// Generate hreflang alternate links
function generateAlternateLinks() {
  const links = locales.map(lang => ({
    rel: 'alternate',
    hrefLang: lang,
    href: lang === 'en' ? baseUrl : `${baseUrl}/${lang}`,
  }));
  
  // Add x-default for search engines
  links.push({
    rel: 'alternate',
    hrefLang: 'x-default',
    href: baseUrl,
  });
  
  return links;
}

export default function RootLayout({ children }) {
  const alternateLinks = generateAlternateLinks();
  const canonicalUrl = baseUrl; // Ensure canonical is the non-www version
  
  return (
    <html lang="en" className="dark">
      <head>
        {/* Canonical URL - tells Google this is the main version */}
        <link rel="canonical" href={canonicalUrl} />
        
        {/* 80s Rock Style Fonts */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Teko:wght@400;500;600;700&display=swap" rel="stylesheet" />
        
        {/* Google Analytics GA4 */}
        <script
          async
          src="https://www.googletagmanager.com/gtag/js?id=G-92RKGQW8NJ"
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'G-92RKGQW8NJ', {
                page_title: document.title,
                page_location: window.location.href,
              });
            `,
          }}
        />
        
        {/* Hreflang tags for international SEO */}
        {alternateLinks.map((link, index) => (
          <link
            key={index}
            rel={link.rel}
            hrefLang={link.hrefLang}
            href={link.href}
          />
        ))}
        
        {/* Structured Data for Rich Snippets */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebSite",
              "name": "DadRock Tabs",
              "alternateName": ["DadRock Guitar Tabs", "Dad Rock Tabs"],
              "url": baseUrl,
              "description": "Free guitar and bass tabs for classic rock hits. Learn to play Led Zeppelin, AC/DC, Van Halen, and more!",
              "inLanguage": locales,
              "potentialAction": {
                "@type": "SearchAction",
                "target": {
                  "@type": "EntryPoint",
                  "urlTemplate": `${baseUrl}/search?q={search_term_string}`
                },
                "query-input": "required name=search_term_string"
              },
              "publisher": {
                "@type": "Organization",
                "name": "DadRock Tabs",
                "url": baseUrl
              }
            })
          }}
        />
        
        {/* Additional structured data for music education */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "EducationalOrganization",
              "name": "DadRock Tabs",
              "description": "Guitar and bass tablature lessons for classic rock music",
              "url": baseUrl,
              "sameAs": [
                "https://youtube.com/@dadrockytofficial"
              ],
              "teaches": [
                "Guitar",
                "Bass Guitar",
                "Music Theory",
                "Classic Rock"
              ]
            })
          }}
        />
      </head>
      <body className="min-h-screen bg-background antialiased">
        {children}
      </body>
    </html>
  );
}
