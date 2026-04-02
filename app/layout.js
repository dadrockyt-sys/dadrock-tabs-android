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
  alternates: {
    canonical: baseUrl,
    languages: Object.fromEntries(
      locales.map(lang => [lang, lang === 'en' ? baseUrl : `${baseUrl}/${lang}`])
    ),
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

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <head>
        {/* 
          IMPORTANT: Do NOT add <link rel="canonical"> or hreflang tags here.
          Each page's generateMetadata() handles its own canonical and hreflang 
          to avoid duplicate/conflicting tags that cause GSC errors.
        */}
        
        {/* 80s Rock Style Fonts */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Teko:wght@400;500;600;700&display=swap" rel="stylesheet" />
        
        {/* Google Analytics GA4 + Firebase Analytics */}
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
