'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { usePathname, useRouter } from 'next/navigation';

// Fire color palette — maps heat intensity (0-36) to RGB (classic doom fire)
const FIRE_PALETTE = [
  [0,0,0],[7,7,7],[31,7,7],[47,15,7],[71,15,7],[87,23,7],[103,31,7],[119,31,7],
  [143,39,7],[159,47,7],[175,63,7],[191,71,7],[199,71,7],[223,79,7],[223,87,7],
  [223,87,7],[215,95,7],[215,103,15],[207,111,15],[207,119,15],[207,127,15],
  [207,135,23],[199,135,23],[199,143,23],[199,151,31],[191,159,31],[191,159,31],
  [191,167,39],[191,167,39],[191,175,47],[183,175,47],[183,183,47],[183,183,55],
  [207,207,111],[223,223,159],[239,239,199],[255,255,255]
];

const PIXEL_SIZE = 4;         // Each "fire pixel" is 4x4 real pixels
const BURN_IN_TIME = 900;     // ms for fire to cover screen
const HOLD_TIME = 150;        // ms to hold at full coverage
const BURN_OUT_TIME = 800;    // ms for fire to fade away

export default function FlameTransition() {
  const pathname = usePathname();
  const router = useRouter();
  const [phase, setPhase] = useState('idle');
  const prevPathRef = useRef(pathname);
  const pendingHref = useRef(null);
  const canvasRef = useRef(null);
  const fireRef = useRef(null);      // { buffer, width, height }
  const rafRef = useRef(null);
  const phaseRef = useRef('idle');
  const startTimeRef = useRef(0);
  const ctxRef = useRef(null);
  const imageDataRef = useRef(null);
  const canvasSizeRef = useRef({ w: 0, h: 0 });

  // Keep phase ref in sync for the animation loop
  useEffect(() => {
    phaseRef.current = phase;
  }, [phase]);

  // Detect route changes — trigger burn-out (fire dies down naturally)
  useEffect(() => {
    if (pathname !== prevPathRef.current) {
      prevPathRef.current = pathname;
      // Start burn-out from wherever the fire currently is
      phaseRef.current = 'burn-out';
      setPhase('burn-out');
      startTimeRef.current = performance.now();

      // Schedule cleanup after burn-out completes
      const timer = setTimeout(() => {
        setPhase('idle');
        stopAnimation();
        // Clear refs for next transition
        fireRef.current = null;
        ctxRef.current = null;
        imageDataRef.current = null;
      }, BURN_OUT_TIME + 200);

      return () => clearTimeout(timer);
    }
  }, [pathname]);

  // Stop the animation loop
  const stopAnimation = useCallback(() => {
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
  }, []);

  // Initialize or resize the canvas + fire buffer
  const ensureCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return false;

    const width = window.innerWidth;
    const height = window.innerHeight;

    // Only reinitialize if canvas size changed or no buffer exists
    if (canvasSizeRef.current.w !== width || canvasSizeRef.current.h !== height || !fireRef.current) {
      canvas.width = width;
      canvas.height = height;
      canvasSizeRef.current = { w: width, h: height };

      const fw = Math.ceil(width / PIXEL_SIZE);
      const fh = Math.ceil(height / PIXEL_SIZE);
      const buffer = new Uint8Array(fw * fh);
      fireRef.current = { buffer, width: fw, height: fh };

      ctxRef.current = canvas.getContext('2d');
      imageDataRef.current = ctxRef.current.createImageData(width, height);
    }

    return true;
  }, []);

  // The main animation loop — reads phaseRef to decide behavior
  const runAnimation = useCallback(() => {
    if (!ensureCanvas()) return;

    const { buffer, width: fw, height: fh } = fireRef.current;
    const ctx = ctxRef.current;
    const imageData = imageDataRef.current;
    const { w: canvasW, h: canvasH } = canvasSizeRef.current;

    const animate = () => {
      const currentPhase = phaseRef.current;
      if (currentPhase === 'idle') {
        rafRef.current = null;
        return;
      }

      const elapsed = performance.now() - startTimeRef.current;

      if (currentPhase === 'burn-in') {
        // Gradually ignite bottom rows — more as time progresses
        const progress = Math.min(elapsed / BURN_IN_TIME, 1);
        const igniteRows = Math.max(1, Math.floor(progress * 3));
        for (let row = 0; row < igniteRows; row++) {
          const y = fh - 1 - row;
          for (let x = 0; x < fw; x++) {
            buffer[y * fw + x] = 36; // Max heat
          }
        }
        // Add random sparks ahead of the fire front for drama
        if (progress > 0.2) {
          const sparkY = Math.floor(fh * (1 - progress * 0.8));
          const sparkCount = Math.floor(fw * 0.3);
          for (let i = 0; i < sparkCount; i++) {
            const sx = Math.floor(Math.random() * fw);
            const sy = sparkY + Math.floor(Math.random() * 5);
            if (sy >= 0 && sy < fh) {
              buffer[sy * fw + sx] = Math.floor(Math.random() * 20) + 10;
            }
          }
        }
      } else if (currentPhase === 'burn-out') {
        // Gradually reduce the heat source at the bottom
        const progress = Math.min(elapsed / BURN_OUT_TIME, 1);
        // Diminish bottom row heat over time
        const bottomHeat = Math.max(0, Math.floor(36 * (1 - progress * 1.5)));
        for (let x = 0; x < fw; x++) {
          const idx = (fh - 1) * fw + x;
          buffer[idx] = Math.min(buffer[idx], bottomHeat);
        }
        // Actively cool the entire buffer to speed up disappearance
        if (progress > 0.3) {
          const coolStrength = Math.floor((progress - 0.3) * 4);
          for (let i = 0; i < buffer.length; i++) {
            buffer[i] = Math.max(0, buffer[i] - coolStrength);
          }
        }
      }

      // Propagate fire upward (core doom fire algorithm)
      for (let x = 0; x < fw; x++) {
        for (let y = 1; y < fh; y++) {
          const src = y * fw + x;
          const heat = buffer[src];
          if (heat === 0) {
            buffer[(y - 1) * fw + x] = 0;
          } else {
            const randIdx = Math.round(Math.random() * 3);
            const dstX = Math.min(fw - 1, Math.max(0, x - randIdx + 1));
            const dst = (y - 1) * fw + dstX;
            buffer[dst] = Math.max(0, heat - Math.floor(Math.random() * 2));
          }
        }
      }

      // Render fire buffer to canvas pixels
      const pixels = imageData.data;
      for (let y = 0; y < fh; y++) {
        for (let x = 0; x < fw; x++) {
          const heat = buffer[y * fw + x];
          const color = FIRE_PALETTE[Math.min(heat, 36)];

          for (let py = 0; py < PIXEL_SIZE; py++) {
            for (let px = 0; px < PIXEL_SIZE; px++) {
              const realX = x * PIXEL_SIZE + px;
              const realY = y * PIXEL_SIZE + py;
              if (realX < canvasW && realY < canvasH) {
                const idx = (realY * canvasW + realX) * 4;
                pixels[idx] = color[0];
                pixels[idx + 1] = color[1];
                pixels[idx + 2] = color[2];
                pixels[idx + 3] = heat > 0 ? 255 : 0;
              }
            }
          }
        }
      }

      ctx.putImageData(imageData, 0, 0);
      rafRef.current = requestAnimationFrame(animate);
    };

    // Cancel any existing loop before starting new one
    stopAnimation();
    rafRef.current = requestAnimationFrame(animate);
  }, [ensureCanvas, stopAnimation]);

  // Start animation when entering burn-in (fresh fire)
  // For burn-out, the existing animation loop continues with preserved buffer
  useEffect(() => {
    if (phase === 'burn-in') {
      // Fresh fire — reinitialize buffer
      fireRef.current = null;
      runAnimation();
    } else if (phase === 'burn-out') {
      // Continue animation with existing fire buffer (if available)
      // If no existing buffer (edge case), start fresh anyway
      if (!rafRef.current) {
        runAnimation();
      }
      // If animation is already running, it will read the updated phaseRef
    }

    return () => {
      if (phase === 'idle') {
        stopAnimation();
      }
    };
  }, [phase, runAnimation, stopAnimation]);

  // Intercept internal link clicks to trigger flame transition
  useEffect(() => {
    function handleClick(e) {
      if (phaseRef.current !== 'idle') return;

      const anchor = e.target.closest('a');
      if (!anchor) return;

      const href = anchor.getAttribute('href');
      if (!href) return;

      // Skip external links, mailto, tel, anchors, new tabs, downloads
      if (
        href.startsWith('http') || href.startsWith('mailto:') ||
        href.startsWith('tel:') || href.startsWith('#') ||
        anchor.target === '_blank' || anchor.hasAttribute('download')
      ) return;

      // Skip same page and API routes
      if (href === pathname || href.startsWith('/api/')) return;

      e.preventDefault();
      e.stopPropagation();

      pendingHref.current = href;
      setPhase('burn-in');
      startTimeRef.current = performance.now();

      setTimeout(() => {
        if (pendingHref.current) {
          router.push(pendingHref.current);
          pendingHref.current = null;
        }
      }, BURN_IN_TIME + HOLD_TIME);
    }

    document.addEventListener('click', handleClick, true);
    return () => document.removeEventListener('click', handleClick, true);
  }, [pathname, router]);

  // Global flame navigate for programmatic navigation (Random Song button etc.)
  useEffect(() => {
    window.__flameNavigate = (href) => {
      if (phaseRef.current !== 'idle') {
        router.push(href);
        return;
      }
      pendingHref.current = href;
      setPhase('burn-in');
      startTimeRef.current = performance.now();

      setTimeout(() => {
        if (pendingHref.current) {
          router.push(pendingHref.current);
          pendingHref.current = null;
        }
      }, BURN_IN_TIME + HOLD_TIME);
    };

    return () => { delete window.__flameNavigate; };
  }, [router]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopAnimation();
      delete window.__flameNavigate;
    };
  }, [stopAnimation]);

  if (phase === 'idle') return null;

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 99999 }}
      aria-hidden="true"
    />
  );
}
