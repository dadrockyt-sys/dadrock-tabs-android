from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f'Missing expected block: {label}')
    return text.replace(old, new, 1)


# 1. Repair the checkout props and remove the duplicate capture in app/ai-tab/page.js.
page_path = Path('app/ai-tab/page.js')
page = page_path.read_text()

old_handler_start = """  const handlePaymentApproved =
    async (orderId) => {
      setGenerationError('');

      setStatusMessage(
        'Confirming your PayPal payment...'
      );

      try {
        if (!orderId) {
          throw new Error(
            'PayPal did not return an order ID.'
          );
        }

        const response = await fetch(
          '/api/paypal/capture-order',
          {
            method: 'POST',

            headers: {
              'Content-Type':
                'application/json',
            },

            body: JSON.stringify({
              orderId,

              songTitle:
                songTitle.trim(),

              artistName:
                artistName.trim(),

              transcriptionType:
                selectedType,

              customerEmail:
                customerEmail.trim(),

              amount: PRICE,
            }),
          }
        );

        const data = await response
          .json()
          .catch(() => ({}));

        if (!response.ok) {
          throw new Error(
            data.error ||
              data.message ||
              'Unable to confirm your PayPal payment.'
          );
        }

        const paymentStatus =
          data.status ||
          data.captureStatus ||
          '';

        const acceptedStatuses = [
          'COMPLETED',
          'APPROVED',
          'SUCCESS',
        ];

        if (
          paymentStatus &&
          !acceptedStatuses.includes(
            String(
              paymentStatus
            ).toUpperCase()
          )
        ) {
          throw new Error(
            'PayPal has not marked this payment as completed.'
          );
        }

        setPurchaseOrderId(
          orderId
        );

        setPaymentCompleted(
          true
        );

        setPreviewUnlocked(
          true
        );

        setUsingFreeToken(
          false
        );

        setStatusMessage(
          'Payment confirmed. Your full PDF is now unlocked.'
        );

        window.setTimeout(() => {
          document
            .getElementById(
              'download-section'
            )
            ?.scrollIntoView({
              behavior: 'smooth',
              block: 'start',
            });
        }, 150);
      } catch (error) {
        console.error(
          'PayPal capture error:',
          error
        );

        setPaymentCompleted(
          false
        );

        setPreviewUnlocked(
          false
        );

        setGenerationError(
          error instanceof Error
            ? error.message
            : 'Unable to confirm your PayPal payment.'
        );

        setStatusMessage('');
      }
    };
"""

new_handler = """  const handlePaymentApproved =
    ({ orderId } = {}) => {
      setGenerationError('');

      if (!orderId) {
        setPaymentCompleted(false);
        setPreviewUnlocked(false);
        setStatusMessage('');
        setGenerationError(
          'PayPal did not return an order ID.'
        );
        return;
      }

      setPurchaseOrderId(orderId);
      setPaymentCompleted(true);
      setPreviewUnlocked(true);
      setUsingFreeToken(false);
      setStatusMessage(
        'Payment confirmed. Your full PDF is now unlocked.'
      );

      window.setTimeout(() => {
        document
          .getElementById('download-section')
          ?.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          });
      }, 150);
    };
"""
page = replace_once(page, old_handler_start, new_handler, 'PayPal approval handler')

old_checkout = """                        <PayPalCheckoutButton
                          amount={PRICE}
                          description={`${artistName} - ${songTitle} ${selectedTypeDetails?.title || 'Tab'} PDF`}
                          onApproved={
                            handlePaymentApproved
                          }
                          onCancelled={
                            handlePaymentCancelled
                          }
                          onError={
                            handlePaymentError
                          }
                        />
"""
new_checkout = """                        <PayPalCheckoutButton
                          song={songTitle.trim()}
                          artist={artistName.trim()}
                          transcriptionType={selectedType}
                          customerEmail={customerEmail.trim()}
                          onPaymentCompleted={handlePaymentApproved}
                          onPaymentCancelled={handlePaymentCancelled}
                          onPaymentError={handlePaymentError}
                        />
"""
page = replace_once(page, old_checkout, new_checkout, 'PayPal component props')

page = page.replace('''              songTitle:\n                songTitle.trim(),\n\n              artistName:\n                artistName.trim(),''', '''              song:\n                songTitle.trim(),\n\n              artist:\n                artistName.trim(),''', 1)

page_path.write_text(page)


# 2. Repair component callbacks and use CAD consistently.
component_path = Path('components/PayPalCheckoutButton.js')
component = component_path.read_text()
component = replace_once(
    component,
    '  onPaymentCompleted,\n}) {',
    '  onPaymentCompleted,\n  onPaymentCancelled,\n  onPaymentError,\n}) {',
    'checkout callback props',
)
component = component.replace('&currency=USD&intent=capture', '&currency=CAD&intent=capture')
component = replace_once(
    component,
    """            onCancel: () => {
              setPaymentError(
                'Checkout was cancelled. You have not been charged.'
              );
            },
""",
    """            onCancel: () => {
              setPaymentError(
                'Checkout was cancelled. You have not been charged.'
              );
              if (typeof onPaymentCancelled === 'function') {
                onPaymentCancelled();
              }
            },
""",
    'PayPal cancel callback',
)
component = replace_once(
    component,
    """              setPaymentError(
                error instanceof Error
                  ? error.message
                  : 'PayPal checkout could not be completed.'
              );
""",
    """              setPaymentError(
                error instanceof Error
                  ? error.message
                  : 'PayPal checkout could not be completed.'
              );
              if (typeof onPaymentError === 'function') {
                onPaymentError(error);
              }
""",
    'PayPal error callback',
)
component = component.replace(
    '  onPaymentCompleted,\n]);',
    '  onPaymentCompleted,\n  onPaymentCancelled,\n  onPaymentError,\n]);',
)
component_path.write_text(component)


# 3. Use CAD in both PayPal server routes.
for route in [
    Path('app/api/paypal/create-order/route.js'),
    Path('app/api/paypal/capture-order/route.js'),
]:
    text = route.read_text().replace("const CURRENCY = 'USD';", "const CURRENCY = 'CAD';")
    route.write_text(text)


# 4. Permit securely redeemed free tokens in the finished-PDF route.
pdf_path = Path('app/api/generate-tab-pdf/route.js')
pdf = pdf_path.read_text()
pdf = replace_once(
    pdf,
    "import { createTabPdf } from '@/lib/createTabPdf';\n",
    "import { createTabPdf } from '@/lib/createTabPdf';\nimport { getDb } from '@/lib/mongodb';\n",
    'MongoDB import',
)
pdf = pdf.replace("const CURRENCY = 'USD';", "const CURRENCY = 'CAD';")

insert_before = 'export async function POST(request) {'
verification_helper = """async function verifyFreeToken({
  tokenReference,
  customerEmail,
  song,
  artist,
  transcriptionType,
}) {
  const db = await getDb();
  const token = await db.collection('tab_tokens').findOne({
    code: tokenReference,
    assignedEmail: customerEmail,
    redemptions: {
      $elemMatch: {
        customerEmail,
        songTitle: song,
        artistName: artist,
        transcriptionType,
      },
    },
  });

  if (!token) {
    throw new Error('Free token redemption could not be verified.');
  }
}

"""
pdf = replace_once(pdf, insert_before, verification_helper + insert_before, 'free-token verification helper')

pdf = replace_once(
    pdf,
    """    const orderId = cleanText(body?.orderId, 40);
    const song = cleanText(body?.song, 120);
""",
    """    const orderId = cleanText(body?.orderId, 40);
    const tokenReference = cleanText(body?.tokenReference, 100);
    const unlockMethod = cleanText(body?.unlockMethod, 20).toLowerCase();
    const song = cleanText(body?.song, 120);
""",
    'unlock request fields',
)

pdf = replace_once(
    pdf,
    """      !orderId ||
      !song ||
""",
    """      (!orderId && !tokenReference) ||
      !song ||
""",
    'required unlock reference',
)
pdf = pdf.replace(
    "'Order ID, song, artist, transcription type, tab, and customer email are required.'",
    "'An unlock reference, song, artist, transcription type, tab, and customer email are required.'",
)

old_validation = """    if (!/^[A-Z0-9]+$/i.test(orderId)) {
      return NextResponse.json(
        { error: 'Invalid PayPal order ID.' },
        { status: 400 }
      );
    }

"""
new_validation = """    if (
      unlockMethod === 'paypal' &&
      !/^[A-Z0-9]+$/i.test(orderId)
    ) {
      return NextResponse.json(
        { error: 'Invalid PayPal order ID.' },
        { status: 400 }
      );
    }

    if (!['paypal', 'free-token'].includes(unlockMethod)) {
      return NextResponse.json(
        { error: 'Invalid PDF unlock method.' },
        { status: 400 }
      );
    }

"""
pdf = replace_once(pdf, old_validation, new_validation, 'unlock validation')

old_verify = """    await verifyPayPalOrder({
      orderId,
      song,
      artist,
      transcriptionType,
    });
"""
new_verify = """    if (unlockMethod === 'paypal') {
      await verifyPayPalOrder({
        orderId,
        song,
        artist,
        transcriptionType,
      });
    } else {
      await verifyFreeToken({
        tokenReference,
        customerEmail,
        song,
        artist,
        transcriptionType,
      });
    }
"""
pdf = replace_once(pdf, old_verify, new_verify, 'unlock verification branch')
pdf_path.write_text(pdf)

print('AI Tab unlock repair applied successfully.')
