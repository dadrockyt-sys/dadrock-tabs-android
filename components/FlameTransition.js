'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { usePathname } from 'next/navigation';

// Number of flame columns for the fire curtain effect
const FLAME_COLUMNS = 12;

export default function FlameTransition() {
  const pathname = usePathname();
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [phase, setPhase] = useState('idle'); // 'idle' | 'burn-in' | 'hold' | 'burn-out'
  const prevPathRef = useRef(pathname);
  const timeoutRef = useRef(null);

  // Detect route changes
  useEffect(() => {
    if (pathname !== prevPathRef.current) {
      // Route changed — start burn-out (reveal) phase
      setPhase('burn-out');
      timeoutRef.current = setTimeout(() => {
        setIsTransitioning(false);
        setPhase('idle');
      }, 600);
      prevPathRef.current = pathname;
    }
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [pathname]);

  // Intercept link clicks to trigger the burn-in animation
  useEffect(() => {
    function handleClick(e) {
      // Find the closest anchor tag
      const anchor = e.target.closest('a');
      if (!anchor) return;

      const href = anchor.getAttribute('href');
      if (!href) return;

      // Skip external links, hash links, and special protocols
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

      // Skip if it's the same page
      if (href === pathname) return;

      // Skip API routes
      if (href.startsWith('/api/')) return;

      // Trigger burn-in animation
      setIsTransitioning(true);
      setPhase('burn-in');
    }

    document.addEventListener('click', handleClick, true);
    return () => document.removeEventListener('click', handleClick, true);
  }, [pathname]);

  if (!isTransitioning && phase === 'idle') return null;

  return (
    <div
      className={`flame-transition-overlay ${phase}`}
      aria-hidden="true"
    >
      {/* Fire curtain — individual flame columns that rise/fall at staggered times */}
      <div className="flame-curtain">
        {Array.from({ length: FLAME_COLUMNS }).map((_, i) => (
          <div
            key={i}
            className={`flame-column flame-col-${i}`}
            style={{
              left: `${(i / FLAME_COLUMNS) * 100}%`,
              width: `${(100 / FLAME_COLUMNS) + 1}%`,
              animationDelay: `${
                phase === 'burn-in'
                  ? Math.random() * 0.15
                  : Math.random() * 0.15
              }s`,
            }}
          />
        ))}
      </div>

      {/* Central ember burst */}
      <div className="flame-center-burst" />

      {/* Smoke wisps at the top */}
      <div className="flame-smoke" />
    </div>
  );
}
