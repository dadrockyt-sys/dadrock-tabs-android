'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
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

function basicAuthorization(password) {
  return `Basic ${window.btoa(`admin:${password}`)}`;
}

function tokenStatus(token) {
  const expired =
    token.expiresAt &&
    new Date(token.expiresAt) <= new Date();

  if (!token.active) return 'Disabled';
  if (expired) return 'Expired';
  if (Number(token.usesRemaining) <= 0) return 'Used';
  return 'Active';
}

function formatDate(value) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleString();
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
  const [status, setStatus] = useState({ type: '', message: '' });

  const [tokenType, setTokenType] = useState('testing');
  const [quantity, setQuantity] = useState(1);
  const [uses, setUses] = useState(1);
  const [assignedEmail, setAssignedEmail] = useState('');
  const [expiresAt, setExpiresAt] = useState('');
  const [notes, setNotes] = useState('');
  const [expandedTokenId, setExpandedTokenId] = useState('');

  const storedPassword = useCallback(
    () => window.sessionStorage.getItem('dadrock_admin_auth') || '',
    []
  );

  const authorization = useCallback(
    () => basicAuthorization(storedPassword()),
    [storedPassword]
  );

  const loadTokens = useCallback(async () => {
    if (!storedPassword()) return;

    setIsLoading(true);
    try {
      const response = await fetch('/api/admin/bts-tokens', {
        headers: { Authorization: authorization() },
        cache: 'no-store',
      });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        if (response.status === 401) {
          setAuthStatus('unauthorized');
          window.sessionStorage.removeItem('dadrock_admin_auth');
        }
        throw new Error(data.error || 'Unable to load BTS tokens.');
      }

      setTokens(data.tokens || []);
      setStats(data.stats || EMPTY_STATS);
      setAuthStatus('authorized');
    } catch (error) {
      setStatus({
        type: 'error',
        message: error instanceof Error ? error.message : 'Unable to load BTS tokens.',
      });
    } finally {
      setIsLoading(false);
    }
  }, [authorization, storedPassword]);

  useEffect(() => {
    const verify = async () => {
      const savedPassword = storedPassword();
      if (!savedPassword) {
        setAuthStatus('unauthorized');
        return;
      }

      try {
        const response = await fetch('/api/admin/tab-studio-auth', {
          headers: { Authorization: basicAuthorization(savedPassword) },
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

    verify();
  }, [storedPassword]);

  useEffect(() => {
    if (authStatus === 'authorized') {
      loadTokens();
    }
  }, [authStatus, loadTokens]);

  const handleLogin = async (event) => {
    event.preventDefault();
    const nextPassword = password.trim();
    if (!nextPassword) return;

    setIsLoggingIn(true);
    setAuthError('');

    try {
      const response = await fetch('/api/admin/tab-studio-auth', {
        headers: { Authorization: basicAuthorization(nextPassword) },
        cache: 'no-store',
      });

      if (!response.ok) {
        throw new Error('Invalid admin password.');
      }

      window.sessionStorage.setItem('dadrock_admin_auth', nextPassword);
      setPassword('');
      setAuthStatus('authorized');
    } catch (error) {
      setAuthError(
        error instanceof Error ? error.message : 'Unable to sign in.'
      );
    } finally {
      setIsLoggingIn(false);
    }
  };

  const generateTokens = async () => {
    setIsGenerating(true);
    setStatus({ type: '', message: '' });

    try {
      const response = await fetch('/api/admin/bts-tokens', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: authorization(),
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
      if (!response.ok) {
        throw new Error(data.error || 'Unable to generate BTS tokens.');
      }

      setStatus({
        type: 'success',
        message: `${data.tokens?.length || 0} BTS token(s) generated successfully.`,
      });
      await loadTokens();
    } catch (error) {
      setStatus({
        type: 'error',
        message: error instanceof Error ? error.message : 'Unable to generate BTS tokens.',
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const updateToken = async (id, action, active = false) => {
    setStatus({ type: '', message: '' });

    try {
      const response = await fetch('/api/admin/bts-tokens', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: authorization(),
        },
        body: JSON.stringify({ id, action, active }),
      });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.error || 'Unable to update BTS token.');
      }

      await loadTokens();
    } catch (error) {
      setStatus({
        type: 'error',
        message: error instanceof Error ? error.message : 'Unable to update BTS token.',
      });
    }
  };

  const activeTokens = useMemo(
    () => tokens.filter((token) => tokenStatus(token) === 'Active').length,
    [tokens]
  );

  if (authStatus === 'checking') {
    return (
      <main className="flex min-h-screen items-center justify-center bg-zinc-950 text-white">
        <div className="text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-orange-400" />
          <p className="mt-3 text-sm text-zinc-400">Checking admin access…</p>
        </div>
      </main>
    );
  }

  if (authStatus !== 'authorized') {
    return (
      <main className="min-h-screen bg-zinc-950 px-4 py-10 text-white">
        <div className="mx-auto max-w-md">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm font-semibold text-zinc-400 hover:text-orange-400"
          >
            <ArrowLeft className="h-4 w-4" /> DadRock Tabs
          </Link>

          <section className="mt-8 rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-orange-500/10 p-3 text-orange-400">
                <LockKeyhole className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-xl font-black">BTS Token Admin</h1>
                <p className="text-sm text-zinc-500">Use the same admin password as the main panel.</p>
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

              {authError && (
                <p className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">
                  {authError}
                </p>
              )}

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
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Link
              href="/bts"
              className="inline-flex items-center gap-2 text-sm font-semibold text-zinc-400 hover:text-orange-400"
            >
              <ArrowLeft className="h-4 w-4" /> Backing Track Studio
            </Link>
            <h1 className="mt-3 flex items-center gap-3 text-3xl font-black">
              <KeyRound className="h-8 w-8 text-green-400" />
              Backing Track Studio Tokens
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-zinc-400">
              Separate from AI Tab tokens. BTS uses the same multi-use, assigned-email, expiration, disable/enable, and redemption-tracking rules.
            </p>
          </div>

          <button
            type="button"
            onClick={loadTokens}
            disabled={isLoading}
            className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-zinc-800 px-4 py-2 font-bold text-zinc-200 hover:bg-zinc-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        <section className="mt-7 rounded-2xl border border-green-500/20 bg-green-500/5 p-5">
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-green-400" />
            <div>
              <p className="font-bold text-green-300">Token systems are isolated</p>
              <p className="mt-1 text-xs leading-5 text-zinc-400">
                BTS tokens use the <span className="font-mono text-green-300">BTS-XXXX-XXXX-XXXX</span> format and the <span className="font-mono">bts_tokens</span> database collection. AI Tab <span className="font-mono">DRT-...</span> tokens and their tracker are unchanged.
              </p>
            </div>
          </div>
        </section>

        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {[
            ['Total', stats.total, 'text-white'],
            ['Active', stats.active ?? activeTokens, 'text-green-400'],
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
              <select
                value={tokenType}
                onChange={(event) => setTokenType(event.target.value)}
                className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-3 py-3 text-white"
              >
                <option value="testing">Testing</option>
                <option value="giveaway">Giveaway</option>
                <option value="promotion">Promotion</option>
                <option value="customer">Customer</option>
                <option value="support">Customer Support</option>
              </select>
            </label>

            <label className="text-sm font-semibold text-zinc-400">
              Quantity
              <input
                type="number"
                min="1"
                max="100"
                value={quantity}
                onChange={(event) => setQuantity(event.target.value)}
                className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-3 py-3 text-white"
              />
            </label>

            <label className="text-sm font-semibold text-zinc-400">
              Uses Per Token
              <input
                type="number"
                min="1"
                max="100"
                value={uses}
                onChange={(event) => setUses(event.target.value)}
                className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-3 py-3 text-white"
              />
            </label>

            <label className="text-sm font-semibold text-zinc-400">
              Assigned Email (optional)
              <input
                type="email"
                value={assignedEmail}
                onChange={(event) => setAssignedEmail(event.target.value)}
                placeholder="tester@example.com"
                className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-3 py-3 text-white placeholder:text-zinc-700"
              />
            </label>

            <label className="text-sm font-semibold text-zinc-400">
              Expiration (optional)
              <input
                type="datetime-local"
                value={expiresAt}
                onChange={(event) => setExpiresAt(event.target.value)}
                className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-3 py-3 text-white"
              />
            </label>

            <label className="text-sm font-semibold text-zinc-400">
              Notes (optional)
              <input
                type="text"
                value={notes}
                onChange={(event) => setNotes(event.target.value)}
                placeholder="Beta tester, giveaway…"
                className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-3 py-3 text-white placeholder:text-zinc-700"
              />
            </label>
          </div>

          <button
            type="button"
            onClick={generateTokens}
            disabled={isGenerating || Number(quantity) < 1 || Number(uses) < 1}
            className="mt-5 inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl bg-green-600 px-5 py-3 font-black text-white hover:bg-green-500 disabled:opacity-50 sm:w-auto"
          >
            {isGenerating ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <KeyRound className="h-5 w-5" />
            )}
            {isGenerating ? 'Generating…' : 'Generate BTS Tokens'}
          </button>
        </section>

        {status.message && (
          <div className={`mt-5 rounded-xl border p-4 text-sm ${status.type === 'success' ? 'border-green-500/30 bg-green-500/10 text-green-300' : 'border-red-500/30 bg-red-500/10 text-red-300'}`}>
            {status.type === 'success' && <CheckCircle2 className="mr-2 inline h-4 w-4" />}
            {status.message}
          </div>
        )}

        <section className="mt-6 overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900">
          <div className="border-b border-zinc-800 px-5 py-4">
            <h2 className="font-black">BTS Token Tracker</h2>
            <p className="mt-1 text-xs text-zinc-500">Tap a token row to view its redemption history.</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px] text-sm">
              <thead className="bg-zinc-950 text-zinc-500">
                <tr>
                  <th className="px-4 py-3 text-left">Token</th>
                  <th className="px-4 py-3 text-left">Type</th>
                  <th className="px-4 py-3 text-left">Email</th>
                  <th className="px-4 py-3 text-center">Uses</th>
                  <th className="px-4 py-3 text-left">Expires</th>
                  <th className="px-4 py-3 text-left">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {isLoading && tokens.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-4 py-10 text-center text-zinc-500">
                      <Loader2 className="mx-auto h-6 w-6 animate-spin" />
                    </td>
                  </tr>
                ) : tokens.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-4 py-10 text-center text-zinc-500">
                      No BTS tokens generated yet.
                    </td>
                  </tr>
                ) : (
                  tokens.map((token) => {
                    const currentStatus = tokenStatus(token);
                    const expanded = expandedTokenId === token._id;
                    const redemptions = Array.isArray(token.redemptions) ? token.redemptions : [];

                    return (
                      <tbody key={token._id}>
                        <tr
                          className="cursor-pointer border-t border-zinc-800 hover:bg-zinc-800/40"
                          onClick={() => setExpandedTokenId(expanded ? '' : token._id)}
                        >
                          <td className="px-4 py-3 font-mono font-bold text-green-300">{token.code}</td>
                          <td className="px-4 py-3 capitalize text-zinc-300">{token.type}</td>
                          <td className="px-4 py-3 text-zinc-400">{token.assignedEmail || 'Not assigned'}</td>
                          <td className="px-4 py-3 text-center text-white">{token.usesRemaining}/{token.usesAllowed}</td>
                          <td className="px-4 py-3 text-zinc-500">{token.expiresAt ? formatDate(token.expiresAt) : 'No expiry'}</td>
                          <td className="px-4 py-3">
                            <span className={`rounded-full px-2 py-1 text-xs font-bold ${currentStatus === 'Active' ? 'bg-green-500/15 text-green-300' : currentStatus === 'Used' ? 'bg-blue-500/15 text-blue-300' : currentStatus === 'Expired' ? 'bg-amber-500/15 text-amber-300' : 'bg-red-500/15 text-red-300'}`}>
                              {currentStatus}
                            </span>
                          </td>
                          <td className="px-4 py-3" onClick={(event) => event.stopPropagation()}>
                            <div className="flex justify-end gap-2">
                              <button
                                type="button"
                                title="Copy token"
                                onClick={() => navigator.clipboard.writeText(token.code)}
                                className="rounded-lg bg-zinc-800 p-2 text-zinc-300 hover:text-white"
                              >
                                <Copy className="h-4 w-4" />
                              </button>
                              <button
                                type="button"
                                onClick={() => updateToken(token._id, 'toggle', !token.active)}
                                className="rounded-lg bg-zinc-800 px-3 py-2 text-xs font-bold text-zinc-300 hover:text-white"
                              >
                                {token.active ? 'Disable' : 'Enable'}
                              </button>
                              <button
                                type="button"
                                onClick={() => {
                                  if (window.confirm('Delete this BTS token permanently?')) {
                                    updateToken(token._id, 'delete');
                                  }
                                }}
                                className="rounded-lg bg-red-500/10 p-2 text-red-400 hover:bg-red-500/20"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </td>
                        </tr>

                        {expanded && (
                          <tr className="border-t border-zinc-800 bg-zinc-950/70">
                            <td colSpan="7" className="px-5 py-4">
                              <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
                                <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4 text-xs text-zinc-400">
                                  <p><span className="font-bold text-zinc-300">Created:</span> {formatDate(token.createdAt)}</p>
                                  <p className="mt-2"><span className="font-bold text-zinc-300">Notes:</span> {token.notes || 'None'}</p>
                                  <p className="mt-2"><span className="font-bold text-zinc-300">Redemptions:</span> {redemptions.length}</p>
                                </div>

                                <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
                                  <p className="text-xs font-bold uppercase tracking-wider text-zinc-500">Redemption History</p>
                                  {redemptions.length === 0 ? (
                                    <p className="mt-3 text-xs text-zinc-600">This token has not been used yet.</p>
                                  ) : (
                                    <div className="mt-3 space-y-2">
                                      {[...redemptions].reverse().map((redemption, index) => (
                                        <div key={`${token._id}-${index}`} className="rounded-lg bg-zinc-950 px-3 py-2 text-xs text-zinc-400">
                                          <div className="flex flex-wrap items-center justify-between gap-2">
                                            <span className="font-semibold text-zinc-300">{redemption.customerEmail}</span>
                                            <span>{formatDate(redemption.redeemedAt)}</span>
                                          </div>
                                          <p className="mt-1 capitalize text-green-400">{String(redemption.removalMode || '').replace('guitar-bass', 'guitars + bass').replace('guitar', 'guitars')}</p>
                                        </div>
                                      ))}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </tbody>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}
