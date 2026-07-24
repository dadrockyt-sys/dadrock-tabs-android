'use client';

import { useEffect, useRef, useState } from 'react';

const PAYPAL_SCRIPT_ID = 'dadrock-paypal-sdk';

export default function PayPalCheckoutButton({
  song,
  artist,
  transcriptionType,
  onPaymentCompleted,
}) {
  const containerRef = useRef(null);
  const hasRenderedRef = useRef(false);

  const [isLoading, setIsLoading] = useState(true);
  const [paymentError, setPaymentError] = useState('');
  const [paymentCompleted, setPaymentCompleted] = useState(false);

  useEffect(() => {
    let isCancelled = false;

    const clientId = process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID;

    if (!clientId) {
      setPaymentError('PayPal is not configured.');
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

              const response = await fetch('/api/paypal/create-order', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  song,
                  artist,
                  transcriptionType,
                }),
              });

              const data = await response.json();

              if (!response.ok || !data.orderId) {
                throw new Error(
                  data.error || 'Unable to start PayPal checkout.'
                );
              }

              return data.orderId;
            },

            onApprove: async (data) => {
              setPaymentError('');

              const response = await fetch('/api/paypal/capture-order', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  orderId: data.orderID,
                }),
              });

              const result = await response.json();

              if (!response.ok || !result.success) {
                throw new Error(
                  result.error || 'Unable to complete the payment.'
                );
              }

              setPaymentCompleted(true);

              if (typeof onPaymentCompleted === 'function') {
                onPaymentCompleted(result);
              }
            },

            onCancel: () => {
              setPaymentError(
                'Checkout was cancelled. You have not been charged.'
              );
            },

            onError: (error) => {
              console.error('PayPal checkout error:', error);

              setPaymentError(
                error instanceof Error
                  ? error.message
                  : 'PayPal checkout could not be completed.'
              );
            },
          })
          .render(containerRef.current);
      } catch (error) {
        console.error('Unable to render PayPal buttons:', error);

        setPaymentError(
          error instanceof Error
            ? error.message
            : 'Unable to load PayPal checkout.'
        );

        setIsLoading(false);
      }
    }

    function loadPayPalScript() {
      if (window.paypal) {
        renderPayPalButtons();
        return;
      }

      const existingScript = document.getElementById(PAYPAL_SCRIPT_ID);

      if (existingScript) {
        existingScript.addEventListener('load', renderPayPalButtons, {
          once: true,
        });

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
          setPaymentError('Unable to load PayPal checkout.');
          setIsLoading(false);
        }
      };

      document.body.appendChild(script);
    }

    loadPayPalScript();

    return () => {
      isCancelled = true;
    };
  }, [song, artist, transcriptionType, onPaymentCompleted]);

  if (paymentCompleted) {
    return (
      <div className="rounded-xl border border-green-500/40 bg-green-500/10 p-4 text-center">
        <p className="font-bold text-green-400">
          ✓ Sandbox payment completed
        </p>

        <p className="mt-1 text-sm text-zinc-400">
          Your printable PDF is now unlocked.
        </p>
      </div>
    );
  }

  return (
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
        Sandbox test payment — no real money will be charged.
      </p>
    </div>
  );
}
