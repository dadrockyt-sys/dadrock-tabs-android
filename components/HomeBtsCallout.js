'use client';

import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import Link from 'next/link';
import { Music } from 'lucide-react';
import { usePathname } from 'next/navigation';

const HOME_PATH_PATTERN = /^\/(?:es|pt|pt-br|de|fr|it|ja|ko|zh|ru|hi|sv|fi)?\/?$/;
const PORTAL_ID = 'bts-homepage-callout-portal';

export default function HomeBtsCallout() {
  const pathname = usePathname();
  const [portalNode, setPortalNode] = useState(null);

  useEffect(() => {
    if (!HOME_PATH_PATTERN.test(pathname || '/')) {
      setPortalNode(null);
      return undefined;
    }

    let active = true;
    let observer;
    let fallbackTimer;

    const placeCallout = () => {
      const searchBorder = document.querySelector('.gradient-border');
      const searchForm = searchBorder?.closest('form');

      if (!searchForm?.parentNode) return false;

      let node = document.getElementById(PORTAL_ID);
      if (!node) {
        node = document.createElement('div');
        node.id = PORTAL_ID;
        node.className = 'w-full max-w-2xl';
      }

      if (node.parentNode !== searchForm.parentNode || node.nextSibling !== searchForm) {
        searchForm.parentNode.insertBefore(node, searchForm);
      }

      if (active) setPortalNode(node);
      return true;
    };

    if (!placeCallout()) {
      observer = new MutationObserver(() => {
        if (placeCallout()) observer?.disconnect();
      });
      observer.observe(document.body, { childList: true, subtree: true });
      fallbackTimer = window.setTimeout(() => {
        observer?.disconnect();
        placeCallout();
      }, 3000);
    }

    return () => {
      active = false;
      observer?.disconnect();
      if (fallbackTimer) window.clearTimeout(fallbackTimer);

      const node = document.getElementById(PORTAL_ID);
      if (node) node.remove();
      setPortalNode(null);
    };
  }, [pathname]);

  if (!portalNode) return null;

  return createPortal(
    <Link
      href="/bts"
      aria-label="Open Backing Track Studio"
      className="group relative mb-5 flex w-full items-center gap-3 overflow-hidden rounded-full border-2 border-amber-400/90 bg-gradient-to-r from-zinc-950 via-orange-950 to-zinc-950 px-4 py-3.5 shadow-[0_0_30px_rgba(245,158,11,0.38)] transition-all duration-300 hover:scale-[1.015] hover:border-amber-300 hover:shadow-[0_0_44px_rgba(245,158,11,0.58)] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-amber-400/60 sm:gap-4 sm:px-5 sm:py-4"
    >
      <span className="relative z-10 flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-red-600 text-[11px] font-black tracking-wide text-white shadow-[0_0_18px_rgba(220,38,38,0.9)] ring-2 ring-red-300/70 sm:h-12 sm:w-12 sm:text-xs">
        NEW
      </span>

      <span className="relative z-10 flex-1 text-center text-lg font-black uppercase tracking-wider text-white transition-colors group-hover:text-amber-200 sm:text-xl">
        Backing Track Studio
      </span>

      <Music className="relative z-10 h-6 w-6 shrink-0 text-amber-400 transition-transform duration-300 group-hover:scale-110 sm:h-7 sm:w-7" />

      <span className="pointer-events-none absolute inset-0 bg-gradient-to-r from-red-600/10 via-amber-400/10 to-orange-500/10 opacity-70 transition-opacity group-hover:opacity-100" />
    </Link>,
    portalNode
  );
}
