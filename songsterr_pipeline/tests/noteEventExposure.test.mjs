import test from 'node:test';
import assert from 'node:assert/strict';

import { buildNoteEventExposure } from '../noteEventExposure.mjs';

function evidence({ roleResolved = false } = {}) {
  return {
    adapterContract: {
      referenceBlind: true,
      structureFrozen: true,
      structureIdentityVerified: true,
    },
    role: 'guitar',
    structureIdentity: { signature: 'fnv1a32:test' },
    capabilities: {
      roleRelevanceResolved: roleResolved,
      polyphonyResolved: false,
      durationResolution: 'partial',
    },
    promotedEvents: [
      { evidenceOnsetId: 'a', start: 0.5, midi: 40, duration: 0.25 },
      { evidenceOnsetId: 'b', start: 1, midi: 52 },
    ],
  };
}

test('locally pitch-resolved events stay visible while unresolved role exposure is empty', () => {
  const result = buildNoteEventExposure(evidence(), { acceptedForCompleteTab: false });
  assert.deepEqual(result.pitchResolvedEvents.map((event) => event.midi), [40, 52]);
  assert.equal(result.roleAcceptedEvents.length, 0);
  assert.equal(result.completeTabEligibleEvents.length, 0);
  assert.equal(result.metrics.pitchResolvedEventCount, 2);
  assert.equal(result.metrics.roleAcceptedEventCount, 0);
  assert.ok(result.blockers.includes('ROLE_RELEVANCE_UNRESOLVED'));
});

test('role resolution exposes the exact same MIDI/onset identities without substitution', () => {
  const result = buildNoteEventExposure(evidence({ roleResolved: true }), { acceptedForCompleteTab: false });
  assert.deepEqual(
    result.roleAcceptedEvents.map((event) => [event.evidenceOnsetId, event.start, event.midi]),
    [['a', 0.5, 40], ['b', 1, 52]],
  );
  assert.equal(result.completeTabEligibleEvents.length, 0);
});

test('complete-tab eligibility requires both role exposure and evaluator acceptance', () => {
  const result = buildNoteEventExposure(evidence({ roleResolved: true }), { acceptedForCompleteTab: true });
  assert.deepEqual(result.completeTabEligibleEvents, result.roleAcceptedEvents);
  assert.equal(result.metrics.completeTabEligibleEventCount, 2);
});

test('exposure fails closed when frozen reference-blind identity was not verified', () => {
  const raw = evidence();
  raw.adapterContract.structureIdentityVerified = false;
  assert.throws(() => buildNoteEventExposure(raw, { acceptedForCompleteTab: false }), /STRUCTURE_IDENTITY_UNVERIFIED/);
});
