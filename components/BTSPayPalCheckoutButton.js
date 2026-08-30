'use client';

import { useEffect, useRef, useState } from 'react';

const PAYPAL_SCRIPT_ID = 'dadrock-paypal-sdk';

const TOKEN_ERROR_TITLES = {
  TOKEN_NOT_FOUND: 'Token Not Found',
  TOKEN_EXPIRED: 'Token Expired',
  TOKEN_EXHAUSTED: 'Token Fully Used',
  TOKEN_EMAIL_MISMATCH: 'Wrong Email Address',
  TOKEN_INACTIVE: 'Invalid Token',
};

export default function BTSPayPalCheckoutButton({
  customerEmail,
  removalMode,
  pathname,
  onPaymentCompleted,
  onPaymentCancelled,
  onPaymentError,
}) {
  const containerRef = useRef(null);
  const hasRenderedRef = useRef(false);

  const [isLoading, setIsLoading] = useState(true);
  const [paymentError, setPaymentError] = useState('');
  const [paymentCompleted, setPaymentCompleted] = useState(false);
  const [unlockMethod, setUnlockMethod] = useState('');

  const [showTokenEntry, setShowTokenEntry] = useState(false);
  const [freeTokenCode, setFreeTokenCode] = useState('');
  const [isRedeemingToken, setIsRedeemingToken] = useState(false);
  const [tokenError, setTokenError] = useState('');
  const [tokenErrorTitle, setTokenErrorTitle] = useState('');
  const [tokenUsesRemaining, setTokenUsesRemaining] = useState(null);

  useEffect(() => {
    let isCancelled = false;

    const clientId =
      process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID;

    if (!clientId) {
      setPaymentError('PayPal is not configured. You can still use a valid BTS token.');
      setIsLoading(false);
      return undefined;
    }

    async function renderPayPalButtons() {
      if (
        isCancelled ||
        hasRenderedRef.current ||
        !containerRef.current ||
        !window.paypal
      ) {
        return;
      }

      hasRenderedRef.current = true;
      setIsLoading(false);

      try {
        await window.paypal
          .Buttons({
            style: {
              layout: 'vertical',
              shape: 'rect',
              label: 'paypal',
              height: 48,
            },

            createOrder: async () => {
              setPaymentError('');

              const response = await fetch(
                '/api/bts/paypal/create-order',
                {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({
                    customerEmail,
                    removalMode,
                    pathname,
                  }),
                }
              );

              const data = await response
                .json()
                .catch(() => ({}));

              if (!response.ok || !data.orderId) {
                throw new Error(
                  data.error ||
                    'Unable to start BTS PayPal checkout.'
                );
              }

              return data.orderId;
            },

            onApprove: async (data) => {
              setPaymentError('');

              const response = await fetch(
                '/api/bts/paypal/capture-order',
                {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({
                    orderId: data.orderID,
                    customerEmail,
                    removalMode,
                    pathname,
                  }),
                }
              );

              const result = await response
                .json()
                .catch(() => ({}));

              if (
                !response.ok ||
                !result.success ||
                !result.jobToken
              ) {
                throw new Error(
                  result.error ||
                    'Unable to verify the BTS payment.'
                );
              }

              setUnlockMethod('paypal');
              setPaymentCompleted(true);

              if (
                typeof onPaymentCompleted === 'function'
              ) {
                onPaymentCompleted({
                  orderId: data.orderID,
                  jobToken: result.jobToken,
                  unlockMethod: 'paypal',
                });
              }
            },

            onCancel: () => {
              setPaymentError(
                'Checkout was cancelled. You have not been charged.'
              );

              if (
                typeof onPaymentCancelled === 'function'
              ) {
                onPaymentCancelled();
              }
            },

            onError: (error) => {
              console.error(
                'BTS PayPal checkout error:',
                error
              );

              setPaymentError(
                error instanceof Error
                  ? error.message
                  : 'BTS PayPal checkout could not be completed.'
              );

              if (
                typeof onPaymentError === 'function'
              ) {
                onPaymentError(error);
              }
            },
          })
          .render(containerRef.current);
      } catch (error) {
        console.error(
          'Unable to render BTS PayPal buttons:',
          error
        );

        setPaymentError(
          error instanceof Error
            ? error.message
            : 'Unable to load BTS PayPal checkout.'
        );

        setIsLoading(false);
      }
    }

    function loadPayPalScript() {
      if (window.paypal) {
        renderPayPalButtons();
        return;
      }

      const existingScript =
        document.getElementById(PAYPAL_SCRIPT_ID);

      if (existingScript) {
        existingScript.addEventListener(
          'load',
          renderPayPalButtons,
          { once: true }
        );
        return;
      }

      const script = document.createElement('script');

      script.id = PAYPAL_SCRIPT_ID;
      script.src =
        `https://www.paypal.com/sdk/js` +
        `?client-id=${encodeURIComponent(clientId)}` +
        `&currency=USD&intent=capture`;
      script.async = true;
      script.onload = renderPayPalButtons;

      script.onerror = () => {
        if (!isCancelled) {
          setPaymentError(
            'Unable to load BTS PayPal checkout. You can still use a valid BTS token.'
          );
          setIsLoading(false);
        }
      };

      document.body.appendChild(script);
    }

    loadPayPalScript();

    return () => {
      isCancelled = true;
    };
  }, [
    customerEmail,
    removalMode,
    pathname,
    onPaymentCompleted,
    onPaymentCancelled,
    onPaymentError,
  ]);

  const handleFreeTokenUnlock = async () => {
    if (isRedeemingToken || paymentCompleted) return;

    const normalizedToken = freeTokenCode
      .trim()
      .toUpperCase();

    if (!normalizedToken) {
      setTokenErrorTitle('Token Required');
      setTokenError('Enter your free BTS token code before continuing.');
      setTokenUsesRemaining(null);
      return;
    }

    setIsRedeemingToken(true);
    setTokenError('');
    setTokenErrorTitle('');
    setTokenUsesRemaining(null);

    try {
      const response = await fetch(
        '/api/bts/free-token',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            tokenCode: normalizedToken,
            customerEmail,
            removalMode,
            pathname,
          }),
        }
      );

      const result = await response
        .json()
        .catch(() => ({}));

      if (
        !response.ok ||
        !result.success ||
        !result.unlocked ||
        !result.jobToken
      ) {
        setTokenErrorTitle(
          TOKEN_ERROR_TITLES[result.code] || 'Invalid Token'
        );
        setTokenError(
          result.error ||
            result.message ||
            'This BTS token could not be used.'
        );
        throw new Error(
          result.error ||
            result.message ||
            'This BTS token could not be used.'
        );
      }

      setUnlockMethod('free-token');
      setTokenUsesRemaining(
        result.usesRemaining ?? null
      );
      setFreeTokenCode('');
      setTokenError('');
      setTokenErrorTitle('');
      setPaymentError('');
      setPaymentCompleted(true);

      if (
        typeof onPaymentCompleted === 'function'
      ) {
        onPaymentCompleted({
          orderId: result.orderId || result.tokenId,
          jobToken: result.jobToken,
          unlockMethod: 'free-token',
          usesRemaining: result.usesRemaining ?? null,
        });
      }
    } catch (error) {
      console.error('BTS free token error:', error);
    } finally {
      setIsRedeemingToken(false);
    }
  };

  if (paymentCompleted) {
    return (
      <div className="rounded-xl border border-green-500/40 bg-green-500/10 p-4 text-center">
        <p className="font-bold text-green-400">
          {unlockMethod === 'free-token'
            ? '✓ Free BTS token accepted'
            : '✓ $1.00 payment completed'}
        </p>
        <p className="mt-1 text-sm text-zinc-400">
          Your backing track is being prepared.
        </p>
        {unlockMethod === 'free-token' && tokenUsesRemaining !== null && (
          <p className="mt-2 text-xs text-zinc-500">
            Token uses remaining: {tokenUsesRemaining}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="space-y-3">
        {isLoading && (
          <p className="text-center text-sm text-zinc-400">
            Loading secure PayPal checkout…
          </p>
        )}

        <div ref={containerRef} />

        {paymentError && (
          <p className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">
            {paymentError}
          </p>
        )}

        <p className="text-center text-xs text-zinc-500">
          USD $1.00 per backing track.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <div className="h-px flex-1 bg-zinc-800" />
        <span className="text-xs font-bold uppercase tracking-wider text-zinc-600">
          or
        </span>
        <div className="h-px flex-1 bg-zinc-800" />
      </div>

      <div className="rounded-xl border border-green-500/20 bg-green-500/5 p-4">
        <button
          type="button"
          onClick={() => {
            setShowTokenEntry((current) => !current);
            setTokenError('');
            setTokenErrorTitle('');
          }}
          className="w-full text-left"
        >
          <p className="font-bold text-green-300">
            Have a free BTS token?
          </p>
          <p className="mt-1 text-xs text-zinc-500">
            Use a Backing Track Studio token instead of PayPal.
          </p>
        </button>

        {showTokenEntry && (
          <div className="mt-4 space-y-3">
            <input
              type="text"
              value={freeTokenCode}
              onChange={(event) => {
                setFreeTokenCode(event.target.value.toUpperCase());
                setTokenError('');
                setTokenErrorTitle('');
              }}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  event.preventDefault();
                  handleFreeTokenUnlock();
                }
              }}
              maxLength={40}
              autoComplete="off"
              placeholder="BTS-XXXX-XXXX-XXXX"
              className="w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-3 font-mono text-sm uppercase text-white outline-none placeholder:text-zinc-700 focus:border-green-500"
            />

            {tokenError && (
              <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">
                {tokenErrorTitle && (
                  <p className="font-bold">{tokenErrorTitle}</p>
                )}
                <p className={tokenErrorTitle ? 'mt-1 text-xs' : ''}>
                  {tokenError}
                </p>
              </div>
            )}

            <button
              type="button"
              onClick={handleFreeTokenUnlock}
              disabled={isRedeemingToken || !freeTokenCode.trim()}
              className="w-full rounded-lg bg-green-600 px-4 py-3 font-black text-white transition hover:bg-green-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isRedeemingToken
                ? 'Checking token…'
                : 'Use Free BTS Token'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
