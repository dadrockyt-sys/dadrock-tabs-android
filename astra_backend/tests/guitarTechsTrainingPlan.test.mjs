import test from 'node:test';
import assert from 'node:assert/strict';

import {
  assertGuitarTechsPlanIntegrity,
  getGuitarTechsTrainingPlan,
} from '../guitarTechsTrainingPlan.mjs';

test('Guitar-TECHS plan is static and does not download, open or train', () => {
  const plan = getGuitarTechsTrainingPlan();
  assert.equal(plan.contract.invokesModel, false);
  assert.equal(plan.contract.downloadsTrainingMedia, false);
  assert.equal(plan.contract.opensTrainingMedia, false);
  assert.equal(plan.contract.trainsModel, false);
  assert.equal(plan.contractReceipt.sha256, '09436268922e0d24332b7e3234225d54a0f28e58e23b55ea71227eeab1b1e81f');
  assert.equal(plan.customerDeliveryEligible, false);
});

test('blocked GuitarProFX checkpoint cannot initialize the new candidate', () => {
  const plan = getGuitarTechsTrainingPlan();
  assert.equal(plan.architecture.initialization, 'random-only');
  assert.equal(plan.architecture.forbiddenInitializationArtifact, 'tabcnn_guitarprofx_dafx24');
  assert.equal(assertGuitarTechsPlanIntegrity(plan), true);

  plan.architecture.initialization = 'pretrained';
  assert.throws(
    () => assertGuitarTechsPlanIntegrity(plan),
    /BLOCKED_CHECKPOINT_INITIALIZATION_FORBIDDEN/,
  );
});

test('development folds are performer-disjoint and P3 remains sealed', () => {
  const plan = getGuitarTechsTrainingPlan();
  for (const fold of plan.splitPolicy.developmentFolds) {
    assert.equal(
      fold.trainPerformers.some((performer) => fold.validationPerformers.includes(performer)),
      false,
    );
    assert.equal(fold.trainPerformers.includes('P3'), false);
    assert.equal(fold.validationPerformers.includes('P3'), false);
  }
  assert.deepEqual(plan.splitPolicy.sealedGeneralizationGate.performers, ['P3']);
  assert.equal(plan.splitPolicy.sealedGeneralizationGate.mayOpenBeforeFreeze, false);
});

test('capture-channel grouping prevents correlated-view leakage', () => {
  const plan = getGuitarTechsTrainingPlan();
  assert.equal(plan.splitPolicy.groupingUnit, 'underlying-performance');
  assert.equal(plan.splitPolicy.keepAllCaptureChannelsTogether, true);
  assert.equal(plan.splitPolicy.randomClipSplitForbidden, true);
});

test('published archive identities are deterministic and defensive', () => {
  const first = getGuitarTechsTrainingPlan();
  const p3 = first.dataset.publishedArchives.P3[0];
  assert.equal(p3.file, 'P3_music.zip');
  assert.equal(p3.bytes, 129505089);
  assert.equal(p3.md5, '071ba80aecf00f4a31fbd167b3f22198');
  assert.equal(first.dataset.publishedIdentityManifestSha256, 'a3445d799c4a0b17a0078dac0c9387a0e676111367a5f07d608fd55bd8118e52');
  assert.equal(first.splitPolicy.receiptSha256, 'd116556c13d250af28900bb1d73d2c0ccd3130246db8bdd2d6d387ac87be799a');
  first.dataset.publishedArchives.P1[0].md5 = 'mutated';
  const second = getGuitarTechsTrainingPlan();
  assert.equal(second.dataset.publishedArchives.P1[0].md5, 'be9ef8bbdceb1912d565254e607a6d94');
});
