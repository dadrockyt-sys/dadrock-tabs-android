const pdfRuntimeTraceExcludes = [
  './public/*gomyway*',
  './public/*GOMYWAY*',
  './public/DadRock TABS - gomyway*',
  './public/Stairway to Heaven AI test.m4a',
];

const pdfRuntimeTraceIncludes = [
  './public/DadRock-Tabs-Logo.png',
];

const nextConfig = {
  images: {
    unoptimized: true,
  },
  // Keep branch-only research/test artifacts out of the two real Product/PDF
  // serverless traces. Both renderers need only the DadRock logo from public/.
  // /api/pdf-preview is intentionally excluded from this rule because its
  // development proof path legitimately reads a gomyway notation fixture.
  outputFileTracingExcludes: {
    '/api/generate-tab-pdf': pdfRuntimeTraceExcludes,
    '/api/generate-tab-preview': pdfRuntimeTraceExcludes,
  },
  outputFileTracingIncludes: {
    '/api/generate-tab-pdf': pdfRuntimeTraceIncludes,
    '/api/generate-tab-preview': pdfRuntimeTraceIncludes,
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
