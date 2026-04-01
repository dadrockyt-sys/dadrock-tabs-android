import { NextResponse } from 'next/server';

// Supported locales — must match lib/i18n.js and sitemap.js
const locales = ['en', 'es', 'pt', 'pt-br', 'de', 'fr', 'it', 'ja', 'ko', 'zh', 'ru', 'hi', 'sv', 'fi'];

export function middleware(request) {
  const url = request.nextUrl.clone();
  const hostname = request.headers.get('host') || '';
  
  // Redirect www to non-www
  if (hostname.startsWith('www.')) {
    const newHostname = hostname.replace('www.', '');
    url.host = newHostname;
    return NextResponse.redirect(url, 301);
  }

  const pathname = request.nextUrl.pathname;

  // Check if the path starts with a locale prefix
  // Handle 'pt-br' first (longer match), then single-segment locales
  let matchedLocale = null;
  let restPath = null;

  // Check for 'pt-br' first since it contains a hyphen
  if (pathname.startsWith('/pt-br/') || pathname === '/pt-br') {
    matchedLocale = 'pt-br';
    restPath = pathname === '/pt-br' ? '' : pathname.slice('/pt-br'.length);
  } else {
    // Check other single-segment locales
    for (const locale of locales) {
      if (locale === 'pt-br') continue; // Already handled above
      if (pathname.startsWith(`/${locale}/`)) {
        matchedLocale = locale;
        restPath = pathname.slice(`/${locale}`.length);
        break;
      }
      // Exact match for locale root (e.g., /es, /fr) — handled by [lang]/page.js
      if (pathname === `/${locale}`) {
        matchedLocale = locale;
        restPath = '';
        break;
      }
    }
  }

  // If no locale matched, continue normally
  if (!matchedLocale) {
    return NextResponse.next();
  }

  // If it's just the locale root (e.g., /es, /fr, /pt-br with no subpath),
  // let the existing [lang]/page.js handle it
  if (!restPath || restPath === '' || restPath === '/') {
    return NextResponse.next();
  }

  // For subpaths like /es/artist/acdc, /pt/quickies, /ko/top-lessons, etc.
  // Rewrite to the actual path (strip the locale prefix)
  const rewriteUrl = new URL(restPath, request.url);
  const response = NextResponse.rewrite(rewriteUrl);
  
  // Pass the locale as a header so pages can optionally read it server-side
  response.headers.set('x-locale', matchedLocale);
  
  return response;
}

export const config = {
  matcher: [
    // Match all paths except static files, api routes, and Next.js internals
    '/((?!_next/static|_next/image|favicon.ico|.*\\..*|api).*)',
  ],
};
