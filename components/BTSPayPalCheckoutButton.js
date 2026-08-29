'use client';

import { useEffect, useRef, useState } from 'react';

const PAYPAL_SCRIPT_ID = 'dadrock-paypal-sdk';

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

  useEffect(() => {
    let isCancelled = false;

    const clientId =
      process.env.NEXT_PUBLIC_PAYPAL_SANDBOX_CLIENT_ID ||
      process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID;

    if (!clientId) {
      setPaymentError('PayPal sandbox is not configured.');
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
                    'Unable to verify the BTS sandbox payment.'
                );
              }

              setPaymentCompleted(true);

              if (
                typeof onPaymentCompleted === 'function'
              ) {
                onPaymentCompleted({
                  orderId: data.orderID,
                  jobToken: result.jobToken,
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
            'Unable to load BTS PayPal checkout.'
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

  if (paymentCompleted) {
    return (
      <div className="rounded-xl border border-green-500/40 bg-green-500/10 p-4 text-center">
        <p className="font-bold text-green-400">
          ✓ $1.00 sandbox payment completed
        </p>
        <p className="mt-1 text-sm text-zinc-400">
          Your backing track is being prepared.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {isLoading && (
        <p className="text-center text-sm text-zinc-400">
          Loading secure PayPal sandbox checkout…
        </p>
      )}

      <div ref={containerRef} />

      {paymentError && (
        <p className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">
          {paymentError}
        </p>
      )}

      <p className="text-center text-xs text-zinc-500">
        Testing price: USD $1.00 — PayPal sandbox only.
      </p>
    </div>
  );
}
