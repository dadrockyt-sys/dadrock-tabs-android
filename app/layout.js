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
        
        {/* Google Analytics GA4 — with bot filtering & "(not set)" prevention */}
        <script
          async
          src="https://www.googletagmanager.com/gtag/js?id=G-92RKGQW8NJ"
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `
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
                if (isBot) return;

                // Detect Android WebView — Firebase SDK handles tracking natively
                // The Android app sends screen_view events via Firebase Analytics,
                // so we skip web gtag to prevent double-tracking and "(not set)" titles.
                var isAndroidWebView = (
                  (ua.indexOf('wv') !== -1 && ua.indexOf('android') !== -1) ||
                  (window.navigator.userAgent.indexOf('; wv)') !== -1)
                );
                if (isAndroidWebView) {
                  // Still define gtag so the GAPageTracker component doesn't error,
                  // but make it a no-op
                  window.dataLayer = window.dataLayer || [];
                  window.gtag = function() {};
                  return;
                }

                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                window.gtag = gtag;
                gtag('js', new Date());

                function getTitle() {
                  return document.title || document.querySelector('title')?.textContent || 'DadRock Tabs';
                }

                // Set persistent defaults immediately
                gtag('set', {
                  page_title: getTitle(),
                  page_location: window.location.href,
                  page_path: window.location.pathname,
                });

                // Config with auto page_view OFF
                gtag('config', 'G-92RKGQW8NJ', { send_page_view: false });

                // Fire manual page_view on window load (title guaranteed set)
                function firePageView() {
                  var title = getTitle();
                  gtag('set', { page_title: title });
                  gtag('event', 'page_view', {
                    page_title: title,
                    page_location: window.location.href,
                    page_path: window.location.pathname,
                    send_to: 'G-92RKGQW8NJ',
                  });
                }

                if (document.readyState === 'complete') {
                  firePageView();
                } else {
                  window.addEventListener('load', firePageView);
                }

                // --- FIX FOR ENHANCED MEASUREMENT "(not set)" ---
                // GA4 Enhanced Measurement listens for history.pushState/replaceState
                // and auto-fires page_view BEFORE Next.js updates document.title.
                // We intercept these calls to update GA defaults AFTER the title changes.
                var origPushState = history.pushState;
                var origReplaceState = history.replaceState;

                function patchHistoryMethod(original) {
                  return function() {
                    var result = original.apply(this, arguments);
                    // After Next.js pushes the new URL, wait for title to update
                    // then set GA defaults so Enhanced Measurement picks up correct title
                    setTimeout(function() {
                      var title = getTitle();
                      if (typeof window.gtag === 'function') {
                        window.gtag('set', {
                          page_title: title,
                          page_location: window.location.href,
                          page_path: window.location.pathname,
                        });
                      }
                    }, 0);
                    // Also check again after React renders
                    setTimeout(function() {
                      var title = getTitle();
                      if (typeof window.gtag === 'function') {
                        window.gtag('set', {
                          page_title: title,
                          page_location: window.location.href,
                          page_path: window.location.pathname,
                        });
                      }
                    }, 300);
                    return result;
                  };
                }

                history.pushState = patchHistoryMethod(origPushState);
                history.replaceState = patchHistoryMethod(origReplaceState);

                // Watch for title element changes (React hydration, metadata updates)
                if (typeof MutationObserver !== 'undefined') {
                  var observer = new MutationObserver(function() {
                    var newTitle = document.title;
                    if (newTitle && typeof window.gtag === 'function') {
                      window.gtag('set', { page_title: newTitle });
                    }
                  });
                  // Observe the head for title changes
                  observer.observe(document.head || document.documentElement, {
                    childList: true, subtree: true, characterData: true,
                  });
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
