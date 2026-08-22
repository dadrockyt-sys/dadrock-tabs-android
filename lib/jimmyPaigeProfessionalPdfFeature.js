const PREVIEW_CANARY_BRANCH = 'v143-contextual-prune-lobo';

export function getJimmyPaigeProfessionalPdfFeatureState(
  env = process.env
) {
  const explicitFlagEnabled =
    String(env?.JIMMY_PAIGE_PROFESSIONAL_PDF_V1 || '') === 'true';

  const branchPreviewCanaryEnabled =
    String(env?.VERCEL_ENV || '') === 'preview' &&
    String(env?.VERCEL_GIT_COMMIT_REF || '') === PREVIEW_CANARY_BRANCH;

  const enabled =
    explicitFlagEnabled || branchPreviewCanaryEnabled;

  return {
    enabled,
    source: explicitFlagEnabled
      ? 'explicit-environment-flag'
      : branchPreviewCanaryEnabled
        ? 'v143-branch-preview-canary'
        : 'disabled',
    explicitFlagEnabled,
    branchPreviewCanaryEnabled,
    previewCanaryBranch: PREVIEW_CANARY_BRANCH,
    productionPromotionAuthorized: false,
  };
}

export { PREVIEW_CANARY_BRANCH };
