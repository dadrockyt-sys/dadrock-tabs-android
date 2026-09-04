const pdfRuntimeTraceExcludes = [
  './public/**/*',
];

const pdfRuntimeTraceIncludes = [
  './public/DadRock-Tabs-Logo.png',
];

const nextConfig = {
  images: {
    unoptimized: true,
  },
  // The Product/PDF serverless functions read only the DadRock logo from
  // public/. Keep the rest of the static/research tree out of these function
  // bundles; public assets remain deployed normally for the website itself.
  // /api/pdf-preview is intentionally excluded because its proof path reads
  // a gomyway notation fixture from public/.
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
