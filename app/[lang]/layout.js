// Locale-prefixed subpages are visitor-facing translations, not independent
// search landing pages. Default the entire locale subtree to noindex while
// allowing crawling/following so Google can see each page's English canonical.
//
// app/[lang]/page.js explicitly overrides this for locale homepages, which are
// intentionally indexable and self-canonical with hreflang alternates.
export const metadata = {
  robots: {
    index: false,
    follow: true,
    googleBot: {
      index: false,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function LocaleLayout({ children }) {
  return children;
}
