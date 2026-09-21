const EVIDENCE = Object.freeze({
  receiptSha256: '8e65fda2a74f5f5af77ab62be3538715d9ec2c0dcd783de5837a56c5dd42b1ae',
  workflowRunId: 35565975272,
  sourceCommit: 'f6c0d17d367b1a264529ffce66a0a6d919bfd147',
  implementationReceiptSha256: 'b33dd0fd220fcef4a459cc47277f48cf90c0acd320e523c3afcea5fc52a8a26f',
  alignmentScriptSha256: 'b084da0900acf9bd4ec61386a4a928350af0e138c9ed36ef3fbafb15539bc330',
  primaryUniverseCaptureCount: 336,
  acceptedPrimaryCaptureCount: 256,
  abstainedPrimaryCaptureCount: 80,
  acceptedPrimaryCaptureKeysSha256: 'f520f5ffe3daf44da9bad1d145adaa1c9ff0bb662141b027f85b8c7bc827eabc',
  abstainedPrimaryCaptureKeysSha256: 'b4221bdc8236eb5f7c3a1cc5dca0f0d5d931d6acff7a56210525f08c0d26c812',
  p3Opened: false,
  trainingRun: false,
});

export const GUITAR_TECHS_ALIGNMENT_EVIDENCE_RECEIPT_SHA256 = EVIDENCE.receiptSha256;

export function getGuitarTechsAlignmentEvidenceIdentity() {
  return structuredClone(EVIDENCE);
}

export function evaluateGuitarTechsAlignmentEvidence({
  receiptSha256,
  workflowRunId,
  implementationReceiptSha256,
  alignmentScriptSha256,
  primaryUniverseCaptureCount,
  acceptedPrimaryCaptureCount,
  abstainedPrimaryCaptureCount,
  acceptedPrimaryCaptureKeysSha256,
  abstainedPrimaryCaptureKeysSha256,
  p3Opened = false,
  trainingRun = false,
} = {}) {
  const blockers = [];
  if (receiptSha256 !== EVIDENCE.receiptSha256) blockers.push('GUITAR_TECHS_ALIGNMENT_RECEIPT_IDENTITY_MISMATCH');
  if (workflowRunId !== EVIDENCE.workflowRunId) blockers.push('GUITAR_TECHS_ALIGNMENT_RUN_IDENTITY_MISMATCH');
  if (implementationReceiptSha256 !== EVIDENCE.implementationReceiptSha256
      || alignmentScriptSha256 !== EVIDENCE.alignmentScriptSha256) {
    blockers.push('GUITAR_TECHS_ALIGNMENT_IMPLEMENTATION_IDENTITY_MISMATCH');
  }
  if (primaryUniverseCaptureCount !== EVIDENCE.primaryUniverseCaptureCount
      || acceptedPrimaryCaptureCount !== EVIDENCE.acceptedPrimaryCaptureCount
      || abstainedPrimaryCaptureCount !== EVIDENCE.abstainedPrimaryCaptureCount
      || acceptedPrimaryCaptureCount + abstainedPrimaryCaptureCount !== primaryUniverseCaptureCount) {
    blockers.push('GUITAR_TECHS_ALIGNMENT_CAPTURE_COUNT_MISMATCH');
  }
  if (acceptedPrimaryCaptureKeysSha256 !== EVIDENCE.acceptedPrimaryCaptureKeysSha256
      || abstainedPrimaryCaptureKeysSha256 !== EVIDENCE.abstainedPrimaryCaptureKeysSha256) {
    blockers.push('GUITAR_TECHS_ALIGNMENT_CAPTURE_SET_IDENTITY_MISMATCH');
  }
  if (p3Opened === true) blockers.push('GUITAR_TECHS_P3_SEALED');
  if (trainingRun === true) blockers.push('GUITAR_TECHS_TRAINING_NOT_AUTHORIZED_BY_ALIGNMENT_RECEIPT');

  const uniqueBlockers = [...new Set(blockers)].sort();
  return {
    evidenceAccepted: uniqueBlockers.length === 0,
    blockers: uniqueBlockers,
    alignmentCorrectionVerified: uniqueBlockers.length === 0,
    acceptedPrimaryCaptureCount: EVIDENCE.acceptedPrimaryCaptureCount,
    abstainedPrimaryCaptureCount: EVIDENCE.abstainedPrimaryCaptureCount,
    requiresExactAbstentionFilter: true,
    trainingAuthorizedByThisReceipt: false,
    p3Sealed: true,
    customerDeliveryEligible: false,
  };
}
