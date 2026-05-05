'use client';

import { useState, useEffect, useRef } from 'react';

export default function ExitIntentPopup() {
  const [show, setShow] = useState(false);
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  const triggered = useRef(false);
  const dismissed = useRef(false);

  useEffect(() => {
    // Don't show if already subscribed or dismissed this session
    if (localStorage.getItem('dadrock_newsletter_subscribed')) return;
    if (sessionStorage.getItem('dadrock_exit_dismissed')) return;

    // Wait 10 seconds before arming the exit intent
    const armTimer = setTimeout(() => {
      const handleMouseLeave = (e) => {
        if (e.clientY <= 0 && !triggered.current && !dismissed.current) {
          triggered.current = true;
          setShow(true);
        }
      };

      // For mobile: detect back button or scroll up fast
      const handleScroll = () => {
        if (window.scrollY === 0 && !triggered.current && !dismissed.current) {
          // User scrolled to very top - might be leaving
          // Only trigger after they've scrolled down first
          if (window._hasScrolledDown) {
            triggered.current = true;
            setShow(true);
          }
        }
        if (window.scrollY > 300) {
          window._hasScrolledDown = true;
        }
      };

      document.addEventListener('mouseleave', handleMouseLeave);
      window.addEventListener('scroll', handleScroll, { passive: true });

      return () => {
        document.removeEventListener('mouseleave', handleMouseLeave);
        window.removeEventListener('scroll', handleScroll);
      };
    }, 10000);

    return () => clearTimeout(armTimer);
  }, []);

  const handleDismiss = () => {
    setShow(false);
    dismissed.current = true;
    sessionStorage.setItem('dadrock_exit_dismissed', 'true');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !email.includes('@')) {
      setError('Please enter a valid email');
      return;
    }

    try {
      const res = await fetch('/api/newsletter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      if (res.ok) {
        setSubmitted(true);
        localStorage.setItem('dadrock_newsletter_subscribed', 'true');
        setTimeout(() => setShow(false), 3000);
      } else {
        setError('Something went wrong. Try again!');
      }
    } catch {
      setError('Network error. Try again!');
    }
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 z-[99998] flex items-center justify-center p-4" onClick={handleDismiss}>
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      {/* Modal */}
      <div
        className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 border-2 border-orange-500/50 rounded-2xl p-8 max-w-md w-full shadow-2xl shadow-orange-900/30 animate-in"
        onClick={e => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={handleDismiss}
          className="absolute top-3 right-3 text-gray-500 hover:text-white text-xl w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-700"
        >
          ✕
        </button>

        {!submitted ? (
          <>
            <div className="text-center mb-6">
              <span className="text-4xl">🎸</span>
              <h2 className="text-2xl font-bold text-orange-400 mt-3">Wait! Don&apos;t Miss Out</h2>
              <p className="text-gray-300 mt-2">
                Get the <span className="text-yellow-400 font-bold">Tab of the Week</span> delivered to your inbox.
                Free guitar lessons for classic rock fans.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-orange-500"
              />
              {error && <p className="text-red-400 text-sm">{error}</p>}
              <button
                type="submit"
                className="w-full py-3 bg-gradient-to-r from-orange-500 to-red-600 text-white font-bold rounded-lg hover:from-orange-600 hover:to-red-700 transition-all"
              >
                🔥 Get Free Weekly Tabs
              </button>
            </form>

            <p className="text-gray-500 text-xs text-center mt-3">No spam. Unsubscribe anytime.</p>
          </>
        ) : (
          <div className="text-center py-4">
            <span className="text-5xl">🤘</span>
            <h2 className="text-2xl font-bold text-green-400 mt-3">You&apos;re In!</h2>
            <p className="text-gray-300 mt-2">Welcome to the DadRock family. Rock on!</p>
          </div>
        )}
      </div>
    </div>
  );
}
