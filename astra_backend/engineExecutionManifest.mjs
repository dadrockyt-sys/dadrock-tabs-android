const SHA1 = /^[0-9a-f]{40}$/;
const SHA256 = /^[0-9a-f]{64}$/;
const ROLES = new Set(['lead', 'rhythm', 'bass']);

const EXPECTED = Object.freeze({
  contractName: 'jimmy-paige-astra-engine-execution-manifest',
  contractVersion: 1,
  candidateId: 'htdemucs6s-basic-pitch',
  audioSeparator: Object.freeze({
    packageVersion: '0.30.2',
    upstreamCommit: '99840eea955a19305413639c21ee58e320a1fd14',
  }),
  demucs: Object.freeze({
    packageVersion: '4.0.1',
    upstreamCommit: 'ef66d254cd6d558e207eeff2c4b8d053db2e77dd',
    modelName: 'htdemucs_6s',
    configGitBlob: '651a0fa536038a3e6d650f7b2bcc0b50ff7a4be9',
    weightFilename: '5c90dfd2-34c22ccb.th',
    historicalWeightSha256: 'd2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411',
  }),
  basicPitch: Object.freeze({
    packageVersion: '0.4.0',
    upstreamCommit: '9991303bba609a3b93089d13ec80d1d495083596',
    modelPath: 'basic_pitch/saved_models/icassp_2022/nmp.tflite',
    modelGitBlob: '85a41befdd036e9b365a052b7c704c6810288b95',
    modelBytes: 204448,
  }),
});

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function requireObject(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`${label} must be an object.`);
  }
  return value;
}

function requireExact(actual, expected, label) {
  if (actual !== expected) throw new Error(`${label} does not match the frozen Astra identity.`);
}

function requireDigest(value, pattern, label) {
  if (typeof value !== 'string' || !pattern.test(value)) {
    throw new Error(`${label} must be a lowercase hexadecimal digest.`);
  }
}

export function getFrozenAstraEngineIdentity() {
  return clone(EXPECTED);
}

export function validateAstraEngineExecutionManifest(manifest, { role } = {}) {
  const root = requireObject(manifest, 'manifest');
  if (!ROLES.has(role)) throw new Error('role must be lead, rhythm, or bass.');

  const contract = requireObject(root.contract, 'contract');
  requireExact(contract.name, EXPECTED.contractName, 'contract.name');
  requireExact(contract.version, EXPECTED.contractVersion, 'contract.version');
  requireExact(root.candidateId, EXPECTED.candidateId, 'candidateId');
  requireExact(root.intendedUse, 'development-comparison-only', 'intendedUse');

  const execution = requireObject(root.execution, 'execution');
  requireExact(execution.device, 'cpu', 'execution.device');

  const audioSeparator = requireObject(execution.audioSeparator, 'execution.audioSeparator');
  requireExact(audioSeparator.packageVersion, EXPECTED.audioSeparator.packageVersion, 'audioSeparator.packageVersion');
  requireDigest(audioSeparator.upstreamCommit, SHA1, 'audioSeparator.upstreamCommit');
  requireExact(audioSeparator.upstreamCommit, EXPECTED.audioSeparator.upstreamCommit, 'audioSeparator.upstreamCommit');

  const demucs = requireObject(execution.demucs, 'execution.demucs');
  requireExact(demucs.packageVersion, EXPECTED.demucs.packageVersion, 'demucs.packageVersion');
  requireExact(demucs.upstreamCommit, EXPECTED.demucs.upstreamCommit, 'demucs.upstreamCommit');
  requireExact(demucs.modelName, EXPECTED.demucs.modelName, 'demucs.modelName');
  requireExact(demucs.configGitBlob, EXPECTED.demucs.configGitBlob, 'demucs.configGitBlob');
  requireExact(demucs.weightFilename, EXPECTED.demucs.weightFilename, 'demucs.weightFilename');
  requireDigest(demucs.historicalWeightSha256, SHA256, 'demucs.historicalWeightSha256');
  requireExact(
    demucs.historicalWeightSha256,
    EXPECTED.demucs.historicalWeightSha256,
    'demucs.historicalWeightSha256',
  );

  const basicPitch = requireObject(execution.basicPitch, 'execution.basicPitch');
  requireExact(basicPitch.packageVersion, EXPECTED.basicPitch.packageVersion, 'basicPitch.packageVersion');
  requireExact(basicPitch.upstreamCommit, EXPECTED.basicPitch.upstreamCommit, 'basicPitch.upstreamCommit');
  requireExact(basicPitch.modelPath, EXPECTED.basicPitch.modelPath, 'basicPitch.modelPath');
  requireExact(basicPitch.modelGitBlob, EXPECTED.basicPitch.modelGitBlob, 'basicPitch.modelGitBlob');
  requireExact(basicPitch.modelBytes, EXPECTED.basicPitch.modelBytes, 'basicPitch.modelBytes');

  const capabilities = requireObject(root.capabilities, 'capabilities');
  requireExact(capabilities.bassStem, true, 'capabilities.bassStem');
  requireExact(capabilities.genericGuitarStem, true, 'capabilities.genericGuitarStem');
  requireExact(capabilities.leadRhythmDistinction, false, 'capabilities.leadRhythmDistinction');

  const rights = requireObject(root.rights, 'rights');
  const demucsWeightRights = requireObject(rights.demucsWeight, 'rights.demucsWeight');
  const basicPitchModelRights = requireObject(rights.basicPitchModel, 'rights.basicPitchModel');
  const evidence = requireObject(root.evidence, 'evidence');
  const policy = requireObject(root.policy, 'policy');

  const blockers = [];
  if (!SHA256.test(evidence.packageLockSha256 || '')) blockers.push('PACKAGE_LOCK_IDENTITY_MISSING');
  if (evidence.modelArtifactsVerifiedOnAstra !== true) blockers.push('MODEL_ARTIFACTS_NOT_VERIFIED_ON_ASTRA');
  if (evidence.runtimeWithin1200Seconds !== true) blockers.push('RUNTIME_BUDGET_UNPROVEN');
  if (evidence.developmentMaterialAuthorized !== true) blockers.push('DEVELOPMENT_MATERIAL_AUTHORIZATION_MISSING');
  if (demucsWeightRights.status !== 'reviewed-cleared' || demucsWeightRights.commercialUseReviewed !== true) {
    blockers.push('DEMUCS_WEIGHT_TERMS_UNRESOLVED');
  }
  if (basicPitchModelRights.status !== 'reviewed-cleared' || basicPitchModelRights.commercialUseReviewed !== true) {
    blockers.push('BASIC_PITCH_MODEL_TERMS_UNREVIEWED');
  }
  if (role === 'lead' || role === 'rhythm') blockers.push('LEAD_RHYTHM_DISTINCTION_UNAVAILABLE');
  if (policy.customerDeliveryAllowed !== false) {
    throw new Error('policy.customerDeliveryAllowed must remain false for this manifest version.');
  }

  const normalizedBlockers = [...new Set(blockers)].sort();
  return {
    validationContract: { name: 'jimmy-paige-astra-engine-manifest-validation', version: 1 },
    candidateId: root.candidateId,
    role,
    manifestStructurallyValid: true,
    exactKnownIdentitiesMatch: true,
    blockers: normalizedBlockers,
    developmentExecutionReady: normalizedBlockers.length === 0,
    customerDeliveryEligible: false,
    invokesModel: false,
    opensAudio: false,
    performsNetworkAccess: false,
  };
}
