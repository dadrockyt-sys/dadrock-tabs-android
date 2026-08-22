import assert from 'node:assert/strict';

import {
  PREVIEW_CANARY_BRANCH,
  getJimmyPaigeProfessionalPdfFeatureState,
} from '../lib/jimmyPaigeProfessionalPdfFeature.js';

const disabled = getJimmyPaigeProfessionalPdfFeatureState({});
assert.equal(disabled.enabled, false);
assert.equal(disabled.source, 'disabled');
assert.equal(disabled.productionPromotionAuthorized, false);

const productionSameBranch = getJimmyPaigeProfessionalPdfFeatureState({
  VERCEL_ENV: 'production',
  VERCEL_GIT_COMMIT_REF: PREVIEW_CANARY_BRANCH,
});
assert.equal(
  productionSameBranch.enabled,
  false,
  'same branch must not auto-enable professional PDF in Production'
);
assert.equal(
  productionSameBranch.branchPreviewCanaryEnabled,
  false
);

const previewWrongBranch = getJimmyPaigeProfessionalPdfFeatureState({
  VERCEL_ENV: 'preview',
  VERCEL_GIT_COMMIT_REF: 'some-other-branch',
});
assert.equal(
  previewWrongBranch.enabled,
  false,
  'other Preview branches must remain disabled'
);

const previewCanary = getJimmyPaigeProfessionalPdfFeatureState({
  VERCEL_ENV: 'preview',
  VERCEL_GIT_COMMIT_REF: PREVIEW_CANARY_BRANCH,
});
assert.equal(previewCanary.enabled, true);
assert.equal(
  previewCanary.source,
  'v143-branch-preview-canary'
);
assert.equal(
  previewCanary.branchPreviewCanaryEnabled,
  true
);
assert.equal(
  previewCanary.productionPromotionAuthorized,
  false
);

const explicitFlag = getJimmyPaigeProfessionalPdfFeatureState({
  JIMMY_PAIGE_PROFESSIONAL_PDF_V1: 'true',
  VERCEL_ENV: 'production',
  VERCEL_GIT_COMMIT_REF: 'main',
});
assert.equal(
  explicitFlag.enabled,
  true,
  'existing explicit environment flag behavior must remain intact'
);
assert.equal(
  explicitFlag.source,
  'explicit-environment-flag'
);
assert.equal(
  explicitFlag.productionPromotionAuthorized,
  false
);

const explicitFalse = getJimmyPaigeProfessionalPdfFeatureState({
  JIMMY_PAIGE_PROFESSIONAL_PDF_V1: 'false',
  VERCEL_ENV: 'production',
  VERCEL_GIT_COMMIT_REF: 'main',
});
assert.equal(explicitFalse.enabled, false);

console.log('=== JIMMY PAIGE PREVIEW FEATURE GATE VERIFIED ===');
console.log(`previewCanaryBranch: ${PREVIEW_CANARY_BRANCH}`);
console.log(`previewCanaryEnabled: ${previewCanary.enabled}`);
console.log(`productionSameBranchEnabled: ${productionSameBranch.enabled}`);
console.log(`wrongPreviewBranchEnabled: ${previewWrongBranch.enabled}`);
console.log(`explicitFlagPreserved: ${explicitFlag.enabled}`);
console.log('productionPromotionAuthorized: false');
