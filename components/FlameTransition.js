'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { usePathname, useRouter } from 'next/navigation';

// ─── Smooth fire color palette (64 entries for smoother gradients) ───
function buildFirePalette() {
  const palette = [];
  const keyColors = [
    [0, 0, 0],       // 0  - black
    [20, 4, 2],      // 8  - very dark red
    [60, 8, 4],      // 14 - dark maroon
    [120, 16, 4],    // 20 - deep red
    [180, 30, 4],    // 26 - red
    [210, 60, 8],    // 32 - red-orange
    [230, 90, 10],   // 38 - orange
    [240, 130, 20],  // 44 - bright orange
    [250, 170, 40],  // 50 - yellow-orange
    [255, 210, 80],  // 56 - yellow
    [255, 240, 160], // 60 - pale yellow
    [255, 255, 220], // 63 - near white
  ];
  const stops = [0, 8, 14, 20, 26, 32, 38, 44, 50, 56, 60, 63];

  for (let i = 0; i <= 63; i++) {
    let segIdx = 0;
    for (let s = 0; s < stops.length - 1; s++) {
      if (i >= stops[s] && i <= stops[s + 1]) { segIdx = s; break; }
    }
    const t = (i - stops[segIdx]) / (stops[segIdx + 1] - stops[segIdx]);
    const c0 = keyColors[segIdx];
    const c1 = keyColors[segIdx + 1];
    palette.push([
      Math.round(c0[0] + (c1[0] - c0[0]) * t),
      Math.round(c0[1] + (c1[1] - c0[1]) * t),
      Math.round(c0[2] + (c1[2] - c0[2]) * t),
    ]);
  }
  return palette;
}

const FIRE_PALETTE = buildFirePalette();
const MAX_HEAT = 63;

const PIXEL_SIZE = 2;         // Finer resolution for smoother look
const BURN_IN_TIME = 700;     // ms for fire to cover screen
const HOLD_TIME = 100;        // ms to hold at full coverage
const BURN_OUT_TIME = 600;    // ms for fire to fade away
const MAX_PARTICLES = 250;    // Ember particle count

// ─── Ember Particle class ───
class Ember {
  constructor(screenW, screenH, fromBottom = true) {
    this.reset(screenW, screenH, fromBottom);
  }

  reset(screenW, screenH, fromBottom = true) {
    this.x = Math.random() * screenW;
    this.y = fromBottom ? screenH + Math.random() * 40 : screenH * (0.4 + Math.random() * 0.6);
    this.vx = (Math.random() - 0.5) * 1.5;
    this.vy = -(1.5 + Math.random() * 3.5);
    this.size = 1 + Math.random() * 3;
    this.life = 0.8 + Math.random() * 0.4;
    this.maxLife = this.life;
    this.brightness = 0.5 + Math.random() * 0.5;
    // Color: white-hot → yellow → orange → red
    const colorRand = Math.random();
    if (colorRand < 0.15) {
      this.color = [255, 255, 200]; // white-hot
    } else if (colorRand < 0.4) {
      this.color = [255, 220, 50];  // bright yellow
    } else if (colorRand < 0.7) {
      this.color = [255, 140, 20];  // orange
    } else {
      this.color = [255, 60, 10];   // red
    }
    this.turbulenceOffset = Math.random() * 1000;
    this.turbulenceSpeed = 2 + Math.random() * 3;
    this.active = true;
  }

  update(dt, time) {
    this.life -= dt;
    if (this.life <= 0) { this.active = false; return; }

    // Turbulence
    const turb = Math.sin(time * this.turbulenceSpeed + this.turbulenceOffset) * 0.8;
    this.x += this.vx + turb;
    this.y += this.vy;
    this.vy *= 0.995; // Slow down slightly
    this.size *= 0.998; // Shrink slightly
  }

  draw(ctx) {
    if (!this.active) return;
    const alpha = (this.life / this.maxLife) * this.brightness;
    if (alpha <= 0.01) return;

    const [r, g, b] = this.color;

    // Soft glow circle
    const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size * 3);
    gradient.addColorStop(0, `rgba(${r},${g},${b},${alpha})`);
    gradient.addColorStop(0.3, `rgba(${r},${g},${b},${alpha * 0.5})`);
    gradient.addColorStop(1, `rgba(${r},${g},${b},0)`);

    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size * 3, 0, Math.PI * 2);
    ctx.fill();

    // Bright core
    ctx.fillStyle = `rgba(${Math.min(255, r + 50)},${Math.min(255, g + 50)},${Math.min(255, b + 30)},${alpha * 0.9})`;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size * 0.5, 0, Math.PI * 2);
    ctx.fill();
  }
}

export default function FlameTransition() {
  const pathname = usePathname();
  const router = useRouter();
  const [phase, setPhase] = useState('idle');
  const prevPathRef = useRef(pathname);
  const pendingHref = useRef(null);
  const canvasRef = useRef(null);
  const fireRef = useRef(null);
  const rafRef = useRef(null);
  const phaseRef = useRef('idle');
  const startTimeRef = useRef(0);
  const particlesRef = useRef([]);
  const lastFrameRef = useRef(0);

  useEffect(() => { phaseRef.current = phase; }, [phase]);

  // Detect route change → burn-out
  useEffect(() => {
    if (pathname !== prevPathRef.current) {
      prevPathRef.current = pathname;
      phaseRef.current = 'burn-out';
      setPhase('burn-out');
      startTimeRef.current = performance.now();

      const timer = setTimeout(() => {
        setPhase('idle');
        stopAnimation();
        fireRef.current = null;
        particlesRef.current = [];
      }, BURN_OUT_TIME + 300);

      return () => clearTimeout(timer);
    }
  }, [pathname]);

  const stopAnimation = useCallback(() => {
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
  }, []);

  // ─── Main animation engine ───
  const runAnimation = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const W = window.innerWidth;
    const H = window.innerHeight;
    canvas.width = W;
    canvas.height = H;

    const ctx = canvas.getContext('2d');

    // Fire grid
    const fw = Math.ceil(W / PIXEL_SIZE);
    const fh = Math.ceil(H / PIXEL_SIZE);

    // Reuse existing buffer for burn-out, fresh for burn-in
    if (!fireRef.current || fireRef.current.width !== fw || fireRef.current.height !== fh) {
      fireRef.current = {
        buffer: new Uint8Array(fw * fh),
        width: fw,
        height: fh,
      };
    }

    const { buffer } = fireRef.current;

    // Create offscreen canvas for fire rendering
    const offCanvas = document.createElement('canvas');
    offCanvas.width = W;
    offCanvas.height = H;
    const offCtx = offCanvas.getContext('2d');
    const offImageData = offCtx.createImageData(W, H);

    // Initialize particles
    if (particlesRef.current.length === 0) {
      for (let i = 0; i < MAX_PARTICLES; i++) {
        particlesRef.current.push(new Ember(W, H, true));
      }
    }

    lastFrameRef.current = performance.now();

    const animate = (now) => {
      const currentPhase = phaseRef.current;
      if (currentPhase === 'idle') {
        rafRef.current = null;
        return;
      }

      const dt = Math.min((now - lastFrameRef.current) / 1000, 0.05);
      lastFrameRef.current = now;
      const elapsed = now - startTimeRef.current;
      const time = now / 1000;

      // ─── Update fire simulation ───
      if (currentPhase === 'burn-in') {
        const progress = Math.min(elapsed / BURN_IN_TIME, 1);
        // Ignite bottom rows — scale with progress for dramatic buildup
        const igniteRows = Math.max(2, Math.floor(progress * 8));
        for (let row = 0; row < igniteRows; row++) {
          const y = fh - 1 - row;
          if (y >= 0) {
            for (let x = 0; x < fw; x++) {
              const variation = Math.random() < 0.85 ? MAX_HEAT : MAX_HEAT - Math.floor(Math.random() * 10);
              buffer[y * fw + x] = variation;
            }
          }
        }
        // Dense sparks ahead of the fire front to fill the screen faster
        if (progress > 0.1) {
          const frontY = Math.floor(fh * (1 - progress * 0.9));
          const sparkCount = Math.floor(fw * 0.5 * progress);
          for (let i = 0; i < sparkCount; i++) {
            const sx = Math.floor(Math.random() * fw);
            const sy = frontY + Math.floor(Math.random() * Math.max(4, fh * progress * 0.4));
            if (sy >= 0 && sy < fh) {
              const sparkHeat = Math.floor(Math.random() * 20) + (MAX_HEAT - 20);
              buffer[sy * fw + sx] = Math.max(buffer[sy * fw + sx], sparkHeat);
            }
          }
        }
        // Vertical fire jets — random columns of intense heat that shoot upward
        if (progress > 0.2) {
          const jetCount = Math.floor(fw * 0.05 * progress);
          for (let j = 0; j < jetCount; j++) {
            const jx = Math.floor(Math.random() * fw);
            const jetHeight = Math.floor(fh * progress * (0.3 + Math.random() * 0.5));
            for (let dy = 0; dy < jetHeight; dy++) {
              const jy = fh - 1 - dy;
              if (jy >= 0) {
                // Slight horizontal drift for organic look
                const drift = jx + Math.floor((Math.random() - 0.5) * 3);
                const dx = Math.min(fw - 1, Math.max(0, drift));
                const jetHeat = Math.max(0, MAX_HEAT - Math.floor(dy * (MAX_HEAT / jetHeight) * 0.6));
                buffer[jy * fw + dx] = Math.max(buffer[jy * fw + dx], jetHeat);
              }
            }
          }
        }
      } else if (currentPhase === 'burn-out') {
        const progress = Math.min(elapsed / BURN_OUT_TIME, 1);
        // Kill the heat source at bottom immediately
        const bottomHeat = Math.max(0, Math.floor(MAX_HEAT * Math.max(0, 1 - progress * 3)));
        for (let x = 0; x < fw; x++) {
          buffer[(fh - 1) * fw + x] = Math.min(buffer[(fh - 1) * fw + x], bottomHeat);
          // Also kill the second row
          if (fh > 1) buffer[(fh - 2) * fw + x] = Math.min(buffer[(fh - 2) * fw + x], bottomHeat);
        }
        // Aggressive global cooling — eases in then accelerates
        const coolAmount = Math.floor(progress * progress * 16) + (progress > 0.1 ? 1 : 0);
        for (let i = 0; i < buffer.length; i++) {
          buffer[i] = Math.max(0, buffer[i] - coolAmount);
        }
      }

      // ─── Doom fire propagation ───
      for (let x = 0; x < fw; x++) {
        for (let y = 1; y < fh; y++) {
          const src = y * fw + x;
          const heat = buffer[src];
          if (heat === 0) {
            buffer[(y - 1) * fw + x] = 0;
          } else {
            const rand = Math.round(Math.random() * 3);
            const dstX = Math.min(fw - 1, Math.max(0, x - rand + 1));
            const decay = Math.floor(Math.random() * 2);
            buffer[(y - 1) * fw + dstX] = Math.max(0, heat - decay);
          }
        }
      }

      // ─── Render fire to offscreen canvas ───
      const pixels = offImageData.data;
      for (let y = 0; y < fh; y++) {
        for (let x = 0; x < fw; x++) {
          const heat = buffer[y * fw + x];
          if (heat === 0) {
            // Transparent pixel blocks
            for (let py = 0; py < PIXEL_SIZE; py++) {
              for (let px = 0; px < PIXEL_SIZE; px++) {
                const rX = x * PIXEL_SIZE + px;
                const rY = y * PIXEL_SIZE + py;
                if (rX < W && rY < H) {
                  const idx = (rY * W + rX) * 4;
                  pixels[idx + 3] = 0;
                }
              }
            }
            continue;
          }
          const color = FIRE_PALETTE[Math.min(heat, MAX_HEAT)];

          for (let py = 0; py < PIXEL_SIZE; py++) {
            for (let px = 0; px < PIXEL_SIZE; px++) {
              const rX = x * PIXEL_SIZE + px;
              const rY = y * PIXEL_SIZE + py;
              if (rX < W && rY < H) {
                const idx = (rY * W + rX) * 4;
                pixels[idx] = color[0];
                pixels[idx + 1] = color[1];
                pixels[idx + 2] = color[2];
                pixels[idx + 3] = Math.min(255, heat * 6);
              }
            }
          }
        }
      }
      offCtx.putImageData(offImageData, 0, 0);

      // ─── Composite to main canvas ───
      ctx.clearRect(0, 0, W, H);

      // During burn-out, reduce intensity progressively
      const isBurnOut = currentPhase === 'burn-out';
      const burnOutFade = isBurnOut ? Math.max(0, 1 - (elapsed / BURN_OUT_TIME)) : 1;

      // Layer 1: Blurred fire base (warm glow)
      ctx.save();
      ctx.filter = 'blur(6px)';
      ctx.globalAlpha = 0.7 * burnOutFade;
      ctx.drawImage(offCanvas, 0, 0);
      ctx.restore();

      // Layer 2: Slightly blurred fire (medium detail)
      ctx.save();
      ctx.filter = 'blur(2px)';
      ctx.globalAlpha = 0.85 * (isBurnOut ? Math.max(0.3, burnOutFade) : 1);
      ctx.drawImage(offCanvas, 0, 0);
      ctx.restore();

      // Layer 3: Sharp fire on top (fine detail + brightness) — fade faster during burn-out
      ctx.save();
      ctx.globalAlpha = 0.6 * (isBurnOut ? burnOutFade * burnOutFade : 1);
      ctx.globalCompositeOperation = 'lighter';
      ctx.drawImage(offCanvas, 0, 0);
      ctx.restore();

      // ─── Ember particles ───
      ctx.save();
      ctx.globalCompositeOperation = 'lighter';
      const particles = particlesRef.current;
      let activeCount = 0;

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        if (p.active) {
          p.update(dt, time);
          p.draw(ctx);
          activeCount++;
          // Remove particles that go off screen
          if (p.y < -50 || p.x < -50 || p.x > W + 50) {
            p.active = false;
          }
        }
      }

      // Respawn dead particles during burn-in or early burn-out
      if (currentPhase === 'burn-in' || (currentPhase === 'burn-out' && elapsed < BURN_OUT_TIME * 0.5)) {
        const spawnRate = currentPhase === 'burn-in'
          ? Math.min(elapsed / BURN_IN_TIME, 1) * 0.8
          : Math.max(0, 1 - (elapsed / (BURN_OUT_TIME * 0.5))) * 0.3;

        for (let i = 0; i < particles.length; i++) {
          if (!particles[i].active && Math.random() < spawnRate * 0.15) {
            particles[i].reset(W, H, true);
          }
        }
      }
      ctx.restore();

      // ─── Heat haze / glow at the top edge ───
      if (currentPhase === 'burn-in') {
        const progress = Math.min(elapsed / BURN_IN_TIME, 1);
        if (progress > 0.3) {
          const hazeAlpha = (progress - 0.3) * 0.15;
          const gradient = ctx.createLinearGradient(0, 0, 0, H * 0.3);
          gradient.addColorStop(0, `rgba(40, 10, 0, ${hazeAlpha})`);
          gradient.addColorStop(1, 'rgba(40, 10, 0, 0)');
          ctx.fillStyle = gradient;
          ctx.fillRect(0, 0, W, H * 0.3);
        }
      }

      rafRef.current = requestAnimationFrame(animate);
    };

    stopAnimation();
    rafRef.current = requestAnimationFrame(animate);
  }, [stopAnimation]);

  // Phase-based animation control
  useEffect(() => {
    if (phase === 'burn-in') {
      fireRef.current = null;
      particlesRef.current = [];
      runAnimation();
    } else if (phase === 'burn-out') {
      if (!rafRef.current) {
        runAnimation();
      }
    }
    return () => {
      if (phase === 'idle') stopAnimation();
    };
  }, [phase, runAnimation, stopAnimation]);

  // ─── Click interceptor for internal links ───
  useEffect(() => {
    function handleClick(e) {
      if (phaseRef.current !== 'idle') return;

      const anchor = e.target.closest('a');
      if (!anchor) return;

      const href = anchor.getAttribute('href');
      if (!href) return;

      if (
        href.startsWith('http') || href.startsWith('mailto:') ||
        href.startsWith('tel:') || href.startsWith('#') ||
        anchor.target === '_blank' || anchor.hasAttribute('download')
      ) return;

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

  // ─── Global programmatic navigation (Random Song, etc.) ───
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
