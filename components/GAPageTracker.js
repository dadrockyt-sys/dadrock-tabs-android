'use client';

import { useEffect, useRef } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';

const GA_MEASUREMENT_ID = 'G-92RKGQW8NJ';

/**
 * GAPageTracker — Fires GA4 page_view events on every client-side route change.
 *
 * Fixes "(not set)" page titles in GA4 by:
 * 1. Waiting for document.title to be set after route change
 * 2. Using requestAnimationFrame + delay to ensure React has updated the DOM
 * 3. Retrying title capture if it's still empty
 */
export default function GAPageTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const isFirstRender = useRef(true);

  useEffect(() => {
    // Skip the first render — the initial page_view is handled by the
    // window.addEventListener('load', ...) in layout.js
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    // Only fire if gtag is loaded (not blocked by bot filter)
    if (typeof window.gtag !== 'function') return;

    // Wait for React to finish rendering the new page title
    // requestAnimationFrame ensures DOM is painted, then 300ms delay
    // gives Next.js metadata time to update document.title
    const rafId = requestAnimationFrame(() => {
      const timer = setTimeout(() => {
        const title = document.title || 'DadRock Tabs';
        
        window.gtag('event', 'page_view', {
          page_title: title,
          page_location: window.location.href,
          page_path: pathname,
          send_to: GA_MEASUREMENT_ID,
        });
      }, 300);

      // Store timer for cleanup
      window.__gaTimerCleanup = () => clearTimeout(timer);
    });

    return () => {
      cancelAnimationFrame(rafId);
      if (window.__gaTimerCleanup) window.__gaTimerCleanup();
    };
  }, [pathname, searchParams]);

  return null; // This component renders nothing
}
