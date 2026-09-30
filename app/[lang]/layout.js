// Most locale-prefixed subpages are visitor-facing translations, not independent
// search landing pages. Default the locale subtree to noindex while allowing
// crawling/following so Google can see each page's English canonical.
//
// Exceptions explicitly override this metadata:
// - app/[lang]/page.js: localized homepages
// - app/[lang]/learn/[slug]/page.js via the shared guide metadata: localized
//   Learn guides, which are indexable and use self-canonicals + hreflang
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
