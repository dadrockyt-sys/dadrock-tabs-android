import './globals.css';
import { Suspense } from 'react';
import { locales } from '@/lib/i18n';
import GAPageTracker from '@/components/GAPageTracker';

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
        
        {/* Google Analytics GA4 + Firebase Analytics — with bot filtering */}
        <script
          async
          src="https://www.googletagmanager.com/gtag/js?id=G-92RKGQW8NJ"
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Bot detection — skip GA tracking for known bots/scanners
              (function() {
                var ua = (navigator.userAgent || '').toLowerCase();
                var botPatterns = [
                  'bot', 'crawl', 'spider', 'slurp', 'mediapartners',
                  'semrush', 'ahref', 'mj12bot', 'dotbot', 'blexbot',
                  'python', 'curl', 'wget', 'java', 'perl', 'scrapy',
                  'phantom', 'headless', 'sqlmap', 'nikto', 'nmap',
                  'zgrab', 'masscan', 'gobuster', 'nuclei', 'httpx',
                  'bytespider', 'yandex', 'sogou', 'baidu',
                  'ltx71', 'megaindex', 'seekport'
                ];
                var isBot = botPatterns.some(function(p) { return ua.indexOf(p) !== -1; });
                
                if (!isBot) {
                  window.dataLayer = window.dataLayer || [];
                  function gtag(){dataLayer.push(arguments);}
                  window.gtag = gtag;
                  gtag('js', new Date());

                  // IMPORTANT: Delay config until Window Loaded so document.title is ready
                  // This prevents "(not set)" page titles in GA4
                  gtag('config', 'G-92RKGQW8NJ', {
                    send_page_view: false,  // We fire it manually after window load
                  });

                  function fireInitialPageView() {
                    var title = document.title || 'DadRock Tabs';
                    gtag('event', 'page_view', {
                      page_title: title,
                      page_location: window.location.href,
                      page_path: window.location.pathname,
                      send_to: 'G-92RKGQW8NJ',
                    });
                  }

                  // Use Window Loaded to ensure title is set
                  if (document.readyState === 'complete') {
                    fireInitialPageView();
                  } else {
                    window.addEventListener('load', fireInitialPageView);
                  }
                }
              })();
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
        <Suspense fallback={null}>
          <GAPageTracker />
        </Suspense>
        {children}
      </body>
    </html>
  );
}
