import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

import {
  GUITAR_TECHS_V2_RESULT_ADMISSION_CONTRACT_SHA256,
  evaluateGuitarTechsV2TrainingResults,
  getGuitarTechsV2ResultAdmissionContract,
} from '../guitarTechsV2ResultAdmission.mjs';

const receiptBytes = readFileSync(new URL('../../docs/astra/GUITARTECHS_V2_RESULT_ADMISSION_CONTRACT_V1.json', import.meta.url));
const metrics = (overrides={}) => ({
  precision: 0.80, recall: 0.72, f1: 0.75, completeness: 0.70,
  frameAccuracy: 0.78, abstentionRate: 0.03,
  contentF1: {chords:0.70, scales:0.80, singlenotes:0.85, PalmMute:0.68},
  ...overrides,
});
const balance = (n) => ({
  canonicalPerformanceCount:n, activeFractionOfValid:0.2,
  perString:Array.from({length:6},()=>({active:1})),
  perContent:{chords:{active:1},scales:{active:1},singlenotes:{active:1},PalmMute:{active:1}},
});
const fold = (name, train, validate, performances, validationCaptures, supervised, overrides={}) => ({
  schema:'astra-guitar-techs-real-training-fold-v2', candidateId:'astra_guitartechs_tabcnn_v2',
  fold:name, trainPerformer:train, validationPerformer:validate, seed:20260921,
  epochs:1000, optimizerSteps:2000, sequenceFrames:200, batchSequences:32,
  microbatchSequences:1, validationCheckpoints:50,
  selected:{epoch:800}, fullValidationMetrics:metrics(),
  preparedCaptureCounts:{P1:136,P2:120}, trainingPerformanceCount:performances,
  validationCaptureCount:validationCaptures, supervisedFramePositions:supervised,
  pretrainingLabelBalance:balance(performances),
  budgetReceiptSha256:'8705df7cde4456dc17b5973d84404981387a322ea195a3f995a72ae6b236b430',
  failureDiagnosisReceiptSha256:'c9ec7f099b57451bdaaa683c3d644a3f11e340b296916f9771702f4699462848',
  guards:{p3Opened:false,publishedCheckpointLoaded:false,paidComputeUsed:false,customerDeliveryEligible:false},
  ...overrides,
});
const good = {
  admissionContractSha256:GUITAR_TECHS_V2_RESULT_ADMISSION_CONTRACT_SHA256,
  authorizationReceiptSha256:'0edfb4656675e31fce0c8cbd1ba42f37619e877b43793d3386781572dea8cb69',
  p1TrainP2Validate:fold('p1-train-p2-validate','P1','P2',41,120,8200000),
  p2TrainP1Validate:fold('p2-train-p1-validate','P2','P1',40,136,8000000),
};

test('committed V2 result admission contract has exact frozen identity',()=>{
  assert.equal(createHash('sha256').update(receiptBytes).digest('hex'),GUITAR_TECHS_V2_RESULT_ADMISSION_CONTRACT_SHA256);
  const r=JSON.parse(receiptBytes.toString('utf8'));
  assert.equal(r.folds['p1-train-p2-validate'].supervisedFramePositions,8200000);
  assert.equal(r.folds['p2-train-p1-validate'].supervisedFramePositions,8000000);
  assert.equal(r.decision.thresholdRetuningAllowed,false);
  assert.equal(r.decision.p3OpeningAuthorizedByThisContract,false);
});

test('exact V2 fold evidence plus passing frozen metrics becomes development-accepted only',()=>{
  const r=evaluateGuitarTechsV2TrainingResults(good);
  assert.equal(r.developmentAccepted,true);
  assert.equal(r.modelTrainingEvidenceComplete,true);
  assert.equal(r.p3OpeningEligibleForSeparateAuthorization,true);
  assert.equal(r.p3OpeningAuthorizedByThisContract,false);
  assert.equal(r.customerDeliveryEligible,false);
  assert.deepEqual(r.blockers,[]);
});

test('wrong exposure or fold population fails closed before metric admission',()=>{
  let r=evaluateGuitarTechsV2TrainingResults({...good,p1TrainP2Validate:{...good.p1TrainP2Validate,supervisedFramePositions:80000}});
  assert.ok(r.blockers.includes('p1-train-p2-validate_SUPERVISEDFRAMEPOSITIONS_MISMATCH'));
  r=evaluateGuitarTechsV2TrainingResults({...good,p2TrainP1Validate:{...good.p2TrainP1Validate,trainingPerformanceCount:39}});
  assert.ok(r.blockers.includes('p2-train-p1-validate_TRAININGPERFORMANCECOUNT_MISMATCH'));
});

test('bad label-balance evidence and guard violations fail closed',()=>{
  const bad={...good.p1TrainP2Validate,pretrainingLabelBalance:balance(41),guards:{p3Opened:true,publishedCheckpointLoaded:false,paidComputeUsed:false,customerDeliveryEligible:false}};
  bad.pretrainingLabelBalance.activeFractionOfValid=0;
  const r=evaluateGuitarTechsV2TrainingResults({...good,p1TrainP2Validate:bad});
  assert.ok(r.blockers.includes('p1-train-p2-validate_PRETRAINING_ACTIVE_FRACTION_INVALID'));
  assert.ok(r.blockers.includes('p1-train-p2-validate_GUARD_VIOLATION'));
  assert.equal(r.developmentAccepted,false);
});

test('frozen metric failure stays a development failure and does not authorize P3',()=>{
  const badMetrics={...good.p2TrainP1Validate,fullValidationMetrics:metrics({f1:0.60})};
  const r=evaluateGuitarTechsV2TrainingResults({...good,p2TrainP1Validate:badMetrics});
  assert.ok(r.blockers.includes('P2_TRAIN_P1_VALIDATE_F1_BELOW_THRESHOLD'));
  assert.equal(r.developmentAccepted,false);
  assert.equal(r.p3OpeningEligibleForSeparateAuthorization,false);
});

test('P3 and customer delivery remain separately forbidden',()=>{
  const r=evaluateGuitarTechsV2TrainingResults({...good,p3Opened:true,customerDeliveryRequested:true});
  assert.ok(r.blockers.includes('GUITAR_TECHS_P3_SEALED'));
  assert.ok(r.blockers.includes('CUSTOMER_DELIVERY_NOT_AUTHORIZED'));
  assert.equal(r.p3OpeningAuthorizedByThisContract,false);
});

test('contract reads are defensive',()=>{
  const first=getGuitarTechsV2ResultAdmissionContract();
  first.folds['p1-train-p2-validate'].epochs=1;
  assert.equal(getGuitarTechsV2ResultAdmissionContract().folds['p1-train-p2-validate'].epochs,1000);
});
