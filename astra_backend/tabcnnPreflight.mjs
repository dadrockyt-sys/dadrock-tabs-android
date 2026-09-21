const EXPECTED = Object.freeze({
  candidateId: 'tabcnn_guitarprofx_dafx24',
  source: Object.freeze({
    repository: 'robust-guitar-tabs/code',
    revision: 'f50309ad06dc734ddae5e3a0eda756fca221e2e7',
    blobs: Object.freeze({
      trainingScript: '3531fb19292f8b6198ab48c311bee1d6b87ff162',
      inferenceScript: 'cf59fbc2fd6d274d35ea888eb058cdeb7f69b7ed',
      model: 'e09856db2fffd77642e005ab509846acc894b886',
      cqt: '7f08cbd3448765c5406b28f8627a8a8fb66f27b7',
      vqt: 'a4e5e7d4958ec64d2d149eb51acdaf936e649b00',
      featurePostProcessing: '79b71e763bc12d9d8a26d5bcce5b8ff9800bea92',
      audioIo: '3b7c4acce352009393e1b786935704d259888681',
    }),
  }),
  preprocessing: Object.freeze({
    sampleRateHz: 22050,
    mono: true,
    audioNormalization: 'rms',
    hopLengthSamples: 512,
    cqtBins: 192,
    binsPerOctave: 24,
    fmin: 'C1',
    gamma: 0,
    decibelReference: 'max',
    decibelFloorAssumption: -80,
    featureScale: 'db_div_80_plus_1',
    frameContext: 9,
    guitarFrets: 19,
  }),
  artifact: Object.freeze({
    record: 'https://zenodo.org/records/11406378',
    file: 'best_TabCNN_tablature_trancription_model',
    bytes: 3345122,
    md5: 'ce168b2cd426f81a2a78499214e40605',
    sha256: '1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c',
  }),
  reproduction: Object.freeze({
    receiptSha256: '3a9474ccad43f1b06b76bc2e4b836642c355565a1d86a608aed8780a0bf8c333',
    normalizedAudioSha256: '1711cac27e4c3c2d90840ec92faca29c4f343c5d55236d59e8f10c23b573f2b3',
    sourceParityTolerance: 1e-7,
  }),
  runtime: Object.freeze({
    platform: 'linux-x86_64',
    pythonVersion: '3.10.15',
    numpyVersion: '1.21.6',
    scipyVersion: '1.8.1',
    librosaVersion: '0.9.1',
    torchVersion: '1.11.0+cpu',
    dependencyLockSha256: '0e711709b063a705ad11570f6b7ef4dfe5bcc2d433d98707a1a74897dbb25bc0',
    wheelManifestSha256: '0796acee36cea76e9784e602da190223a14a89907381882b401986763c371567',
  }),
  service: Object.freeze({
    maxWallTimeSeconds: 1200,
    maxPeakMemoryMb: 4096,
  }),
});

function nonEmpty(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

function sameObject(actual, expected) {
  if (!actual || typeof actual !== 'object') return false;
  return Object.entries(expected).every(([key, value]) => actual[key] === value);
}

function sourceBlobsMatch(source) {
  return source
    && source.repository === EXPECTED.source.repository
    && source.revision === EXPECTED.source.revision
    && sameObject(source.blobs, EXPECTED.source.blobs);
}

function preprocessingMatches(preprocessing) {
  return sameObject(preprocessing, EXPECTED.preprocessing);
}

function finiteNonNegative(value) {
  return Number.isFinite(value) && value >= 0;
}

export function getExpectedTabcnnPreflightIdentity() {
  return structuredClone(EXPECTED);
}

export function evaluateTabcnnDevelopmentPreflight({
  source = {},
  artifact = {},
  runtime = {},
  preprocessing = {},
  rights = {},
} = {}) {
  const blockers = [];

  if (!sourceBlobsMatch(source)) blockers.push('SOURCE_IDENTITY_MISMATCH');
  if (!preprocessingMatches(preprocessing)) blockers.push('PREPROCESSING_CONTRACT_MISMATCH');
  if (preprocessing.numericalReproductionVerified !== true) {
    blockers.push('PREPROCESSING_NUMERICAL_REPRODUCTION_PENDING');
  }
  if (preprocessing.numericalReproductionReceiptSha256 !== EXPECTED.reproduction.receiptSha256
      || preprocessing.normalizedAudioSha256 !== EXPECTED.reproduction.normalizedAudioSha256) {
    blockers.push('PREPROCESSING_REPRODUCTION_IDENTITY_MISMATCH');
  }
  if (preprocessing.sourceParityVerified !== true
      || !finiteNonNegative(preprocessing.sourceParityMaxAbsoluteDifference)
      || preprocessing.sourceParityMaxAbsoluteDifference > EXPECTED.reproduction.sourceParityTolerance) {
    blockers.push('PREPROCESSING_SOURCE_PARITY_UNVERIFIED');
  }

  if (artifact.record !== EXPECTED.artifact.record
      || artifact.file !== EXPECTED.artifact.file
      || artifact.bytes !== EXPECTED.artifact.bytes) {
    blockers.push('OFFICIAL_ARTIFACT_IDENTITY_MISMATCH');
  }
  if (artifact.downloadedFromOfficialRecord !== true) {
    blockers.push('OFFICIAL_ARTIFACT_NOT_DOWNLOADED');
  }
  if (artifact.publishedMd5Verified !== true
      || artifact.md5 !== EXPECTED.artifact.md5) {
    blockers.push('OFFICIAL_ARTIFACT_MD5_UNVERIFIED');
  }
  if (!nonEmpty(artifact.sha256)
      || !/^[a-f0-9]{64}$/.test(artifact.sha256)
      || artifact.sha256 !== EXPECTED.artifact.sha256) {
    blockers.push('OFFICIAL_ARTIFACT_SHA256_UNVERIFIED');
  }

  if (runtime.dependencyLockComplete !== true
      || runtime.dependencyLockSha256 !== EXPECTED.runtime.dependencyLockSha256
      || runtime.wheelManifestSha256 !== EXPECTED.runtime.wheelManifestSha256) {
    blockers.push('RUNTIME_DEPENDENCY_LOCK_PENDING');
  }
  if (runtime.exactPackageVersionsFrozen !== true
      || runtime.platform !== EXPECTED.runtime.platform
      || runtime.pythonVersion !== EXPECTED.runtime.pythonVersion
      || runtime.numpyVersion !== EXPECTED.runtime.numpyVersion
      || runtime.scipyVersion !== EXPECTED.runtime.scipyVersion
      || runtime.librosaVersion !== EXPECTED.runtime.librosaVersion
      || runtime.torchVersion !== EXPECTED.runtime.torchVersion) {
    blockers.push('RUNTIME_PACKAGE_VERSIONS_UNFROZEN');
  }
  if (runtime.cpuSmokeTestPassed !== true) {
    blockers.push('CPU_SMOKE_TEST_PENDING');
  }
  if (!nonEmpty(runtime.cpuSmokeReceiptSha256)) {
    blockers.push('CPU_SMOKE_RECEIPT_MISSING');
  }
  if (!finiteNonNegative(runtime.wallTimeSeconds)
      || runtime.wallTimeSeconds > EXPECTED.service.maxWallTimeSeconds) {
    blockers.push('CPU_WALL_TIME_OUT_OF_BUDGET');
  }
  if (!finiteNonNegative(runtime.peakMemoryMb)
      || runtime.peakMemoryMb > EXPECTED.service.maxPeakMemoryMb) {
    blockers.push('CPU_MEMORY_OUT_OF_BUDGET');
  }

  if (rights.checkpointLicenseReviewed !== true) {
    blockers.push('CHECKPOINT_LICENSE_REVIEW_PENDING');
  }
  if (rights.trainingDataCommercialRightsReviewed !== true) {
    blockers.push('TRAINING_DATA_COMMERCIAL_RIGHTS_REVIEW_PENDING');
  }
  if (rights.trainingDataCommercialRightsCleared !== true) {
    blockers.push('TRAINING_DATA_COMMERCIAL_RIGHTS_UNRESOLVED');
  }
  if (rights.developmentUseAuthorized !== true) {
    blockers.push('DEVELOPMENT_USE_NOT_AUTHORIZED');
  }

  const uniqueBlockers = [...new Set(blockers)].sort();

  return {
    contract: {
      name: 'astra-tabcnn-development-preflight',
      version: 1,
      invokesModel: false,
      downloadsArtifact: false,
      opensAudio: false,
      performsNetworkAccess: false,
      mutatesProduction: false,
      grantsCustomerDelivery: false,
    },
    candidateId: EXPECTED.candidateId,
    expected: getExpectedTabcnnPreflightIdentity(),
    checks: {
      sourceIdentityVerified: sourceBlobsMatch(source),
      preprocessingIdentityVerified: preprocessingMatches(preprocessing),
      preprocessingNumericallyReproduced: preprocessing.numericalReproductionVerified === true
        && preprocessing.numericalReproductionReceiptSha256 === EXPECTED.reproduction.receiptSha256
        && preprocessing.normalizedAudioSha256 === EXPECTED.reproduction.normalizedAudioSha256
        && preprocessing.sourceParityVerified === true
        && finiteNonNegative(preprocessing.sourceParityMaxAbsoluteDifference)
        && preprocessing.sourceParityMaxAbsoluteDifference <= EXPECTED.reproduction.sourceParityTolerance,
      officialArtifactIdentityVerified: artifact.record === EXPECTED.artifact.record
        && artifact.file === EXPECTED.artifact.file
        && artifact.bytes === EXPECTED.artifact.bytes,
      officialArtifactDigestVerified: artifact.downloadedFromOfficialRecord === true
        && artifact.publishedMd5Verified === true
        && artifact.md5 === EXPECTED.artifact.md5
        && nonEmpty(artifact.sha256)
        && /^[a-f0-9]{64}$/.test(artifact.sha256)
        && artifact.sha256 === EXPECTED.artifact.sha256,
      runtimeLockVerified: runtime.dependencyLockComplete === true
        && runtime.exactPackageVersionsFrozen === true
        && runtime.dependencyLockSha256 === EXPECTED.runtime.dependencyLockSha256
        && runtime.wheelManifestSha256 === EXPECTED.runtime.wheelManifestSha256
        && runtime.platform === EXPECTED.runtime.platform
        && runtime.pythonVersion === EXPECTED.runtime.pythonVersion
        && runtime.numpyVersion === EXPECTED.runtime.numpyVersion
        && runtime.scipyVersion === EXPECTED.runtime.scipyVersion
        && runtime.librosaVersion === EXPECTED.runtime.librosaVersion
        && runtime.torchVersion === EXPECTED.runtime.torchVersion,
      cpuBudgetVerified: runtime.cpuSmokeTestPassed === true
        && nonEmpty(runtime.cpuSmokeReceiptSha256)
        && finiteNonNegative(runtime.wallTimeSeconds)
        && runtime.wallTimeSeconds <= EXPECTED.service.maxWallTimeSeconds
        && finiteNonNegative(runtime.peakMemoryMb)
        && runtime.peakMemoryMb <= EXPECTED.service.maxPeakMemoryMb,
      rightsVerified: rights.checkpointLicenseReviewed === true
        && rights.trainingDataCommercialRightsReviewed === true
        && rights.trainingDataCommercialRightsCleared === true
        && rights.developmentUseAuthorized === true,
    },
    developmentExecutionReady: uniqueBlockers.length === 0,
    blockers: uniqueBlockers,
    customerDeliveryEligible: false,
  };
}
