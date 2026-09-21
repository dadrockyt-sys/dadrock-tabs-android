import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

test('V1 training failure diagnosis receipt is frozen and keeps P3 sealed', () => {
  const bytes = readFileSync(new URL('../../docs/astra/GUITARTECHS_V1_TRAINING_FAILURE_DIAGNOSIS_V1.json', import.meta.url));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), 'c9ec7f099b57451bdaaa683c3d644a3f11e340b296916f9771702f4699462848');
  const receipt = JSON.parse(bytes.toString('utf8'));
  assert.equal(receipt.findings.v1TrainingSemantics.supervisedFramePositionsPerFold, 80000);
  assert.equal(receipt.findings.pinnedUpstreamSemantics.numFramesPerTrackSample, 200);
  assert.equal(receipt.findings.mismatch.minimumFrameExposureRatioVsSame2500StepsWith200FrameSequences, 200);
  assert.equal(receipt.findings.v1TrainingSemantics.silenceAcceptedAsSample, true);
  assert.equal(receipt.v2DesignConstraints.sequenceFrames, 200);
  assert.equal(receipt.v2DesignConstraints.realTrainingAuthorized, false);
  assert.equal(receipt.guards.p3Opened, false);
});
