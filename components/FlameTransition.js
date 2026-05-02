'use client';

import { useEffect, useState, useRef } from 'react';
import { usePathname, useRouter } from 'next/navigation';

const FLAME_COLUMNS = 14;
const BURN_IN_DURATION = 800; // ms — how long the flames take to cover the screen
const HOLD_DURATION = 200;   // ms — brief hold at full coverage before navigating

export default function FlameTransition() {
  const pathname = usePathname();
  const router = useRouter();
  const [phase, setPhase] = useState('idle'); // 'idle' | 'burn-in' | 'burn-out'
  const prevPathRef = useRef(pathname);
  const pendingHref = useRef(null);
  const timeoutRef = useRef(null);

  // When pathname changes (new page loaded), play burn-out
  useEffect(() => {
    if (pathname !== prevPathRef.current) {
      prevPathRef.current = pathname;
      // New page has loaded — reveal it with burn-out
      setPhase('burn-out');
      timeoutRef.current = setTimeout(() => {
        setPhase('idle');
      }, 900);
    }
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [pathname]);

  // Intercept ALL internal link clicks
  useEffect(() => {
    function handleClick(e) {
      // Don't intercept if already transitioning
      if (phase !== 'idle') return;

      const anchor = e.target.closest('a');
      if (!anchor) return;

      const href = anchor.getAttribute('href');
      if (!href) return;

      // Skip external links, special protocols, new tabs, downloads
      if (
        href.startsWith('http') ||
        href.startsWith('mailto:') ||
        href.startsWith('tel:') ||
        href.startsWith('#') ||
        anchor.target === '_blank' ||
        anchor.hasAttribute('download')
      ) {
        return;
      }

      // Skip same page
      if (href === pathname) return;

      // Skip API routes
      if (href.startsWith('/api/')) return;

      // PREVENT the default navigation
      e.preventDefault();
      e.stopPropagation();

      // Store the destination
      pendingHref.current = href;

      // Start burn-in (flames cover the screen)
      setPhase('burn-in');

      // After flames fully cover, navigate to the new page
      timeoutRef.current = setTimeout(() => {
        router.push(pendingHref.current);
        pendingHref.current = null;
      }, BURN_IN_DURATION + HOLD_DURATION);
    }

    document.addEventListener('click', handleClick, true);
    return () => document.removeEventListener('click', handleClick, true);
  }, [pathname, phase, router]);

  // Also handle programmatic navigation (like the Random Song button)
  useEffect(() => {
    // Override window.location assignments for internal navigation
    const originalAssign = window.location.assign;
    const originalHref = Object.getOwnPropertyDescriptor(window.location, 'href');

    // Patch fetch-then-navigate pattern (Random Song button uses window.location.href)
    // We'll add a global helper
    window.__flameNavigate = (href) => {
      if (phase !== 'idle') {
        router.push(href);
        return;
      }
      pendingHref.current = href;
      setPhase('burn-in');
      setTimeout(() => {
        router.push(href);
        pendingHref.current = null;
      }, BURN_IN_DURATION + HOLD_DURATION);
    };

    return () => {
      delete window.__flameNavigate;
    };
  }, [phase, router]);

  if (phase === 'idle') return null;

  return (
    <div className={`flame-overlay ${phase}`} aria-hidden="true">
      {/* Fire columns */}
      <div className="flame-curtain">
        {Array.from({ length: FLAME_COLUMNS }).map((_, i) => (
          <div
            key={i}
            className={`flame-col flame-col-${i % 12}`}
            style={{
              left: `${(i / FLAME_COLUMNS) * 100}%`,
              width: `${(100 / FLAME_COLUMNS) + 0.5}%`,
            }}
          />
        ))}
      </div>

      {/* Hot white center flash */}
      <div className="flame-flash" />

      {/* Top smoke */}
      <div className="flame-smoke-top" />
    </div>
  );
}
