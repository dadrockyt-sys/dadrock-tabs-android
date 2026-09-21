const RESULT = Object.freeze({
  receiptSha256: '3edfcf97766bef89ea56429a7385107d99868dc948d867251bcc5f9066a18112',
  workflowRunId: 35569391647,
  launchCommit: 'ec4860d9da2eef2952bf47bb7beb904b215562c4',
  p1TrainP2Validate: Object.freeze({
    resultSha256: '024e5d2d3612732e85f2c0b812f223e602fcdf6e69f82ca8d5a2d0d0e89090f0',
    modelSha256: '8dc70d94741e0b472e93481f498efafb7627445896594752b217e000f2832a83',
    f1: 0.237859615980499,
    qualified: false,
  }),
  p2TrainP1Validate: Object.freeze({
    resultSha256: 'c6dcc9e557c7e030f523410e705c35e4e7fea3c994e490487c7755e3e2793950',
    modelSha256: 'd480cadf66fc0d98608c719252c34bdab4c3120252167e8786502b4332264841',
    f1: 0.18940295658840373,
    qualified: false,
  }),
  macroF1: 0.21363128628445138,
  macroCompleteness: 0.20420847659537342,
  developmentAccepted: false,
  p3OpeningEligible: false,
});

export const GUITAR_TECHS_REAL_TRAINING_RESULT_RECEIPT_SHA256 = RESULT.receiptSha256;

export function getGuitarTechsRealTrainingResultIdentity() {
  return structuredClone(RESULT);
}

export function evaluateGuitarTechsRealTrainingResult({
  receiptSha256,
  workflowRunId,
  p1TrainP2ResultSha256,
  p2TrainP1ResultSha256,
  p3Opened = false,
  customerDeliveryRequested = false,
} = {}) {
  const blockers = [];
  if (receiptSha256 !== RESULT.receiptSha256) blockers.push('GUITAR_TECHS_REAL_TRAINING_RESULT_RECEIPT_MISMATCH');
  if (workflowRunId !== RESULT.workflowRunId) blockers.push('GUITAR_TECHS_REAL_TRAINING_RUN_IDENTITY_MISMATCH');
  if (p1TrainP2ResultSha256 !== RESULT.p1TrainP2Validate.resultSha256
      || p2TrainP1ResultSha256 !== RESULT.p2TrainP1Validate.resultSha256) {
    blockers.push('GUITAR_TECHS_REAL_TRAINING_FOLD_RESULT_IDENTITY_MISMATCH');
  }
  blockers.push('GUITAR_TECHS_DEVELOPMENT_THRESHOLDS_NOT_MET');
  if (p3Opened === true) blockers.push('GUITAR_TECHS_P3_SEALED');
  if (customerDeliveryRequested === true) blockers.push('CUSTOMER_DELIVERY_NOT_AUTHORIZED');

  return {
    evidenceAccepted: blockers.every((b) => b === 'GUITAR_TECHS_DEVELOPMENT_THRESHOLDS_NOT_MET'),
    developmentAccepted: false,
    blockers: [...new Set(blockers)].sort(),
    modelTrained: true,
    p3OpeningEligible: false,
    customerDeliveryEligible: false,
  };
}
