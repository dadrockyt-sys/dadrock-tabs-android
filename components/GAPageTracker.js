'use client';

import { useEffect, useRef } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';

const GA_MEASUREMENT_ID = 'G-92RKGQW8NJ';

/**
 * GAPageTracker — Fires GA4 page_view on every client-side route change.
 * Also updates persistent GA defaults (gtag 'set') so Enhanced Measurement
 * auto-events always have the correct page_title and page_path.
 */
export default function GAPageTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const isFirstRender = useRef(true);
  const prevPathRef = useRef(pathname);

  useEffect(() => {
    // Skip first render (handled by layout.js window.load)
    if (isFirstRender.current) {
      isFirstRender.current = false;
      prevPathRef.current = pathname;
      return;
    }

    // Skip if pathname hasn't actually changed
    if (prevPathRef.current === pathname) return;
    prevPathRef.current = pathname;

    if (typeof window.gtag !== 'function') return;

    // Wait for Next.js to finish rendering the new route's title
    // Use requestAnimationFrame + 500ms to be safe
    const rafId = requestAnimationFrame(() => {
      const timer = setTimeout(() => {
        const title = document.title || 'DadRock Tabs';

        // Update persistent defaults FIRST — catches any auto-events too
        window.gtag('set', {
          page_title: title,
          page_location: window.location.href,
          page_path: pathname,
        });

        // Then fire our manual page_view
        window.gtag('event', 'page_view', {
          page_title: title,
          page_location: window.location.href,
          page_path: pathname,
          send_to: GA_MEASUREMENT_ID,
        });
      }, 500);

      window.__gaTimer = timer;
    });

    return () => {
      cancelAnimationFrame(rafId);
      if (window.__gaTimer) clearTimeout(window.__gaTimer);
    };
  }, [pathname, searchParams]);

  return null;
}
