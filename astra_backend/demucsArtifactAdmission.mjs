const SHA256 = /^[0-9a-f]{64}$/;

const EXPECTED = Object.freeze({
  contract: Object.freeze({
    name: 'jimmy-paige-astra-demucs-artifact-admission',
    version: 1,
  }),
  candidateId: 'htdemucs6s-basic-pitch',
  modelName: 'htdemucs_6s',
  artifact: Object.freeze({
    fileName: '5c90dfd2-34c22ccb.th',
    sourceUrl: 'https://dl.fbaipublicfiles.com/demucs/hybrid_transformer/5c90dfd2-34c22ccb.th',
    sha256: 'd2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411',
  }),
  rightsDecision: Object.freeze({
    status: 'required-external-review',
    recordSha256: null,
    requiredArtifactScope: '5c90dfd2-34c22ccb.th@d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411',
    requiredUses: Object.freeze([
      'development-quality-evaluation',
      'commercial-customer-inference',
    ]),
  }),
});

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function requireExact(actual, expected, label) {
  if (actual !== expected) throw new Error(`${label} does not match the frozen Demucs artifact identity.`);
}

export function getFrozenDemucsArtifactAdmissionContract() {
  return clone(EXPECTED);
}

export function evaluateDemucsArtifactAdmission(observation = {}) {
  requireExact(observation.candidateId, EXPECTED.candidateId, 'candidateId');
  requireExact(observation.modelName, EXPECTED.modelName, 'modelName');
  requireExact(observation.fileName, EXPECTED.artifact.fileName, 'fileName');
  requireExact(observation.sourceUrl, EXPECTED.artifact.sourceUrl, 'sourceUrl');
  if (typeof observation.sha256 !== 'string' || !SHA256.test(observation.sha256)) {
    throw new Error('sha256 must be a lowercase hexadecimal digest.');
  }
  requireExact(observation.sha256, EXPECTED.artifact.sha256, 'sha256');

  const blockers = [];
  if (observation.artifactBytesObservedOnAstra !== true) {
    blockers.push('DEMUCS_WEIGHT_BYTES_NOT_OBSERVED_ON_ASTRA');
  }
  if (EXPECTED.rightsDecision.recordSha256 === null) {
    blockers.push('DEMUCS_WEIGHT_RIGHTS_DECISION_NOT_FROZEN');
  } else if (observation.rightsDecisionRecordSha256 !== EXPECTED.rightsDecision.recordSha256) {
    blockers.push('DEMUCS_WEIGHT_RIGHTS_DECISION_MISMATCH');
  }

  const normalizedBlockers = [...new Set(blockers)].sort();
  return {
    admissionContract: clone(EXPECTED.contract),
    candidateId: EXPECTED.candidateId,
    modelName: EXPECTED.modelName,
    artifactIdentityMatches: true,
    rightsDecisionFrozen: EXPECTED.rightsDecision.recordSha256 !== null,
    admittedForDevelopmentExecution: normalizedBlockers.length === 0,
    customerDeliveryAllowed: false,
    blockers: normalizedBlockers,
    downloadsArtifact: false,
    importsModel: false,
    invokesModel: false,
    opensAudio: false,
    performsNetworkAccess: false,
  };
}
