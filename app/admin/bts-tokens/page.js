'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  CheckCircle2,
  Copy,
  KeyRound,
  Loader2,
  LockKeyhole,
  Plus,
  RefreshCw,
  ShieldCheck,
  Trash2,
} from 'lucide-react';

const EMPTY_STATS = {
  total: 0,
  active: 0,
  used: 0,
  expired: 0,
  disabled: 0,
  redemptions: 0,
};

function authHeader(password) {
  return `Basic ${window.btoa(`admin:${password}`)}`;
}

function getStatus(token) {
  if (!token.active) return 'Disabled';
  if (token.expiresAt && new Date(token.expiresAt) <= new Date()) return 'Expired';
  if (Number(token.usesRemaining) <= 0) return 'Used';
  return 'Active';
}

function statusClasses(status) {
  if (status === 'Active') return 'bg-green-500/15 text-green-300';
  if (status === 'Used') return 'bg-blue-500/15 text-blue-300';
  if (status === 'Expired') return 'bg-amber-500/15 text-amber-300';
  return 'bg-red-500/15 text-red-300';
}

function formatDate(value) {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleString();
}

function formatRemoval(value) {
  if (value === 'guitar-bass') return 'Remove Guitars + Bass';
  if (value === 'guitar') return 'Remove Guitars';
  if (value === 'bass') return 'Remove Bass';
  return value || 'Backing track';
}

export default function AdminBtsTokensPage() {
  const [authStatus, setAuthStatus] = useState('checking');
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const [tokens, setTokens] = useState([]);
  const [stats, setStats] = useState(EMPTY_STATS);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [expandedTokenId, setExpandedTokenId] = useState('');

  const [tokenType, setTokenType] = useState('testing');
  const [quantity, setQuantity] = useState(1);
  const [uses, setUses] = useState(1);
  const [assignedEmail, setAssignedEmail] = useState('');
  const [expiresAt, setExpiresAt] = useState('');
  const [notes, setNotes] = useState('');

  const storedPassword = useCallback(
    () => window.sessionStorage.getItem('dadrock_admin_auth') || '',
    []
  );

  const loadTokens = useCallback(async () => {
    const savedPassword = storedPassword();
    if (!savedPassword) return;

    setIsLoading(true);
    try {
      const response = await fetch('/api/admin/bts-tokens', {
        headers: { Authorization: authHeader(savedPassword) },
        cache: 'no-store',
      });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        if (response.status === 401) {
          window.sessionStorage.removeItem('dadrock_admin_auth');
          setAuthStatus('unauthorized');
        }
        throw new Error(data.error || 'Unable to load BTS tokens.');
      }

      setTokens(data.tokens || []);
      setStats(data.stats || EMPTY_STATS);
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Unable to load BTS tokens.',
      });
    } finally {
      setIsLoading(false);
    }
  }, [storedPassword]);

  useEffect(() => {
    const verifySavedLogin = async () => {
      const savedPassword = storedPassword();
      if (!savedPassword) {
        setAuthStatus('unauthorized');
        return;
      }

      try {
        const response = await fetch('/api/admin/tab-studio-auth', {
          headers: { Authorization: authHeader(savedPassword) },
          cache: 'no-store',
        });

        if (!response.ok) {
          window.sessionStorage.removeItem('dadrock_admin_auth');
          setAuthStatus('unauthorized');
          return;
        }

        setAuthStatus('authorized');
      } catch {
        setAuthStatus('unauthorized');
      }
    };

    verifySavedLogin();
  }, [storedPassword]);

  useEffect(() => {
    if (authStatus === 'authorized') loadTokens();
  }, [authStatus, loadTokens]);

  const handleLogin = async (event) => {
    event.preventDefault();
    const nextPassword = password.trim();
    if (!nextPassword) return;

    setIsLoggingIn(true);
    setAuthError('');
    try {
      const response = await fetch('/api/admin/tab-studio-auth', {
        headers: { Authorization: authHeader(nextPassword) },
        cache: 'no-store',
      });

      if (!response.ok) throw new Error('Invalid admin password.');

      window.sessionStorage.setItem('dadrock_admin_auth', nextPassword);
      setPassword('');
      setAuthStatus('authorized');
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'Unable to sign in.');
    } finally {
      setIsLoggingIn(false);
    }
  };

  const generateTokens = async () => {
    const savedPassword = storedPassword();
    if (!savedPassword) return;

    setIsGenerating(true);
    setMessage({ type: '', text: '' });
    try {
      const response = await fetch('/api/admin/bts-tokens', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: authHeader(savedPassword),
        },
        body: JSON.stringify({
          action: 'generate',
          type: tokenType,
          quantity: Number(quantity),
          uses: Number(uses),
          assignedEmail: assignedEmail.trim(),
          expiresAt: expiresAt || null,
          notes: notes.trim(),
        }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || 'Unable to generate BTS tokens.');

      setMessage({
        type: 'success',
        text: `${data.tokens?.length || 0} BTS token(s) generated successfully.`,
      });
      await loadTokens();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Unable to generate BTS tokens.',
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const tokenAction = async (id, action, active = false) => {
    const savedPassword = storedPassword();
    if (!savedPassword) return;

    setMessage({ type: '', text: '' });
    try {
      const response = await fetch('/api/admin/bts-tokens', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: authHeader(savedPassword),
        },
        body: JSON.stringify({ id, action, active }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || 'Unable to update BTS token.');
      await loadTokens();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Unable to update BTS token.',
      });
    }
  };

  if (authStatus === 'checking') {
    return (
      <main className="flex min-h-screen items-center justify-center bg-zinc-950 text-white">
        <Loader2 className="h-8 w-8 animate-spin text-orange-400" />
      </main>
    );
  }

  if (authStatus !== 'authorized') {
    return (
      <main className="min-h-screen bg-zinc-950 px-4 py-10 text-white">
        <div className="mx-auto max-w-md">
          <Link href="/" className="inline-flex items-center gap-2 text-sm font-semibold text-zinc-400 hover:text-orange-400">
            <ArrowLeft className="h-4 w-4" /> DadRock Tabs
          </Link>
          <section className="mt-8 rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-orange-500/10 p-3 text-orange-400">
                <LockKeyhole className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-xl font-black">BTS Token Admin</h1>
                <p className="text-sm text-zinc-500">Same admin password as the main panel.</p>
              </div>
            </div>
            <form onSubmit={handleLogin} className="mt-6 space-y-4">
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Admin password"
                className="w-full rounded-xl border border-zinc-700 bg-zinc-950 px-4 py-3 outline-none focus:border-orange-500"
              />
              {authError && <p className="rounded-lg bg-red-500/10 p-3 text-sm text-red-300">{authError}</p>}
              <button
                type="submit"
                disabled={isLoggingIn || !password.trim()}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-orange-500 px-4 py-3 font-black text-black hover:bg-orange-400 disabled:opacity-50"
              >
                {isLoggingIn && <Loader2 className="h-5 w-5 animate-spin" />}
                {isLoggingIn ? 'Signing in…' : 'Open BTS Token Admin'}
              </button>
            </form>
          </section>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-white">
      <div className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Link href="/bts" className="inline-flex items-center gap-2 text-sm font-semibold text-zinc-400 hover:text-orange-400">
              <ArrowLeft className="h-4 w-4" /> Backing Track Studio
            </Link>
            <h1 className="mt-3 flex items-center gap-3 text-3xl font-black">
              <KeyRound className="h-8 w-8 text-green-400" /> Backing Track Studio Tokens
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-zinc-400">
              Separate from AI Tab tokens, with the same multi-use, assigned-email, expiration, enable/disable, and redemption tracking behavior.
            </p>
          </div>
          <button
            type="button"
            onClick={loadTokens}
            disabled={isLoading}
            className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-zinc-800 px-4 py-2 font-bold text-zinc-200 hover:bg-zinc-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </header>

        <section className="mt-7 rounded-2xl border border-green-500/20 bg-green-500/5 p-5">
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-green-400" />
            <p className="text-xs leading-5 text-zinc-400">
              BTS uses <span className="font-mono font-bold text-green-300">BTS-XXXX-XXXX-XXXX</span> codes in a separate <span className="font-mono">bts_tokens</span> collection. Existing AI Tab <span className="font-mono">DRT-...</span> tokens and their tracker stay untouched.
            </p>
          </div>
        </section>

        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {[
            ['Total', stats.total, 'text-white'],
            ['Active', stats.active, 'text-green-400'],
            ['Used', stats.used, 'text-blue-400'],
            ['Expired', stats.expired, 'text-amber-400'],
            ['Disabled', stats.disabled, 'text-red-400'],
            ['Redemptions', stats.redemptions, 'text-purple-400'],
          ].map(([label, value, color]) => (
            <div key={label} className="rounded-xl border border-zinc-800 bg-zinc-900 p-4 text-center">
              <p className={`text-2xl font-black ${color}`}>{value || 0}</p>
              <p className="mt-1 text-xs text-zinc-500">{label}</p>
            </div>
          ))}
        </div>

        <section className="mt-6 rounded-2xl border border-zinc-800 bg-zinc-900 p-5 sm:p-6">
          <h2 className="flex items-center gap-2 text-xl font-black">
            <Plus className="h-5 w-5 text-green-400" /> Generate BTS Tokens
          </h2>
          <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <label className="text-sm font-semibold text-zinc-400">
              Token Type
              <select value={tokenType} onChange={(event) => setTokenType(event.target.value)} className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-3 py-3 text-white">
                <option value="testing">Testing</option>
                <option value="giveaway">Giveaway</option>
                <option value="promotion">Promotion</option>
                <option value="customer">Customer</option>
                <option value="support">Customer Support</option>
              </select>
            </label>
            <label className="text-sm font-semibold text-zinc-400">
              Quantity
              <input type="number" min="1" max="100" value={quantity} onChange={(event) => setQuantity(event.target.value)} className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-3 py-3 text-white" />
            </label>
            <label className="text-sm font-semibold text-zinc-400">
              Uses Per Token
              <input type="number" min="1" max="100" value={uses} onChange={(event) => setUses(event.target.value)} className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-3 py-3 text-white" />
            </label>
            <label className="text-sm font-semibold text-zinc-400">
              Assigned Email (optional)
              <input type="email" value={assignedEmail} onChange={(event) => setAssignedEmail(event.target.value)} placeholder="tester@example.com" className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-3 py-3 text-white placeholder:text-zinc-700" />
            </label>
            <label className="text-sm font-semibold text-zinc-400">
              Expiration (optional)
              <input type="datetime-local" value={expiresAt} onChange={(event) => setExpiresAt(event.target.value)} className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-3 py-3 text-white" />
            </label>
            <label className="text-sm font-semibold text-zinc-400">
              Notes (optional)
              <input type="text" value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Beta tester, giveaway…" className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-3 py-3 text-white placeholder:text-zinc-700" />
            </label>
          </div>
          <button
            type="button"
            onClick={generateTokens}
            disabled={isGenerating || Number(quantity) < 1 || Number(uses) < 1}
            className="mt-5 inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl bg-green-600 px-5 py-3 font-black text-white hover:bg-green-500 disabled:opacity-50 sm:w-auto"
          >
            {isGenerating ? <Loader2 className="h-5 w-5 animate-spin" /> : <KeyRound className="h-5 w-5" />}
            {isGenerating ? 'Generating…' : 'Generate BTS Tokens'}
          </button>
        </section>

        {message.text && (
          <div className={`mt-5 rounded-xl border p-4 text-sm ${message.type === 'success' ? 'border-green-500/30 bg-green-500/10 text-green-300' : 'border-red-500/30 bg-red-500/10 text-red-300'}`}>
            {message.type === 'success' && <CheckCircle2 className="mr-2 inline h-4 w-4" />}
            {message.text}
          </div>
        )}

        <section className="mt-6 rounded-2xl border border-zinc-800 bg-zinc-900 p-5 sm:p-6">
          <div>
            <h2 className="text-xl font-black">BTS Token Tracker</h2>
            <p className="mt-1 text-xs text-zinc-500">Each token shows uses remaining and its BTS redemption history.</p>
          </div>

          <div className="mt-5 space-y-3">
            {isLoading && tokens.length === 0 ? (
              <div className="py-10 text-center text-zinc-500"><Loader2 className="mx-auto h-6 w-6 animate-spin" /></div>
            ) : tokens.length === 0 ? (
              <p className="py-10 text-center text-sm text-zinc-500">No BTS tokens generated yet.</p>
            ) : (
              tokens.map((token) => {
                const currentStatus = getStatus(token);
                const redemptions = Array.isArray(token.redemptions) ? token.redemptions : [];
                const expanded = expandedTokenId === token._id;

                return (
                  <article key={token._id} className="rounded-xl border border-zinc-800 bg-zinc-950/70">
                    <div className="p-4">
                      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                        <button type="button" onClick={() => setExpandedTokenId(expanded ? '' : token._id)} className="min-w-0 flex-1 text-left">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="font-mono font-black text-green-300">{token.code}</span>
                            <span className={`rounded-full px-2 py-1 text-xs font-bold ${statusClasses(currentStatus)}`}>{currentStatus}</span>
                            <span className="rounded-full bg-zinc-800 px-2 py-1 text-xs capitalize text-zinc-400">{token.type}</span>
                          </div>
                          <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-xs text-zinc-500">
                            <span>Email: {token.assignedEmail || 'Not assigned'}</span>
                            <span>Uses: <strong className="text-white">{token.usesRemaining}/{token.usesAllowed}</strong></span>
                            <span>Redemptions: {redemptions.length}</span>
                            <span>Expires: {token.expiresAt ? formatDate(token.expiresAt) : 'No expiry'}</span>
                          </div>
                        </button>

                        <div className="flex shrink-0 gap-2">
                          <button type="button" title="Copy token" onClick={() => navigator.clipboard.writeText(token.code)} className="rounded-lg bg-zinc-800 p-2 text-zinc-300 hover:text-white"><Copy className="h-4 w-4" /></button>
                          <button type="button" onClick={() => tokenAction(token._id, 'toggle', !token.active)} className="rounded-lg bg-zinc-800 px-3 py-2 text-xs font-bold text-zinc-300 hover:text-white">{token.active ? 'Disable' : 'Enable'}</button>
                          <button type="button" onClick={() => window.confirm('Delete this BTS token permanently?') && tokenAction(token._id, 'delete')} className="rounded-lg bg-red-500/10 p-2 text-red-400 hover:bg-red-500/20"><Trash2 className="h-4 w-4" /></button>
                        </div>
                      </div>

                      {expanded && (
                        <div className="mt-4 grid gap-4 border-t border-zinc-800 pt-4 lg:grid-cols-[0.8fr_1.2fr]">
                          <div className="rounded-lg bg-zinc-900 p-3 text-xs text-zinc-400">
                            <p><strong className="text-zinc-300">Created:</strong> {formatDate(token.createdAt)}</p>
                            <p className="mt-2"><strong className="text-zinc-300">Notes:</strong> {token.notes || 'None'}</p>
                          </div>
                          <div className="rounded-lg bg-zinc-900 p-3">
                            <p className="text-xs font-bold uppercase tracking-wider text-zinc-500">Redemption History</p>
                            {redemptions.length === 0 ? (
                              <p className="mt-3 text-xs text-zinc-600">This token has not been used yet.</p>
                            ) : (
                              <div className="mt-3 space-y-2">
                                {[...redemptions].reverse().map((redemption, index) => (
                                  <div key={`${token._id}-${index}`} className="rounded-lg bg-zinc-950 px-3 py-2 text-xs text-zinc-400">
                                    <div className="flex flex-wrap justify-between gap-2">
                                      <strong className="text-zinc-300">{redemption.customerEmail}</strong>
                                      <span>{formatDate(redemption.redeemedAt)}</span>
                                    </div>
                                    <p className="mt-1 text-green-400">{formatRemoval(redemption.removalMode)}</p>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </article>
                );
              })
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
