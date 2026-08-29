import { createHash } from 'node:crypto';

export const BTS_PRICE = '1.00';
export const BTS_CURRENCY = 'USD';
export const BTS_PAYPAL_BASE_URL =
  'https://api-m.sandbox.paypal.com';

export const BTS_REMOVAL_MODES = [
  'guitars',
  'bass',
  'both',
];

export function cleanBtsText(value, maximumLength) {
  return String(value || '')
    .trim()
    .replace(/\s+/g, ' ')
    .slice(0, maximumLength);
}

export function normalizeBtsRemovalMode(value) {
  return cleanBtsText(value, 20).toLowerCase();
}

export function isValidBtsRemovalMode(value) {
  return BTS_REMOVAL_MODES.includes(
    normalizeBtsRemovalMode(value)
  );
}

export function isValidBtsAudioPathname(value) {
  const pathname = cleanBtsText(value, 1000);

  return (
    pathname.startsWith('bts-audio/') &&
    !pathname.includes('..')
  );
}

export function createBtsPurchaseFingerprint({
  pathname,
  removalMode,
}) {
  const purchaseData = [
    cleanBtsText(pathname, 1000),
    normalizeBtsRemovalMode(removalMode),
    BTS_PRICE,
    BTS_CURRENCY,
  ].join('|');

  return createHash('sha256')
    .update(purchaseData)
    .digest('hex');
}

export function createBtsCustomId({
  pathname,
  removalMode,
}) {
  return `bts-${createBtsPurchaseFingerprint({
    pathname,
    removalMode,
  })}`;
}

export function getBtsRemovalLabel(removalMode) {
  const normalized =
    normalizeBtsRemovalMode(removalMode);

  if (normalized === 'guitars') {
    return 'Remove Guitars';
  }

  if (normalized === 'bass') {
    return 'Remove Bass';
  }

  if (normalized === 'both') {
    return 'Remove Guitars + Bass';
  }

  return 'Backing Track';
}

export async function getBtsPayPalAccessToken() {
  const clientId =
    process.env.PAYPAL_SANDBOX_CLIENT_ID ||
    process.env.NEXT_PUBLIC_PAYPAL_SANDBOX_CLIENT_ID ||
    process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID;

  const clientSecret =
    process.env.PAYPAL_SANDBOX_CLIENT_SECRET ||
    process.env.PAYPAL_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    throw new Error(
      'PayPal sandbox credentials are not configured.'
    );
  }

  const credentials = Buffer.from(
    `${clientId}:${clientSecret}`
  ).toString('base64');

  const response = await fetch(
    `${BTS_PAYPAL_BASE_URL}/v1/oauth2/token`,
    {
      method: 'POST',
      headers: {
        Authorization: `Basic ${credentials}`,
        'Content-Type':
          'application/x-www-form-urlencoded',
      },
      body: 'grant_type=client_credentials',
      cache: 'no-store',
    }
  );

  const data = await response.json();

  if (!response.ok || !data.access_token) {
    console.error('BTS PayPal token error:', data);

    throw new Error(
      'Unable to authenticate with PayPal sandbox.'
    );
  }

  return data.access_token;
}

export function verifyBtsCompletedOrder(
  data,
  { pathname, removalMode }
) {
  const purchaseUnit = data?.purchase_units?.[0];
  const capture =
    purchaseUnit?.payments?.captures?.[0];

  const expectedCustomId = createBtsCustomId({
    pathname,
    removalMode,
  });

  const valid =
    data?.status === 'COMPLETED' &&
    capture?.status === 'COMPLETED' &&
    capture?.amount?.currency_code ===
      BTS_CURRENCY &&
    capture?.amount?.value === BTS_PRICE &&
    purchaseUnit?.custom_id === expectedCustomId;

  return {
    valid,
    purchaseUnit,
    capture,
    expectedCustomId,
  };
}

export async function fetchBtsPayPalOrder(orderId) {
  const cleanOrderId = cleanBtsText(
    orderId,
    40
  );

  if (!/^[A-Z0-9]+$/i.test(cleanOrderId)) {
    throw new Error('Invalid PayPal order ID.');
  }

  const accessToken =
    await getBtsPayPalAccessToken();

  const response = await fetch(
    `${BTS_PAYPAL_BASE_URL}/v2/checkout/orders/${cleanOrderId}`,
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    }
  );

  const data = await response.json();

  if (!response.ok) {
    console.error(
      'BTS PayPal order lookup error:',
      data
    );

    throw new Error(
      'Unable to verify the PayPal sandbox order.'
    );
  }

  return data;
}
