const SHA1 = /^[0-9a-f]{40}$/;
const SHA256 = /^[0-9a-f]{64}$/;
const ROLES = new Set(['lead', 'rhythm', 'bass']);

const EXPECTED = Object.freeze({
  contractName: 'jimmy-paige-astra-engine-execution-manifest',
  contractVersion: 1,
  candidateId: 'htdemucs6s-basic-pitch',
  runtime: Object.freeze({
    pythonVersion: '3.10',
    platform: 'x86_64-manylinux_2_28',
    separatorEntryPoint: 'demucs-cli-direct',
    packageLockPath: 'astra_backend/engine/requirements.lock',
    packageLockSha256: 'a5614dbfad0be96aadc0d76297b6a59abe4e09c80bf2d6a484e53a14a58d38a7',
    packageCount: 57,
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

const LOCKED_CRITICAL_PACKAGES = Object.freeze({
  'basic-pitch': '0.4.0',
  demucs: '4.0.1',
  numpy: '1.26.4',
  'tflite-runtime': '2.14.0',
  torch: '2.11.0+cpu',
  torchaudio: '2.11.0+cpu',
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

export function verifyAstraEngineDependencyLock(lockText) {
  if (typeof lockText !== 'string' || !lockText.trim()) {
    throw new Error('Dependency lock text is required.');
  }

  const matches = [...lockText.matchAll(/^([a-z0-9][a-z0-9_.-]*)==([^\s\\]+)(?:\s*\\)?$/gmi)];
  const packages = {};
  for (const match of matches) {
    const name = match[1].toLowerCase().replaceAll('_', '-');
    if (packages[name]) throw new Error(`Dependency lock contains duplicate package: ${name}.`);
    packages[name] = match[2];

    const blockStart = match.index;
    const next = lockText.slice(blockStart + match[0].length).search(/^[a-z0-9][a-z0-9_.-]*==/mi);
    const blockEnd = next === -1 ? lockText.length : blockStart + match[0].length + next;
    const block = lockText.slice(blockStart, blockEnd);
    if (!/--hash=sha256:[0-9a-f]{64}/.test(block)) {
      throw new Error(`Dependency lock package lacks an artifact hash: ${name}.`);
    }
  }

  requireExact(Object.keys(packages).length, EXPECTED.runtime.packageCount, 'dependency package count');
  for (const [name, version] of Object.entries(LOCKED_CRITICAL_PACKAGES)) {
    requireExact(packages[name], version, `dependency ${name}`);
  }
  if (packages['audio-separator']) throw new Error('audio-separator must not re-enter the direct Demucs runtime.');
  if (packages.tensorflow) throw new Error('TensorFlow must not replace the pinned Python 3.10 TFLite runtime.');

  return {
    lockContract: { name: 'jimmy-paige-astra-engine-dependency-lock', version: 1 },
    packageCount: Object.keys(packages).length,
    criticalPackages: clone(LOCKED_CRITICAL_PACKAGES),
    directDemucsRuntime: true,
    audioSeparatorPresent: false,
    tensorflowPresent: false,
    allPackagesDeclareArtifactHashes: true,
  };
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
  requireExact(execution.pythonVersion, EXPECTED.runtime.pythonVersion, 'execution.pythonVersion');
  requireExact(execution.platform, EXPECTED.runtime.platform, 'execution.platform');
  requireExact(execution.separatorEntryPoint, EXPECTED.runtime.separatorEntryPoint, 'execution.separatorEntryPoint');

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
  const packageLock = requireObject(evidence.packageLock, 'evidence.packageLock');
  requireExact(packageLock.path, EXPECTED.runtime.packageLockPath, 'evidence.packageLock.path');
  requireDigest(packageLock.sha256, SHA256, 'evidence.packageLock.sha256');
  requireExact(packageLock.sha256, EXPECTED.runtime.packageLockSha256, 'evidence.packageLock.sha256');
  requireExact(packageLock.packageCount, EXPECTED.runtime.packageCount, 'evidence.packageLock.packageCount');
  requireExact(packageLock.resolutionVerified, true, 'evidence.packageLock.resolutionVerified');

  const blockers = [];
  if (evidence.packageInstallationVerified !== true) blockers.push('PACKAGE_INSTALLATION_UNVERIFIED');
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
