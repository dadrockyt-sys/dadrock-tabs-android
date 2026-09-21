const RECEIPT = Object.freeze({
  schema: 'astra-guitar-techs-p2-tuning-evidence-v1',
  sha256: '5474eaccdf651c637dc7b3b2145098fe050714b77542b843742ac2f645702715',
  sourceInventoryReceiptSha256: '4d21d578a275587abe18d9f5382074fa9c33bd2f0698c5d10b340788de306bcd',
  sourceFullInventoryRunId: 35563511409,
  openMidiHighToLow: Object.freeze([64, 59, 55, 50, 45, 40]),
  openMidiLowToHigh: Object.freeze([40, 45, 50, 55, 59, 64]),
  tuning: 'E2 A2 D3 G3 B3 E4',
  dStringDirectlyObservedOpenMidi: false,
  dStringStructuralInference: 'shared-allnotes-schema-single-missing-open-endpoint',
});

export const GUITAR_TECHS_P2_TUNING_EVIDENCE_SHA256 = RECEIPT.sha256;

export function getGuitarTechsP2TuningEvidenceIdentity() {
  return structuredClone(RECEIPT);
}

export function evaluateGuitarTechsP2TuningEvidence({
  receiptSha256,
  sourceInventoryReceiptSha256,
  sourceFullInventoryRunId,
  openMidiHighToLow,
  dObservedUniqueMidi,
  usesP3 = false,
  usesModelPrediction = false,
  trainingRun = false,
} = {}) {
  const blockers = [];
  if (receiptSha256 !== RECEIPT.sha256) blockers.push('GUITAR_TECHS_P2_TUNING_RECEIPT_IDENTITY_MISMATCH');
  if (sourceInventoryReceiptSha256 !== RECEIPT.sourceInventoryReceiptSha256
      || sourceFullInventoryRunId !== RECEIPT.sourceFullInventoryRunId) {
    blockers.push('GUITAR_TECHS_P2_TUNING_SOURCE_IDENTITY_MISMATCH');
  }
  if (!Array.isArray(openMidiHighToLow)
      || openMidiHighToLow.length !== RECEIPT.openMidiHighToLow.length
      || openMidiHighToLow.some((midi, index) => midi !== RECEIPT.openMidiHighToLow[index])) {
    blockers.push('GUITAR_TECHS_P2_TUNING_OPEN_STRING_MISMATCH');
  }
  const expectedDObserved = Array.from({length: 22}, (_, index) => 51 + index);
  if (!Array.isArray(dObservedUniqueMidi)
      || dObservedUniqueMidi.length !== expectedDObserved.length
      || dObservedUniqueMidi.some((midi, index) => midi !== expectedDObserved[index])) {
    blockers.push('GUITAR_TECHS_P2_D_STRING_MISSING_ENDPOINT_PATTERN_MISMATCH');
  }
  if (usesP3 === true) blockers.push('GUITAR_TECHS_P3_SEALED');
  if (usesModelPrediction === true) blockers.push('GUITAR_TECHS_TUNING_MUST_NOT_USE_MODEL_PREDICTION');
  if (trainingRun === true) blockers.push('GUITAR_TECHS_TRAINING_NOT_AUTHORIZED_BY_TUNING_RECEIPT');

  const uniqueBlockers = [...new Set(blockers)].sort();
  return {
    evidenceAccepted: uniqueBlockers.length === 0,
    blockers: uniqueBlockers,
    tuningVerified: uniqueBlockers.length === 0,
    openMidiHighToLow: [...RECEIPT.openMidiHighToLow],
    openMidiLowToHigh: [...RECEIPT.openMidiLowToHigh],
    tuning: RECEIPT.tuning,
    dStringOpenMidiDirectlyObserved: false,
    dStringOpenMidiStructurallyVerified: uniqueBlockers.length === 0,
    alignmentAuthorizedByThisReceipt: false,
    trainingAuthorizedByThisReceipt: false,
    p3Sealed: true,
    customerDeliveryEligible: false,
  };
}
