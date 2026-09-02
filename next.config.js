const artistSlugRedirects = {
  'ac-dc': 'acdc',
  'alive-in-chains': 'alice-in-chains',
  'gearge-thorogood': 'george-thorogood',
  'kimg-diamond': 'king-diamond',
  'telsa': 'tesla',
  'the-poilice': 'the-police',
  'xyx': 'xyz',
  'steve-ray-vaughan': 'stevie-ray-vaughan',
  'red-hot-chilli-peppers': 'red-hot-chili-peppers',
  'the-red-hot-chili-peppers': 'red-hot-chili-peppers',
};

const translatedLocales = [
  'es', 'pt', 'pt-br', 'de', 'fr', 'it', 'ja',
  'ko', 'zh', 'ru', 'hi', 'sv', 'fi',
];

const nextConfig = {
  images: {
    unoptimized: true,
  },
  // Skip Next.js automatic trailing slash redirect (308) so our middleware handles it with 301
  skipTrailingSlashRedirect: true,
  // Add empty turbopack config to silence the warning in Next.js 16
  turbopack: {},
  webpack(config, { dev }) {
    if (dev) {
      // Reduce CPU/memory from file watching
      config.watchOptions = {
        poll: 2000, // check every 2 seconds
        aggregateTimeout: 300, // wait before rebuilding
        ignored: ['**/node_modules'],
      };
    }
    return config;
  },
  onDemandEntries: {
    maxInactiveAge: 10000,
    pagesBufferLength: 2,
  },
  async redirects() {
    const redirects = [];

    // Historical database typos and aliases have been seen by Google. Keep
    // one permanent URL for each artist so those old crawl targets cannot
    // continue generating duplicate-canonical noise.
    for (const [oldSlug, canonicalSlug] of Object.entries(artistSlugRedirects)) {
      redirects.push({
        source: `/artist/${oldSlug}`,
        destination: `/artist/${canonicalSlug}`,
        permanent: true,
      });

      // /en is never a canonical prefix on this site.
      redirects.push({
        source: `/en/artist/${oldSlug}`,
        destination: `/artist/${canonicalSlug}`,
        permanent: true,
      });

      for (const locale of translatedLocales) {
        redirects.push({
          source: `/${locale}/artist/${oldSlug}`,
          destination: `/${locale}/artist/${canonicalSlug}`,
          permanent: true,
        });
      }
    }

    return redirects;
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          // Allow embedding (needed for preview)
          { key: "X-Frame-Options", value: "ALLOWALL" },
          { key: "Content-Security-Policy", value: "frame-ancestors *;" },
          // CORS
          { key: "Access-Control-Allow-Origin", value: process.env.CORS_ORIGINS || "*" },
          { key: "Access-Control-Allow-Methods", value: "GET, POST, PUT, DELETE, OPTIONS" },
          { key: "Access-Control-Allow-Headers", value: "*" },
          // Security headers
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-XSS-Protection", value: "1; mode=block" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), interest-cohort=()" },
          { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" },
          // Prevent MIME sniffing and clickjacking from non-trusted origins
          { key: "X-Permitted-Cross-Domain-Policies", value: "none" },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
