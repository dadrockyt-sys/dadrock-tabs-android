#!/usr/bin/env python3
"""Paper-only H1 feasibility evidence review. Does NOT launch or measure H1.

Reads previous scalar JSON receipts plus an optional human-filled evidence worksheet.
No model/module imports, subprocesses, media, network, Actions or artifact writes.
Output is NEVER authorization to run a study; independent safety gates apply.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

LIMIT_SECONDS = 18_000
SOURCE_ANCHORS = {
    'framesGitBlob': '701d4626de0e04200534ed17827db00c896a3d6b',
    'stageCapacityGitBlob': 'e8375ec0cd132eadda93456a023df77a88153eda',
    'priorV9TimingsGitBlob': '309bbe19d6e52083237bd8f10d0998623bea6e80',
    'dormantWorkflowGitBlob': '90e8168fc1ca40738ba07291ca1001a36718f4e3',
}
STAGES = (
    'environmentAndDependencies', 'sourceAcquisition', 'archivesAndPreparation',
    'originalFold1Training', 'originalFold2Training',
    'treatmentFold1Training', 'treatmentFold2Training',
    'originalFold1Evaluation', 'originalFold2Evaluation',
    'treatmentFold1Evaluation', 'treatmentFold2Evaluation',
    'uploadCleanupReserve',
)
RESOURCE_KEYS = ('availableDiskBytesAtJobStart', 'peakAdditionalDiskBytes',
                 'diskReserveBytes', 'availableRamBytes', 'peakResidentRamBytes',
                 'ramReserveBytes')
EVIDENCE_SCHEMA = 'astra-h1-human-feasibility-measurement-worksheet-v1'
SHA256 = re.compile(r'[a-f0-9]{64}\Z')


def read_json_regular(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.resolve() != path.absolute():
        raise ValueError('INPUT_FILE_MISSING_OR_SYMLINK')
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('INPUT_MUST_BE_JSON_OBJECT')
    return data


def read_pinned_json_regular(path: Path, expected_blob: str) -> dict:
    if path.is_symlink() or not path.is_file() or path.resolve() != path.absolute():
        raise ValueError('PINNED_INPUT_FILE_MISSING_OR_SYMLINK')
    raw = path.read_bytes()
    actual = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if actual != expected_blob:
        raise ValueError('PRIOR_SOURCE_BLOB_MISMATCH')
    result = json.loads(raw)
    if not isinstance(result, dict):
        raise ValueError('INPUT_MUST_BE_JSON_OBJECT')
    return result


def evidence_template() -> dict:
    return {
        'schema': EVIDENCE_SCHEMA,
        'sourceAnchors': dict(SOURCE_ANCHORS),
        'stageUpperBounds': {stage: None for stage in STAGES},
        'runnerResources': {k: None for k in RESOURCE_KEYS},
        'runnerEvidence': None,
        'documentation': {
            'notes': 'UNMEASURED; historical V9 timings are illustrative, not H1 maxima.',
            'independentSourceAndPackageReview': 'PENDING',
            'sharedAtomicOneUseControlReview': 'PENDING',
            'writtenSupportCase16795041': 'PENDING',
        },
    }


def source_consistency(frames: dict, capacity: dict, timings: dict) -> dict:
    if (frames.get('schema') != 'astra-h1-prior-scalar-exact-prepared-frame-recovery-v1'
            or capacity.get('schema') != 'astra-h1-exact-prior-scalar-stage-capacity-review-v1'
            or timings.get('schema') != 'astra-h1-prior-v9-preparation-log-reconciliation-v1'):
        raise ValueError('UNEXPECTED_PRIOR_RECEIPT_SCHEMA')
    p = frames['population']
    if (p.get('captures') != 256 or p.get('totalFrames') != 1_924_805
            or p.get('maxFrames') != 23_773
            or p.get('featureAndLabelPayloadBytes') != p['totalFrames'] * 780):
        raise ValueError('FROZEN_PREPARED_FRAME_AGGREGATE_DRIFT')
    archives = capacity['perArchiveSequentialStages']
    if (len(archives) != 8 or sum(x['exactPreparedFrames'] for x in archives) != p['totalFrames']
            or sum(x['thisArchivePreparedArrayPayloadBytes'] for x in archives) != p['featureAndLabelPayloadBytes']
            or capacity.get('completePreparedArrayPayloadBytes') != p['featureAndLabelPayloadBytes']):
        raise ValueError('PER_ARCHIVE_CAPACITY_RECONCILIATION_FAILURE')
    peak = max(max(row[k] for k in ('modeledZipPlusExtractionBytes',
                                   'modeledEndOfPreparationBytes',
                                   'modeledAfterArchiveCleanupBytes')) for row in archives)
    if (peak != 4_391_923_097 or
            capacity.get('largestIdentifiableStage', {}).get('historicalLogicalPlusExactPreparedPayloadBytes') != peak):
        raise ValueError('HISTORICAL_LOGICAL_OVERLAP_DRIFT')
    jobs = timings['jobs']
    elapsed = [x['prepElapsedSeconds'] for x in jobs]
    if (len(jobs) != 10 or not all(x['preparedCaptureTotal'] == 256 for x in jobs)
            or min(elapsed) != 1551.28 or max(elapsed) != 3416.914):
        raise ValueError('V9_HISTORICAL_PREPARATION_DRIFT')
    return {
        'historicPreparedFrames': p['totalFrames'],
        'largestHistoricCaptureFrames': p['maxFrames'],
        'historicPreparedPayloadBytes': p['featureAndLabelPayloadBytes'],
        'historicLogicalOverlapScenarioBytes': peak,
        'v9HistoricPrepObservedMinSeconds': min(elapsed),
        'v9HistoricPrepObservedMaxSeconds': max(elapsed),
        'priorReceiptsReconciled': True,
        'noneOfTheseAreH1ResourceUpperBounds': True,
    }


def _whole_nonnegative(value: object) -> bool:
    return type(value) is int and value >= 0


def _finite_positive_seconds(value: object) -> bool:
    return type(value) in (float, int) and math.isfinite(value) and value > 0


def examine_evidence(worksheet: dict, reconciled: dict) -> dict:
    if worksheet.get('schema') != EVIDENCE_SCHEMA or worksheet.get('sourceAnchors') != SOURCE_ANCHORS:
        raise ValueError('FEASIBILITY_WORKSHEET_SOURCE_IDENTITY_MISMATCH')
    if set(worksheet) != {'schema', 'sourceAnchors', 'stageUpperBounds', 'runnerResources',
                           'runnerEvidence', 'documentation'}:
        raise ValueError('FEASIBILITY_WORKSHEET_UNEXPECTED_FIELDS')
    stages = worksheet['stageUpperBounds']
    resources = worksheet['runnerResources']
    if not isinstance(stages, dict) or set(stages) != set(STAGES):
        raise ValueError('INCORRECT_TWELVE_STAGE_SET')
    if not isinstance(resources, dict) or set(resources) != set(RESOURCE_KEYS):
        raise ValueError('INCORRECT_RESOURCE_FIELD_SET')
    missing = []
    stage_values = {}
    for name, row in stages.items():
        if row is None:
            missing.append('stage:'+name)
            continue
        if not isinstance(row, dict) or set(row) != {'upperBoundSeconds', 'evidenceRunId', 'evidenceSha256'}:
            raise ValueError('STAGE_PROVENANCE_REQUIRED:'+name)
        if (not _finite_positive_seconds(row['upperBoundSeconds']) or
                type(row['evidenceRunId']) is not int or row['evidenceRunId'] < 1 or
                not isinstance(row['evidenceSha256'], str) or not SHA256.fullmatch(row['evidenceSha256'])):
            raise ValueError('INVALID_STAGE_BOUND_OR_PROVENANCE:'+name)
        stage_values[name] = row['upperBoundSeconds']
    for name, number in resources.items():
        if number is None:
            missing.append('resource:'+name)
        elif not _whole_nonnegative(number):
            raise ValueError('INVALID_RESOURCE_BYTE_COUNT:'+name)
    resourceEvidence = worksheet['runnerEvidence']
    if resourceEvidence is None:
        missing.append('runnerEvidence')
    elif (not isinstance(resourceEvidence, dict) or
          set(resourceEvidence) != {'runId', 'evidenceSha256', 'runnerImage'} or
          type(resourceEvidence['runId']) is not int or resourceEvidence['runId'] < 1 or
          not isinstance(resourceEvidence['evidenceSha256'], str) or
          not SHA256.fullmatch(resourceEvidence['evidenceSha256']) or
          resourceEvidence['runnerImage'] != 'ubuntu-22.04'):
        raise ValueError('INVALID_RUNNER_EVIDENCE_REFERENCE')
    if not isinstance(worksheet['documentation'], dict) or set(worksheet['documentation']) != {
        'notes', 'independentSourceAndPackageReview',
        'sharedAtomicOneUseControlReview', 'writtenSupportCase16795041'}:
        raise ValueError('INVALID_DOCUMENTATION_SECTION')
    if (not all(isinstance(x, str) and x for x in worksheet['documentation'].values()) or
            any(worksheet['documentation'][key] != 'PENDING' for key in
                ('independentSourceAndPackageReview', 'sharedAtomicOneUseControlReview',
                 'writtenSupportCase16795041'))):
        raise ValueError('REVIEW_AND_SUPPORT_GATES_CANNOT_BE_SELF_APPROVED_HERE')
    total = sum(stage_values.values()) if not any(k.startswith('stage:') for k in missing) else None
    disk_remaining = None
    ram_remaining = None
    if all(resources[k] is not None for k in
           ('availableDiskBytesAtJobStart', 'peakAdditionalDiskBytes', 'diskReserveBytes')):
        disk_remaining = (resources['availableDiskBytesAtJobStart']-
                          resources['peakAdditionalDiskBytes']-resources['diskReserveBytes'])
    if all(resources[k] is not None for k in
           ('availableRamBytes', 'peakResidentRamBytes', 'ramReserveBytes')):
        ram_remaining = (resources['availableRamBytes']-
                         resources['peakResidentRamBytes']-resources['ramReserveBytes'])
    # Resource measurement lower than a prior *modeled* overlap is a review discrepancy,
    # not a hard contradiction: historical extraction is NOT an H1 measured lower bound.
    floor_discrepancy = (resources['peakAdditionalDiskBytes'] is not None and
        resources['peakAdditionalDiskBytes'] < reconciled['historicLogicalOverlapScenarioBytes'])
    failed = (total is not None and total > LIMIT_SECONDS) or (
        disk_remaining is not None and disk_remaining < 0) or (
        ram_remaining is not None and ram_remaining < 0)
    return {
        'schema': 'astra-h1-paper-only-feasibility-review-result-v1',
        'sourceVerification': reconciled,
        'missingEvidence': sorted(missing),
        'completeTwelveStageBoundSeconds': total,
        'remainingBefore300MinSeconds': None if total is None else LIMIT_SECONDS-total,
        'diskHeadroomAfterReserveBytes': disk_remaining,
        'ramHeadroomAfterReserveBytes': ram_remaining,
        'reviewHistoricalOverlapDiscrepancy': bool(floor_discrepancy),
        'technicalPaperReviewStatus': ('BLOCKED_BOUND_EXCEEDS_LIMIT' if failed else
               'BLOCKED_MISSING_EVIDENCE' if missing else
               'PAPER_PACKAGE_AWAITS_EXTERNAL_VERIFICATION'),
        'actualRunnerTelemetryProvenByThisTool': False,
        'independentLaunchReview': 'PENDING',
        'writtenSupportApproval': 'PENDING',
        'launchPermission': False,
        'realMediaAccessed': False,
        'trainingExecuted': False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--frames', type=Path, required=True, help='Existing scalar-only frame receipt')
    p.add_argument('--capacity', type=Path, required=True, help='Existing scalar-only capacity receipt')
    p.add_argument('--timings', type=Path, required=True, help='Existing historical V9 timing receipt')
    p.add_argument('--worksheet', type=Path, help='Optional human-collected evidence; absent means all unknown')
    args = p.parse_args()
    sources = source_consistency(
        read_pinned_json_regular(args.frames, SOURCE_ANCHORS['framesGitBlob']),
        read_pinned_json_regular(args.capacity, SOURCE_ANCHORS['stageCapacityGitBlob']),
        read_pinned_json_regular(args.timings, SOURCE_ANCHORS['priorV9TimingsGitBlob']))
    worksheet = read_json_regular(args.worksheet) if args.worksheet else evidence_template()
    print(json.dumps(examine_evidence(worksheet,sources),indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
