const RECEIPT = Object.freeze({
  schema: 'astra-guitar-techs-development-inventory-evidence-v1',
  sha256: '4d21d578a275587abe18d9f5382074fa9c33bd2f0698c5d10b340788de306bcd',
  fullInventoryRunId: 35563511409,
  p2ChordsRecoveryRunId: 35563847021,
  p2ChordsRecoveryArtifactId: 10623565422,
  archiveCount: 8,
  performanceGroupCount: 92,
  canonicalTrackNamesHighToLow: Object.freeze(['e', 'B', 'G', 'D', 'A', 'E']),
  chordStringIdentityPolicy: 'explicit-track-name-never-positional',
  p1TuningVerified: true,
  p2TuningFullyVerified: false,
  p3Sealed: true,
});

export const GUITAR_TECHS_INVENTORY_EVIDENCE_RECEIPT_SHA256 = RECEIPT.sha256;

export function getGuitarTechsInventoryEvidenceIdentity() {
  return structuredClone(RECEIPT);
}

export function evaluateGuitarTechsInventoryEvidence({
  receiptSha256,
  fullInventoryRunId,
  p2ChordsRecoveryRunId,
  archiveCount,
  performanceGroupCount,
  chordStringIdentityPolicy,
  p3Opened = false,
  alignmentRun = false,
  trainingRun = false,
} = {}) {
  const blockers = [];
  if (receiptSha256 !== RECEIPT.sha256) blockers.push('GUITAR_TECHS_INVENTORY_RECEIPT_IDENTITY_MISMATCH');
  if (fullInventoryRunId !== RECEIPT.fullInventoryRunId
      || p2ChordsRecoveryRunId !== RECEIPT.p2ChordsRecoveryRunId) {
    blockers.push('GUITAR_TECHS_INVENTORY_RUN_IDENTITY_MISMATCH');
  }
  if (archiveCount !== RECEIPT.archiveCount || performanceGroupCount !== RECEIPT.performanceGroupCount) {
    blockers.push('GUITAR_TECHS_INVENTORY_GROUPING_MISMATCH');
  }
  if (chordStringIdentityPolicy !== RECEIPT.chordStringIdentityPolicy) {
    blockers.push('GUITAR_TECHS_STRING_TRACK_MAPPING_POLICY_MISMATCH');
  }
  if (p3Opened === true) blockers.push('GUITAR_TECHS_P3_SEALED');
  if (alignmentRun === true) blockers.push('GUITAR_TECHS_ALIGNMENT_NOT_AUTHORIZED_BY_INVENTORY_RECEIPT');
  if (trainingRun === true) blockers.push('GUITAR_TECHS_TRAINING_NOT_AUTHORIZED_BY_INVENTORY_RECEIPT');

  const uniqueBlockers = [...new Set(blockers)].sort();
  return {
    evidenceAccepted: uniqueBlockers.length === 0,
    blockers: uniqueBlockers,
    performanceGroupingVerified: uniqueBlockers.length === 0,
    captureViewGroupingVerified: uniqueBlockers.length === 0,
    stringTrackMappingVerified: uniqueBlockers.length === 0,
    techniqueMidiSemanticsReviewed: uniqueBlockers.length === 0,
    p1TuningVerified: uniqueBlockers.length === 0,
    p2TuningFullyVerified: false,
    nextBlockers: uniqueBlockers.length === 0 ? [
      'P2_D_STRING_TUNING_NOT_FULLY_VERIFIED',
      'ALIGNMENT_CORRECTION_NOT_VERIFIED',
      'TRAINING_NOT_AUTHORIZED',
    ] : [],
    p3Sealed: true,
    customerDeliveryEligible: false,
  };
}
