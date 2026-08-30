import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const failures = [];
const passes = [];

function read(relativePath) {
  return fs.readFileSync(
    path.join(root, relativePath),
    'utf8'
  );
}

function check(label, condition) {
  if (condition) {
    passes.push(label);
    console.log(`PASS ${label}`);
    return;
  }

  failures.push(label);
  console.error(`FAIL ${label}`);
}

function includesAll(content, values) {
  return values.every((value) =>
    content.includes(value)
  );
}

const page = read('app/bts/page.js');
const uploadRoute = read(
  'app/api/bts/audio-upload/route.js'
);
const payment = read('lib/btsPayment.js');
const createOrder = read(
  'app/api/bts/paypal/create-order/route.js'
);
const captureOrder = read(
  'app/api/bts/paypal/capture-order/route.js'
);
const processRoute = read(
  'app/api/bts/process/route.js'
);
const cleanupRoute = read(
  'app/api/bts/cleanup/route.js'
);
const freeTokenRoute = read(
  'app/api/bts/free-token/route.js'
);
const btsTokenAdminRoute = read(
  'app/api/admin/bts-tokens/route.js'
);
const btsTokenAdminPage = read(
  'app/admin/bts-tokens/page.js'
);
const aiTokenRoute = read(
  'app/api/free-tab-token/route.js'
);
const aiTokenAdminRoute = read(
  'app/api/admin/tab-tokens/route.js'
);
const paypalButton = read(
  'components/BTSPayPalCheckoutButton.js'
);
const worker = read(
  'analyzer/modal_bts_separator.py'
);
const workerRequirements = read(
  'analyzer/bts-audio-separation-requirements.txt'
);
const vercel = JSON.parse(read('vercel.json'));

check(
  'BTS route uses the BTS logo',
  page.includes("const LOGO_URL = '/dadrock-tabs-bts-logo.png'")
);

check(
  'BTS page exposes all three frozen removal modes',
  includesAll(page, [
    "value: 'guitar'",
    "value: 'bass'",
    "value: 'guitar-bass'",
  ])
);

check(
  'BTS page uses private BTS upload and processing routes',
  includesAll(page, [
    "access: 'private'",
    "'/api/bts/audio-upload'",
    "'/api/bts/process'",
  ])
);

check(
  'BTS page price is fixed to 1.00',
  page.includes("const PRICE = '1.00'")
);

check(
  'BTS customer UI no longer presents sandbox state',
  !page.toLowerCase().includes('sandbox') &&
    !paypalButton.toLowerCase().includes('sandbox')
);

check(
  'BTS email format verification matches AI-tab semantics',
  page.includes('/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/') &&
    uploadRoute.includes('isValidBtsEmail')
);

check(
  'BTS upload is isolated to bts-audio namespace',
  uploadRoute.includes("pathname.startsWith('bts-audio/')") &&
    uploadRoute.includes('maximumSizeInBytes: 50 * 1024 * 1024')
);

check(
  'BTS upload requires rights confirmation',
  uploadRoute.includes('!payload.copyrightConfirmed')
);

check(
  'BTS payment is live, isolated, and server-fixed to USD 1.00',
  includesAll(payment, [
    "export const BTS_PRICE = '1.00'",
    "export const BTS_CURRENCY = 'USD'",
    "https://api-m.paypal.com",
    'process.env.NEXT_PUBLIC_BTS_PAYPAL_CLIENT_ID',
    'process.env.BTS_PAYPAL_CLIENT_SECRET',
  ]) &&
    !payment.includes('api-m.sandbox.paypal.com') &&
    !payment.includes('PAYPAL_SANDBOX_')
);

check(
  'BTS payment modes agree across shared contract',
  includesAll(payment, [
    "'guitar'",
    "'bass'",
    "'guitar-bass'",
  ])
);

check(
  'BTS create order binds a BTS purchase fingerprint',
  includesAll(createOrder, [
    'createBtsPurchaseFingerprint',
    "reference_id: 'dadrock-bts'",
    'custom_id: `bts-${fingerprint}`',
    "environment: 'live'",
  ]) &&
    !createOrder.includes('sandbox: true')
);

check(
  'BTS capture verifies exact price/currency/fingerprint',
  includesAll(captureOrder, [
    "data.status === 'COMPLETED'",
    "capture?.status === 'COMPLETED'",
    'capture?.amount?.currency_code === BTS_CURRENCY',
    'capture?.amount?.value === BTS_PRICE',
    'purchaseUnit?.custom_id === expectedCustomId',
    "environment: 'live'",
  ]) &&
    !captureOrder.includes('sandbox: true')
);

check(
  'BTS capture issues a signed paid-job token',
  captureOrder.includes('createBtsJobToken') &&
    payment.includes("createHmac('sha256'") &&
    payment.includes('exp: now + 6 * 60 * 60')
);

check(
  'BTS process verifies signed job and resolves Blob server-side',
  includesAll(processRoute, [
    'verifyBtsJobToken',
    'await head(pathname',
    'process.env.BTS_SEPARATOR_API_URL',
    'process.env.BTS_SEPARATOR_API_TOKEN',
  ])
);

check(
  'BTS process streams generated audio without persistent storage',
  processRoute.includes('return new Response(separatorResponse.body') &&
    processRoute.includes("'Cache-Control':\n          'private, no-store, max-age=0'")
);

check(
  'BTS successful source is deleted while failures remain retryable',
  includesAll(processRoute, [
    'let processingSucceeded = false',
    'processingSucceeded = true',
    'processingSucceeded &&',
    'retryable: true',
  ])
);

check(
  'BTS cleanup is restricted to BTS audio and under 24-hour maximum',
  includesAll(cleanupRoute, [
    "const BTS_AUDIO_PREFIX = 'bts-audio/'",
    'const CLEANUP_THRESHOLD_MS = 23 * 60 * 60 * 1000',
    'CRON_SECRET',
  ])
);

check(
  'Vercel keeps daily sync and adds hourly BTS cleanup cron',
  Array.isArray(vercel.crons) &&
    vercel.crons.some(
      (cron) =>
        cron.path === '/api/cron/daily-sync' &&
        cron.schedule === '0 6 * * *'
    ) &&
    vercel.crons.some(
      (cron) =>
        cron.path === '/api/bts/cleanup' &&
        cron.schedule === '0 * * * *'
    )
);

check(
  'BTS PayPal UI uses dedicated BTS live checkout endpoints and client ID',
  includesAll(paypalButton, [
    "'/api/bts/paypal/create-order'",
    "'/api/bts/paypal/capture-order'",
    'NEXT_PUBLIC_BTS_PAYPAL_CLIENT_ID',
  ]) &&
    !paypalButton.includes('NEXT_PUBLIC_PAYPAL_CLIENT_ID') &&
    !paypalButton.includes('NEXT_PUBLIC_PAYPAL_SANDBOX_CLIENT_ID')
);

check(
  'BTS checkout exposes a complimentary token alternative',
  includesAll(paypalButton, [
    "'/api/bts/free-token'",
    'Have a free BTS token?',
    'BTS-XXXX-XXXX-XXXX',
    "unlockMethod: 'free-token'",
  ])
);

check(
  'BTS free tokens are structurally isolated from AI Tab tokens',
  freeTokenRoute.includes("db.collection('bts_tokens')") &&
    freeTokenRoute.includes('^BTS-') &&
    !freeTokenRoute.includes("db.collection('tab_tokens')") &&
    aiTokenRoute.includes("db.collection('tab_tokens')") &&
    aiTokenRoute.includes('^DRT-')
);

check(
  'BTS token redemption mirrors AI Tab use accounting',
  includesAll(freeTokenRoute, [
    'active: true',
    'usesRemaining: { $gt: 0 }',
    '$inc: { usesRemaining: -1 }',
    '$push: { redemptions: redemption }',
    "'TOKEN_EMAIL_MISMATCH'",
    "'TOKEN_EXPIRED'",
    'createBtsJobToken',
  ])
);

check(
  'BTS token admin uses a separate collection and AI token admin stays unchanged',
  btsTokenAdminRoute.includes("db.collection('bts_tokens')") &&
    btsTokenAdminRoute.includes('BTS-${value.slice(0, 4)}') &&
    !btsTokenAdminRoute.includes("db.collection('tab_tokens')") &&
    aiTokenAdminRoute.includes("db.collection('tab_tokens')") &&
    aiTokenAdminRoute.includes('DRT-${raw.slice(0, 4)}')
);

check(
  'BTS token admin supports AI-style creator and tracker controls',
  includesAll(btsTokenAdminPage, [
    'Uses Per Token',
    'Assigned Email (optional)',
    'Expiration (optional)',
    'Notes (optional)',
    'Generate BTS Tokens',
    'BTS Token Tracker',
    'Redemption History',
    "tokenAction(token._id, 'toggle'",
    "tokenAction(token._id, 'delete')",
  ])
);

check(
  'BTS worker is genuine six-source waveform separation',
  includesAll(worker, [
    'htdemucs_6s.yaml',
    'EXPECTED_STEMS',
    '"guitar"',
    '"bass"',
    'rebuild_backing_track',
  ])
);

check(
  'BTS worker is CPU-only and does not request Modal GPU',
  worker.includes('audio-separator[cpu]==0.30.2') &&
    worker.includes('"CUDA_VISIBLE_DEVICES": ""') &&
    !worker.includes('gpu="') &&
    !worker.includes("gpu='") &&
    workerRequirements.includes('audio-separator[cpu]==0.30.2') &&
    !workerRequirements.includes('[gpu]')
);

check(
  'BTS worker validates private Vercel Blob identity',
  includesAll(worker, [
    '.blob.vercel-storage.com',
    'decoded_path != pathname',
    'pathname.startswith("bts-audio/")',
  ])
);

console.log('');
console.log(
  `BTS CONTRACT SCORE: ${passes.length}/${
    passes.length + failures.length
  } (${Math.round(
    (passes.length /
      (passes.length + failures.length)) *
      100
  )}%)`
);

if (failures.length) {
  console.error('\nFailed contracts:');
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}
