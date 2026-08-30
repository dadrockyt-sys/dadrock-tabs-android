import {
  createHash,
  createHmac,
  timingSafeEqual,
} from 'node:crypto';

export const BTS_PRICE = '1.00';
export const BTS_CURRENCY = 'USD';

export const BTS_REMOVAL_MODES = [
  'guitar',
  'bass',
  'guitar-bass',
];

export const BTS_PAYPAL_BASE_URL =
  'https://api-m.paypal.com';

export function cleanBtsText(value, maximumLength = 160) {
  return String(value || '')
    .trim()
    .replace(/\s+/g, ' ')
    .slice(0, maximumLength);
}

export function isValidBtsEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
    String(value || '').trim()
  );
}

export function isValidBtsPathname(value) {
  const pathname = cleanBtsText(value, 500);

  return (
    pathname.startsWith('bts-audio/') &&
    !pathname.includes('..')
  );
}

export function createBtsPurchaseFingerprint({
  customerEmail,
  removalMode,
  pathname,
}) {
  const purchaseData = [
    cleanBtsText(customerEmail, 254).toLowerCase(),
    cleanBtsText(removalMode, 40).toLowerCase(),
    cleanBtsText(pathname, 500),
    BTS_PRICE,
    BTS_CURRENCY,
  ].join('|');

  return createHash('sha256')
    .update(purchaseData)
    .digest('hex');
}

export async function getBtsPayPalAccessToken() {
  const clientId =
    process.env.NEXT_PUBLIC_BTS_PAYPAL_CLIENT_ID;

  const clientSecret =
    process.env.BTS_PAYPAL_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    throw new Error(
      'BTS live PayPal credentials are not configured.'
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
      'Unable to authenticate with PayPal.'
    );
  }

  return data.access_token;
}

function getJobSigningSecret() {
  const secret =
    process.env.BTS_JOB_SIGNING_SECRET ||
    process.env.BTS_PAYPAL_CLIENT_SECRET ||
    process.env.PAYPAL_CLIENT_SECRET;

  if (!secret) {
    throw new Error(
      'BTS job signing is not configured.'
    );
  }

  return secret;
}

function hashEmail(email) {
  return createHash('sha256')
    .update(cleanBtsText(email, 254).toLowerCase())
    .digest('hex');
}

function signatureFor(encodedPayload) {
  return createHmac('sha256', getJobSigningSecret())
    .update(encodedPayload)
    .digest('base64url');
}

export function createBtsJobToken({
  orderId,
  customerEmail,
  removalMode,
  pathname,
}) {
  const now = Math.floor(Date.now() / 1000);

  const payload = {
    v: 1,
    orderId: cleanBtsText(orderId, 80),
    emailHash: hashEmail(customerEmail),
    removalMode: cleanBtsText(
      removalMode,
      40
    ).toLowerCase(),
    pathname: cleanBtsText(pathname, 500),
    iat: now,
    exp: now + 6 * 60 * 60,
  };

  const encodedPayload = Buffer.from(
    JSON.stringify(payload)
  ).toString('base64url');

  return `${encodedPayload}.${signatureFor(
    encodedPayload
  )}`;
}

export function verifyBtsJobToken(
  token,
  {
    orderId,
    customerEmail,
    removalMode,
    pathname,
  }
) {
  const [encodedPayload, suppliedSignature] =
    String(token || '').split('.');

  if (!encodedPayload || !suppliedSignature) {
    return false;
  }

  const expectedSignature =
    signatureFor(encodedPayload);

  const suppliedBuffer = Buffer.from(
    suppliedSignature
  );
  const expectedBuffer = Buffer.from(
    expectedSignature
  );

  if (
    suppliedBuffer.length !== expectedBuffer.length ||
    !timingSafeEqual(
      suppliedBuffer,
      expectedBuffer
    )
  ) {
    return false;
  }

  let payload;

  try {
    payload = JSON.parse(
      Buffer.from(
        encodedPayload,
        'base64url'
      ).toString('utf8')
    );
  } catch {
    return false;
  }

  const now = Math.floor(Date.now() / 1000);

  return (
    payload?.v === 1 &&
    Number(payload?.exp || 0) >= now &&
    payload?.orderId ===
      cleanBtsText(orderId, 80) &&
    payload?.emailHash ===
      hashEmail(customerEmail) &&
    payload?.removalMode ===
      cleanBtsText(
        removalMode,
        40
      ).toLowerCase() &&
    payload?.pathname ===
      cleanBtsText(pathname, 500)
  );
}
