'use client';

import { useState } from 'react';
import { getSubPageTranslation } from '@/lib/subPageI18n';

export default function NewsletterSignup({ variant = 'default', lang = 'en' }) {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState(null); // null, 'loading', 'success', 'already', 'error'
  const [message, setMessage] = useState('');
  
const t = getSubPageTranslation(lang);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email || !email.includes('@')) return;

    setStatus('loading');
    try {
      const res = await fetch('/api/newsletter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();

      if (res.ok) {
        if (data.already_subscribed) {
          setStatus('already');
          setMessage('You\'re already subscribed! 🎸');
        } else {
          setStatus('success');
          setMessage('You\'re in! Watch for new lessons. 🤘');
        }
        setEmail('');
      } else {
        setStatus('error');
        setMessage(data.error || 'Something went wrong');
      }
    } catch {
      setStatus('error');
      setMessage('Network error. Try again.');
    }
  }

  if (variant === 'compact') {
    return (
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          className="flex-1 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500 transition-colors"
          required
        />
        <button
          type="submit"
          disabled={status === 'loading'}
          className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-black font-bold text-sm rounded-lg transition-colors disabled:opacity-50"
        >
          {status === 'loading' ? '...' : 'Join'}
        </button>
        {status && status !== 'loading' && (
          <span className={`text-xs self-center ${status === 'success' || status === 'already' ? 'text-green-400' : 'text-red-400'}`}>
            {message}
          </span>
        )}
      </form>
    );
  }

  return (
    <div className="p-6 sm:p-8 bg-gradient-to-br from-zinc-900 via-zinc-900 to-zinc-800 rounded-2xl border border-zinc-700">
      <div className="text-center max-w-md mx-auto">
        <h3 className="text-xl font-bold text-white mb-2">
          🎸 {t.newsletterTitle}
        </h3>
        <p className="text-zinc-400 text-sm mb-5">
          {t.newsletterSubtitle}
        </p>

        {status === 'success' || status === 'already' ? (
          <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-xl">
            <p className="text-green-400 font-medium">{message}</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t.emailPlaceholder}
              className="flex-1 px-5 py-3 bg-zinc-800 border border-zinc-600 rounded-xl text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-all"
              required
            />
            <button
              type="submit"
              disabled={status === 'loading'}
              className="px-6 py-3 bg-amber-500 hover:bg-amber-400 text-black font-bold rounded-xl transition-colors disabled:opacity-50 whitespace-nowrap"
            >
              {status === 'loading' ? t.subscribing : t.subscribeFree}
            </button>
          </form>
        )}

        {status === 'error' && (
          <p className="text-red-400 text-sm mt-3">{message}</p>
        )}

        <p className="text-zinc-600 text-xs mt-4">
          {t.newsletterFooter}
        </p>
      </div>
    </div>
  );
}
