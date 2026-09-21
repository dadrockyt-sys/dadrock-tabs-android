const CONTRACT = Object.freeze({
  "schema": "astra-guitar-techs-development-acquisition-contract-v1",
  "dataset": "Guitar-TECHS",
  "record": "https://zenodo.org/records/14963133",
  "version": "v1",
  "authorizationScope": "guitar-techs-p1-p2-development-media-v1",
  "developmentArchives": [
    {
      "file": "P1_chords.zip",
      "bytes": 981741162,
      "md5": "be9ef8bbdceb1912d565254e607a6d94",
      "performer": "P1",
      "category": "chords"
    },
    {
      "file": "P1_scales.zip",
      "bytes": 453349723,
      "md5": "9c0b98e8fb42a522df727ea8bf545e4f",
      "performer": "P1",
      "category": "scales"
    },
    {
      "file": "P1_singlenotes.zip",
      "bytes": 108626613,
      "md5": "ca0c4674dde3805574685a313f7c39eb",
      "performer": "P1",
      "category": "singlenotes"
    },
    {
      "file": "P1_techniques.zip",
      "bytes": 326280863,
      "md5": "18634a41a6db5a8de10d07eb3122a872",
      "performer": "P1",
      "category": "techniques"
    },
    {
      "file": "P2_chords.zip",
      "bytes": 1150819056,
      "md5": "eb6f74dd19162237189281688ad7ad2e",
      "performer": "P2",
      "category": "chords"
    },
    {
      "file": "P2_scales.zip",
      "bytes": 471254783,
      "md5": "96664853872f51e5f8aa4447313b7cf5",
      "performer": "P2",
      "category": "scales"
    },
    {
      "file": "P2_singlenotes.zip",
      "bytes": 116133457,
      "md5": "40fbf03d8b04bb2cf42df20f36dc2254",
      "performer": "P2",
      "category": "singlenotes"
    },
    {
      "file": "P2_techniques.zip",
      "bytes": 395839610,
      "md5": "f4189251ce50be25f06a173b2c2bba00",
      "performer": "P2",
      "category": "techniques"
    }
  ],
  "sealedArchives": [
    {
      "file": "P3_music.zip",
      "bytes": 129505089,
      "md5": "071ba80aecf00f4a31fbd167b3f22198",
      "performer": "P3",
      "category": "music",
      "reason": "sealed-final-generalization-gate"
    }
  ],
  "totalDevelopmentBytes": 4004045267,
  "requirements": {
    "explicitAuthorizationRequired": true,
    "publishedByteCountRequired": true,
    "publishedMd5Required": true,
    "astraSha256RequiredAfterDownload": true,
    "p3DownloadForbidden": true,
    "archiveExtractionBeforeIdentityVerificationForbidden": true,
    "trainingBeforeGroupingTuningAlignmentReceiptsForbidden": true
  }
});

const DEVELOPMENT_BY_FILE = new Map(
  CONTRACT.developmentArchives.map((archive) => [archive.file, archive]),
);
const SEALED_FILES = new Set(CONTRACT.sealedArchives.map((archive) => archive.file));

function exactArchiveMatch(actual, expected) {
  return actual
    && actual.file === expected.file
    && actual.bytes === expected.bytes
    && actual.md5 === expected.md5
    && actual.performer === expected.performer
    && actual.category === expected.category;
}

export function getGuitarTechsDevelopmentAcquisitionContract() {
  return structuredClone(CONTRACT);
}

export function evaluateGuitarTechsDevelopmentAcquisitionRequest({
  record,
  version,
  authorizationScope,
  developmentMediaAcquisitionAuthorized = false,
  requestedArchives = [],
} = {}) {
  const blockers = [];

  if (record !== CONTRACT.record || version !== CONTRACT.version) {
    blockers.push('GUITAR_TECHS_ACQUISITION_RECORD_IDENTITY_MISMATCH');
  }
  if (developmentMediaAcquisitionAuthorized !== true
      || authorizationScope !== CONTRACT.authorizationScope) {
    blockers.push('GUITAR_TECHS_DEVELOPMENT_MEDIA_ACQUISITION_NOT_AUTHORIZED');
  }
  if (!Array.isArray(requestedArchives) || requestedArchives.length === 0) {
    blockers.push('GUITAR_TECHS_DEVELOPMENT_ARCHIVE_SELECTION_EMPTY');
  } else {
    const names = new Set();
    for (const archive of requestedArchives) {
      if (SEALED_FILES.has(archive?.file)) {
        blockers.push('GUITAR_TECHS_P3_SEALED');
        continue;
      }
      const expected = DEVELOPMENT_BY_FILE.get(archive?.file);
      if (!expected || !exactArchiveMatch(archive, expected)) {
        blockers.push('GUITAR_TECHS_DEVELOPMENT_ARCHIVE_IDENTITY_MISMATCH');
        continue;
      }
      if (names.has(archive.file)) {
        blockers.push('GUITAR_TECHS_DEVELOPMENT_ARCHIVE_DUPLICATE');
        continue;
      }
      names.add(archive.file);
    }
  }

  const uniqueBlockers = [...new Set(blockers)].sort();
  const selectedFiles = Array.isArray(requestedArchives)
    ? requestedArchives.map((archive) => archive?.file).filter(Boolean)
    : [];
  const exactDevelopmentSelection = selectedFiles.length === CONTRACT.developmentArchives.length
    && CONTRACT.developmentArchives.every(({ file }) => selectedFiles.includes(file))
    && new Set(selectedFiles).size === CONTRACT.developmentArchives.length;

  return {
    contract: {
      name: 'astra-guitar-techs-development-acquisition-request',
      version: 1,
      downloadsMedia: false,
      opensMedia: false,
      extractsMedia: false,
      trainsModel: false,
      opensP3: false,
      grantsCustomerDelivery: false,
    },
    dataset: CONTRACT.dataset,
    record: CONTRACT.record,
    version: CONTRACT.version,
    authorizationScope: CONTRACT.authorizationScope,
    requestedArchiveCount: selectedFiles.length,
    fullDevelopmentSetSelected: exactDevelopmentSelection,
    acquisitionPlanAccepted: uniqueBlockers.length === 0,
    blockers: uniqueBlockers,
    nextRequiredEvidence: uniqueBlockers.length === 0
      ? [
        'VERIFY_DOWNLOADED_BYTES_AND_PUBLISHED_MD5',
        'COMPUTE_ASTRA_SHA256_BEFORE_EXTRACTION',
        'FREEZE_EXTRACTED_GROUPING_STRING_MAP_TUNING_RECEIPTS',
      ]
      : [],
    p3Sealed: true,
    customerDeliveryEligible: false,
  };
}
