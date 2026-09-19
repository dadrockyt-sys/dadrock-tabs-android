import test from 'node:test';
import assert from 'node:assert/strict';

import {
  evaluateBanquetIndependentCandidate,
  getBanquetIndependentCandidateReview,
} from '../independentSeparationCandidateReview.mjs';

test('Banquet review freezes the independently trained upstream identity', () => {
  const review = getBanquetIndependentCandidateReview();
  assert.equal(review.source.repository, 'kwatcharasupat/query-bandit');
  assert.equal(review.source.revision, '79ed5bb75e5c3a40cd319d9d990cee913fc65c26');
  assert.equal(review.source.licenseBlob, '227afbe7329cc553d2335a4cf5fd099473e9aad8');
  assert.equal(review.artifact.recordId, '13694558');
  assert.equal(review.artifact.recommendedFile, 'ev-pre-aug.ckpt');
  assert.equal(review.artifact.publishedMd5, '4dfb91d6d27c2dfd4992a15070915541');
  assert.equal(review.artifact.downloadedByAstra, false);
  assert.equal(review.source.modelConfigBlob, '0b157abc2f64b334803b6d89fd7b6ae28a0d5b31');
  assert.equal(review.source.queryEncoderBlob, 'a213f7854800d25349ceb584073ae7d748d9877c');
});

test('Banquet exposes bass and guitar classes and an explicit CPU control', () => {
  const review = getBanquetIndependentCandidateReview();
  assert.ok(review.capabilities.bassClasses.includes('bass_guitar'));
  assert.ok(review.capabilities.guitarClasses.includes('clean_electric_guitar'));
  assert.equal(review.runtime.explicitCpuPathInSource, true);
  assert.equal(review.runtime.cpuControl, 'use_cuda=false');
  assert.equal(review.queryDependency.labelOnlyPathIdentifiedInReviewedSource, false);
  assert.equal(review.queryDependency.precomputedEmbeddingProductPathFrozen, false);
});

test('Banquet fails closed on unresolved checkpoint rights and required query audio', () => {
  const result = evaluateBanquetIndependentCandidate({ role: 'bass' });
  assert.equal(result.technicallyPromisingForBassAndGenericGuitar, true);
  assert.equal(result.developmentExecutionReady, false);
  assert.equal(result.customerDeliveryEligible, false);
  assert.ok(result.blockers.includes('BANQUET_CHECKPOINT_LICENSE_UNRESOLVED'));
  assert.ok(result.blockers.includes('BANQUET_COMMERCIAL_INFERENCE_RIGHTS_UNRESOLVED'));
  assert.ok(result.blockers.includes('AUTHORIZED_QUERY_AUDIO_NOT_DEFINED'));
  assert.ok(result.blockers.includes('REFERENCE_BLIND_PRODUCT_PATH_UNRESOLVED'));
});

test('Banquet cannot manufacture lead or rhythm role evidence from instrument classes', () => {
  for (const role of ['lead', 'rhythm']) {
    const result = evaluateBanquetIndependentCandidate({ role });
    assert.ok(result.blockers.includes('LEAD_RHYTHM_DISTINCTION_UNAVAILABLE'));
    assert.equal(result.customerDeliveryEligible, false);
  }
});

test('Banquet 7B review performs no weight, model, audio, or network runtime work', () => {
  const result = evaluateBanquetIndependentCandidate({ role: 'bass' });
  assert.equal(result.downloadsArtifact, false);
  assert.equal(result.importsModel, false);
  assert.equal(result.invokesModel, false);
  assert.equal(result.opensAudio, false);
  assert.equal(result.performsNetworkAccess, false);
});

test('Banquet review rejects unsupported product roles', () => {
  assert.throws(
    () => evaluateBanquetIndependentCandidate({ role: 'other' }),
    /role must be bass, lead, or rhythm/,
  );
});
