'use client';

import { useEffect, useRef } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';

const GA_MEASUREMENT_ID = 'G-92RKGQW8NJ';

/**
 * GAPageTracker — Fires GA4 page_view events on every client-side route change.
 *
 * Problem: In SPAs like Next.js, client-side navigation (via <Link>) does NOT trigger
 * a full page reload, so GA4 never fires a new page_view. This results in "(not set)"
 * page paths in Google Analytics reports.
 *
 * Solution: Listen for pathname changes via usePathname() and manually fire
 * gtag('event', 'page_view', ...) with the correct page_path and page_location.
 */
export default function GAPageTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const isFirstRender = useRef(true);

  useEffect(() => {
    // Skip the first render — the initial page_view is already handled by the
    // gtag('config', ...) call in layout.js
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    // Only fire if gtag is loaded (not blocked by bot filter)
    if (typeof window.gtag !== 'function') return;

    // Build the full URL with search params
    const url = searchParams?.toString()
      ? `${pathname}?${searchParams.toString()}`
      : pathname;

    // Small delay to ensure document.title has updated after route change
    const timer = setTimeout(() => {
      window.gtag('event', 'page_view', {
        page_title: document.title,
        page_location: window.location.href,
        page_path: pathname,
        send_to: GA_MEASUREMENT_ID,
      });
    }, 100);

    return () => clearTimeout(timer);
  }, [pathname, searchParams]);

  return null; // This component renders nothing
}
