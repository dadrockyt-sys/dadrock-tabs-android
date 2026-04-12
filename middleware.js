import { NextResponse } from 'next/server';

// Supported locales — must match lib/i18n.js and sitemap.js
const locales = ['en', 'es', 'pt', 'pt-br', 'de', 'fr', 'it', 'ja', 'ko', 'zh', 'ru', 'hi', 'sv', 'fi'];

// ─── Bot & Scanner User-Agent Patterns ───
// These are vulnerability scanners, not legitimate crawlers
const BLOCKED_UA_PATTERNS = [
  // Vulnerability scanners
  'sqlmap', 'nikto', 'nmap', 'masscan', 'zgrab', 'gobuster', 'dirbuster',
  'wpscan', 'joomscan', 'droopescan', 'nuclei', 'httpx', 'subfinder',
  'acunetix', 'netsparker', 'burpsuite', 'owasp', 'openvas', 'nessus',
  'qualys', 'nexpose', 'arachni', 'w3af', 'skipfish', 'wapiti',
  // Scraper/spam bots
  'semrush', 'ahref', 'mj12bot', 'dotbot', 'blexbot', 'seekport',
  'megaindex', 'ltx71', 'sogou', 'yandexbot',
  // Generic attack tools
  'python-requests', 'python-urllib', 'curl/', 'wget/', 'go-http-client',
  'java/', 'libwww-perl', 'mechanize', 'scrapy', 'httpclient',
  // Headless browsers used for scanning (not normal browsing)
  'phantom', 'headlesschrome',
];

// ─── Honeypot / Attack Paths ───
// Paths that vulnerability scanners commonly probe
const BLOCKED_PATH_PATTERNS = [
  // WordPress
  '/wp-admin', '/wp-login', '/wp-content', '/wp-includes', '/wp-json',
  '/xmlrpc.php', '/wp-cron', '/wp-config',
  // PHP admin panels
  '/phpmyadmin', '/pma', '/myadmin', '/mysql', '/dbadmin', '/phpinfo',
  '/adminer', '/sqlmanager',
  // Config/env files
  '/.env', '/.git', '/.svn', '/.htaccess', '/.htpasswd', '/.DS_Store',
  '/config.php', '/configuration.php', '/config.yml', '/config.json',
  '/backup', '/database', '/dump', '/sql',
  // CMS exploits
  '/joomla', '/drupal', '/magento', '/typo3', '/modx',
  '/administrator', '/user/login', '/admin.php',
  // Shell/backdoor probes
  '/shell', '/cmd', '/command', '/exec', '/eval',
  '/c99', '/r57', '/wso', '/alfa', '/webshell', '/backdoor',
  // Common scanner paths
  '/cgi-bin', '/scripts', '/fckeditor', '/kcfinder',
  '/elfinder', '/fileman', '/filemanager',
  '/console', '/debug', '/trace', '/actuator',
  '/_profiler', '/_debug', '/telescope',
  // Misc attack vectors
  '/etc/passwd', '/proc/self', '/../../',
  '/vendor', '/node_modules', '/composer',
];

// ─── Blocked File Extensions (in URL path) ───
const BLOCKED_EXTENSIONS = [
  '.php', '.asp', '.aspx', '.jsp', '.cgi', '.pl',
  '.sql', '.bak', '.old', '.orig', '.save', '.swp',
  '.log', '.ini', '.conf', '.cfg',
];

function isBlockedBot(userAgent) {
  if (!userAgent) return true; // No UA = suspicious
  const ua = userAgent.toLowerCase();
  return BLOCKED_UA_PATTERNS.some(pattern => ua.includes(pattern));
}

function isBlockedPath(pathname) {
  const lower = pathname.toLowerCase();
  
  // Check exact path prefix matches
  if (BLOCKED_PATH_PATTERNS.some(p => lower.startsWith(p))) return true;
  
  // Check blocked file extensions
  if (BLOCKED_EXTENSIONS.some(ext => lower.endsWith(ext))) return true;
  
  // Check for directory traversal attempts
  if (lower.includes('..') || lower.includes('%2e%2e')) return true;
  
  // Check for null byte injection
  if (lower.includes('%00') || lower.includes('\x00')) return true;
  
  return false;
}

// Security headers applied to all responses
function addSecurityHeaders(response) {
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'SAMEORIGIN');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), interest-cohort=()');
  response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  return response;
}

export function middleware(request) {
  const url = request.nextUrl.clone();
  const hostname = request.headers.get('host') || '';
  const pathname = request.nextUrl.pathname;
  const userAgent = request.headers.get('user-agent') || '';
  
  // ─── 1. Redirect www to non-www ───
  // Also apply path-level redirects in the same hop to avoid redirect chains
  // (e.g., www.site.com/en/ → site.com/ in one redirect, not three)
  if (hostname.startsWith('www.')) {
    const newHostname = hostname.replace('www.', '');
    url.host = newHostname;

    let cleanPath = pathname;

    // Handle trailing slashes in the same hop
    if (cleanPath !== '/' && cleanPath.endsWith('/')) {
      const withoutSlash = cleanPath.slice(0, -1);
      const segment = withoutSlash.slice(1);

      if (segment === 'en') {
        cleanPath = '/';
      } else if (segment === 'zn') {
        cleanPath = '/zh';
      } else if (withoutSlash.match(/^\/sitemap-[a-z]{2}\.xml$/)) {
        cleanPath = '/sitemap.xml';
      } else if (!locales.includes(segment)) {
        // Strip trailing slash for non-locale-root paths
        cleanPath = withoutSlash;
      }
      // locale roots like /fr/ keep trailing slash — served directly after redirect
    }

    // Handle /en → /
    if (cleanPath === '/en') cleanPath = '/';
    // Handle /zn → /zh
    if (cleanPath === '/zn') cleanPath = '/zh';
    else if (cleanPath.startsWith('/zn/')) cleanPath = '/zh' + cleanPath.slice(3);
    // Handle /search → /
    if (cleanPath === '/search') cleanPath = '/';
    // Handle /fr_ → /fr (known typo in GSC)
    if (cleanPath.match(/^\/([a-z]{2})_$/)) {
      const typoLocale = cleanPath.slice(1, 3);
      if (locales.includes(typoLocale)) cleanPath = '/' + typoLocale;
    }
    // Handle sitemap-xx.xml → sitemap.xml
    if (cleanPath.match(/^\/sitemap-[a-z]{2}\.xml$/)) cleanPath = '/sitemap.xml';

    url.pathname = cleanPath;
    return NextResponse.redirect(url, 301);
  }

  // ─── 2. Block known vulnerability scanners ───
  if (isBlockedBot(userAgent)) {
    return new NextResponse('Forbidden', { status: 403 });
  }

  // ─── 3. Block suspicious/attack paths ───
  if (isBlockedPath(pathname)) {
    // Return 403 instead of 404 — tells scanners the server is actively blocking
    return new NextResponse('Forbidden', { status: 403 });
  }

  // ─── 4. Handle trailing slashes ───
  // Eliminate redirect chains by combining trailing slash strip with known redirects
  if (pathname !== '/' && pathname.endsWith('/')) {
    const withoutSlash = pathname.slice(0, -1);
    const segment = withoutSlash.slice(1); // e.g., '/zh/' → 'zh'

    // /en/ → / directly (English is default locale, single-hop redirect)
    if (segment === 'en') {
      return NextResponse.redirect(new URL('/', request.url), 301);
    }

    // /zn/ → /zh directly (typo fix + trailing slash in one hop)
    if (segment === 'zn') {
      return NextResponse.redirect(new URL('/zh', request.url), 301);
    }

    // /sitemap-xx.xml/ → /sitemap.xml directly (skip intermediate step)
    if (withoutSlash.match(/^\/sitemap-[a-z]{2}\.xml$/)) {
      return NextResponse.redirect(new URL('/sitemap.xml', request.url), 301);
    }

    // Locale roots (/zh/, /fr/) → serve directly without redirect
    if (locales.includes(segment)) {
      // Fall through to locale handling below
    } else {
      // All other trailing slashes → redirect to clean URL
      const cleanUrl = new URL(withoutSlash, request.url);
      cleanUrl.search = request.nextUrl.search;
      return NextResponse.redirect(cleanUrl, 301);
    }
  }

  // ─── 4b. Strip trailing dashes from artist/song slugs ───
  // GSC indexes URLs like /artist/rush- which don't match our slug format
  const trailingDashMatch = pathname.match(/^\/((?:[a-z]{2}(?:-[a-z]{2})?\/)?(?:artist|songs))\/(.+)-$/);
  if (trailingDashMatch) {
    const prefix = trailingDashMatch[1];
    const cleanSlug = trailingDashMatch[2];
    const cleanUrl = new URL(`/${prefix}/${cleanSlug}`, request.url);
    cleanUrl.search = request.nextUrl.search;
    return NextResponse.redirect(cleanUrl, 301);
  }

  // ─── 4c. Redirect known missing songs to their artist pages ───
  // These songs were indexed by GSC but don't exist in the database
  const missingSongRedirects = {
    'pantera-walk': 'pantera',
    'dokken-tooth-and-nail': 'dokken',
  };
  const songSlugMatch = pathname.match(/^(?:\/[a-z]{2}(?:-[a-z]{2})?)?\/songs\/(.+)$/);
  if (songSlugMatch) {
    const songSlug = songSlugMatch[1];
    const artistSlug = missingSongRedirects[songSlug];
    if (artistSlug) {
      // Extract locale prefix if present
      const localePrefix = pathname.match(/^(\/[a-z]{2}(?:-[a-z]{2})?)\/songs\//);
      const prefix = localePrefix ? localePrefix[1] : '';
      return NextResponse.redirect(new URL(`${prefix}/artist/${artistSlug}`, request.url), 301);
    }
  }

  // ─── 5. Handle /en → redirect to / (English is the default locale) ───
  if (pathname === '/en') {
    return NextResponse.redirect(new URL('/', request.url), 301);
  }

  // ─── 6. Handle /zn → redirect to /zh (common typo) ───
  if (pathname === '/zn') {
    return NextResponse.redirect(new URL('/zh', request.url), 301);
  }
  if (pathname.startsWith('/zn/')) {
    const subpath = pathname.slice(3); // '/zn/quickies' → '/quickies'
    return NextResponse.redirect(new URL(`/zh${subpath}`, request.url), 301);
  }

  // ─── 7. Handle /search → redirect to homepage (no search page exists) ───
  if (pathname === '/search') {
    return NextResponse.redirect(new URL('/', request.url), 301);
  }

  // ─── 7b. Handle locale typos like /fr_ → /fr ───
  const localeTypoMatch = pathname.match(/^\/([a-z]{2})_$/);
  if (localeTypoMatch && locales.includes(localeTypoMatch[1])) {
    return NextResponse.redirect(new URL(`/${localeTypoMatch[1]}`, request.url), 301);
  }

  // ─── 8. Handle non-existent sitemap files ───
  if (pathname.match(/^\/sitemap-[a-z]{2}\.xml$/)) {
    // Redirect to the real sitemap
    return NextResponse.redirect(new URL('/sitemap.xml', request.url), 301);
  }

  // ─── 8. Locale handling (i18n URL rewriting) ───
  let matchedLocale = null;
  let restPath = null;

  // Check for 'pt-br' first since it contains a hyphen
  if (pathname.startsWith('/pt-br/') || pathname === '/pt-br') {
    matchedLocale = 'pt-br';
    restPath = pathname === '/pt-br' ? '' : pathname.slice('/pt-br'.length);
  } else {
    // Check other single-segment locales
    for (const locale of locales) {
      if (locale === 'pt-br') continue;
      if (pathname.startsWith(`/${locale}/`)) {
        matchedLocale = locale;
        restPath = pathname.slice(`/${locale}`.length);
        break;
      }
      if (pathname === `/${locale}`) {
        matchedLocale = locale;
        restPath = '';
        break;
      }
    }
  }

  // If no locale matched, add security headers and continue
  if (!matchedLocale) {
    const response = NextResponse.next();
    return addSecurityHeaders(response);
  }

  // If it's just the locale root, let [lang]/page.js handle it
  if (!restPath || restPath === '' || restPath === '/') {
    const response = NextResponse.next();
    return addSecurityHeaders(response);
  }

  // For subpaths like /es/artist/acdc, rewrite to /artist/acdc
  const rewriteUrl = new URL(restPath, request.url);
  const response = NextResponse.rewrite(rewriteUrl);
  response.headers.set('x-locale', matchedLocale);
  return addSecurityHeaders(response);
}

export const config = {
  matcher: [
    // Match all paths except Next.js internals and actual static files
    '/((?!_next/static|_next/image|favicon.ico|api).*)',
  ],
};
