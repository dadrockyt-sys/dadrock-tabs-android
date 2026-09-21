const EXPECTED = Object.freeze({
  record: 'https://zenodo.org/records/14963133',
  version: 'v1',
  license: Object.freeze({
    id: 'CC-BY-4.0',
    repository: 'guitar-techs/guitar-techs.github.io',
    revision: '19a2954f789bfd192b2b4732788ceb000c1dd687',
    indexBlob: '64627b4fb227cd0e29cff05926f02fe0e12b5f26',
  }),
  manifestSha256: 'a3445d799c4a0b17a0078dac0c9387a0e676111367a5f07d608fd55bd8118e52',
  splitReceiptSha256: 'd116556c13d250af28900bb1d73d2c0ccd3130246db8bdd2d6d387ac87be799a',
  totalPublishedBytes: 4133550356,
  archives: Object.freeze([
    Object.freeze({ file: 'P1_chords.zip', bytes: 981741162, md5: 'be9ef8bbdceb1912d565254e607a6d94' }),
    Object.freeze({ file: 'P1_scales.zip', bytes: 453349723, md5: '9c0b98e8fb42a522df727ea8bf545e4f' }),
    Object.freeze({ file: 'P1_singlenotes.zip', bytes: 108626613, md5: 'ca0c4674dde3805574685a313f7c39eb' }),
    Object.freeze({ file: 'P1_techniques.zip', bytes: 326280863, md5: '18634a41a6db5a8de10d07eb3122a872' }),
    Object.freeze({ file: 'P2_chords.zip', bytes: 1150819056, md5: 'eb6f74dd19162237189281688ad7ad2e' }),
    Object.freeze({ file: 'P2_scales.zip', bytes: 471254783, md5: '96664853872f51e5f8aa4447313b7cf5' }),
    Object.freeze({ file: 'P2_singlenotes.zip', bytes: 116133457, md5: '40fbf03d8b04bb2cf42df20f36dc2254' }),
    Object.freeze({ file: 'P2_techniques.zip', bytes: 395839610, md5: 'f4189251ce50be25f06a173b2c2bba00' }),
    Object.freeze({ file: 'P3_music.zip', bytes: 129505089, md5: '071ba80aecf00f4a31fbd167b3f22198' }),
  ]),
});

function archivesMatch(actual) {
  if (!Array.isArray(actual) || actual.length !== EXPECTED.archives.length) return false;
  return EXPECTED.archives.every((expected, index) => {
    const archive = actual[index];
    return archive?.file === expected.file
      && archive?.bytes === expected.bytes
      && archive?.md5 === expected.md5;
  });
}

export function getExpectedGuitarTechsPublishedIdentity() {
  return structuredClone(EXPECTED);
}

export function evaluateGuitarTechsDatasetAdmission({
  record,
  version,
  license = {},
  archives = [],
  manifestSha256,
  splitReceiptSha256,
  astraArchiveSha256Complete = false,
  trainingMediaAcquired = false,
  extractedPerformanceGroupingVerified = false,
} = {}) {
  const blockers = [];
  if (record !== EXPECTED.record || version !== EXPECTED.version) {
    blockers.push('GUITAR_TECHS_RECORD_IDENTITY_MISMATCH');
  }
  if (license.id !== EXPECTED.license.id
      || license.repository !== EXPECTED.license.repository
      || license.revision !== EXPECTED.license.revision
      || license.indexBlob !== EXPECTED.license.indexBlob) {
    blockers.push('GUITAR_TECHS_LICENSE_EVIDENCE_MISMATCH');
  }
  if (!archivesMatch(archives) || manifestSha256 !== EXPECTED.manifestSha256) {
    blockers.push('GUITAR_TECHS_PUBLISHED_ARCHIVE_IDENTITY_MISMATCH');
  }
  if (splitReceiptSha256 !== EXPECTED.splitReceiptSha256) {
    blockers.push('GUITAR_TECHS_SPLIT_RECEIPT_MISMATCH');
  }
  if (astraArchiveSha256Complete !== true) {
    blockers.push('GUITAR_TECHS_ASTRA_SHA256_PENDING');
  }
  if (trainingMediaAcquired !== true) {
    blockers.push('GUITAR_TECHS_MEDIA_NOT_ACQUIRED');
  }
  if (extractedPerformanceGroupingVerified !== true) {
    blockers.push('GUITAR_TECHS_EXTRACTED_GROUPING_PENDING');
  }

  const uniqueBlockers = [...new Set(blockers)].sort();
  return {
    contract: {
      name: 'astra-guitar-techs-dataset-admission',
      version: 1,
      downloadsTrainingMedia: false,
      opensTrainingMedia: false,
      trainsModel: false,
      grantsCustomerDelivery: false,
    },
    expected: getExpectedGuitarTechsPublishedIdentity(),
    metadataIdentityVerified: !uniqueBlockers.some((blocker) => [
      'GUITAR_TECHS_RECORD_IDENTITY_MISMATCH',
      'GUITAR_TECHS_LICENSE_EVIDENCE_MISMATCH',
      'GUITAR_TECHS_PUBLISHED_ARCHIVE_IDENTITY_MISMATCH',
      'GUITAR_TECHS_SPLIT_RECEIPT_MISMATCH',
    ].includes(blocker)),
    trainingMediaAdmissionReady: uniqueBlockers.length === 0,
    blockers: uniqueBlockers,
    customerDeliveryEligible: false,
  };
}
