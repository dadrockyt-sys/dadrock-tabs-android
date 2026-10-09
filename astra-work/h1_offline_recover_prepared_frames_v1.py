#!/usr/bin/env python3
"""Read-only reconciliation of an ALREADY DOWNLOADED scalar-only V9 audit ZIP.

Does not import Astra, Torch, NumPy, media or network tools. Never runs inference,
training, a workflow, or a launch gate. Requires the historical allowed JSON only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from statistics import median
from zipfile import ZipFile

ZIP_SHA256 = '3e7d59b40d6311c800a0a5ee85f4ef90a38a0f8d6a17351578108f292604079b'
JSON_SHA256 = '5dbc876c3b77be3dff1f42b52e33f1955a8b96356aff08452e2fa9116aab6f94'
MEMBER = 'post-v9-admission-audit-v1.json'
FOLD_COUNTS = {'p1-train-p2-validate': ('P2', 120), 'p2-train-p1-validate': ('P1', 136)}
BYTES_PER_FRAME = 192 * 4 + 6 * 2
ARCHIVE_ORDER = ('P1_chords.zip','P1_scales.zip','P1_singlenotes.zip','P1_techniques.zip',
                 'P2_chords.zip','P2_scales.zip','P2_singlenotes.zip','P2_techniques.zip')


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def scalar_zip(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError('MISSING_OR_LINKED_SCALAR_ARTIFACT')
    raw = path.read_bytes()
    if digest(raw) != ZIP_SHA256:
        raise ValueError('SCALAR_ARTIFACT_ARCHIVE_IDENTITY_MISMATCH')
    with ZipFile(path) as z:
        members = z.infolist()
        if len(members) != 1 or members[0].filename != MEMBER or members[0].file_size > 3_000_000:
            raise ValueError('UNEXPECTED_SCALAR_ARTIFACT_MEMBERS')
        if (members[0].external_attr >> 16) & 0o170000 != 0o100000:
            raise ValueError('NON_REGULAR_SCALAR_ARTIFACT_MEMBER')
        data = z.read(members[0])
    if digest(data) != JSON_SHA256:
        raise ValueError('SCALAR_ARTIFACT_JSON_IDENTITY_MISMATCH')
    return json.loads(data)


def reconcile(audit: dict, corrections: dict, published: dict,
              fold_counts: dict = FOLD_COUNTS) -> dict:
    if audit.get('schema') != 'astra-guitar-techs-post-v9-fixed-output-admission-audit-v1':
        raise ValueError('UNEXPECTED_SCALAR_SCHEMA')
    if audit.get('guards', {}).get('optimizerStepsExecuted') != 0:
        raise ValueError('UNEXPECTED_NONZERO_OPTIMIZATION')
    if audit.get('manifestSha256') != published.get('execution', {}).get('manifestSha256'):
        raise ValueError('MANIFEST_IDENTITY_MISMATCH')
    accepted = corrections.get('correctionsMs')
    if not isinstance(accepted, dict) or len(accepted) != sum(size for _, size in fold_counts.values()):
        raise ValueError('ACCEPTED_CAPTURE_SET_MISMATCH')
    lookup = {digest(k.encode()): k for k in accepted}
    if len(lookup) != len(accepted):
        raise ValueError('ACCEPTED_HASH_COLLISION')
    if set(audit['folds']) != set(fold_counts):
        raise ValueError('FOLD_SET_MISMATCH')
    found = {}
    fold_result = {}
    for fold, (performer, n) in fold_counts.items():
        versions = audit['folds'][fold]
        if set(versions) != {'v8', 'v9'}:
            raise ValueError('VERSION_SET_MISMATCH')
        by_version = {}
        for version in ('v8', 'v9'):
            captures = versions[version]['captures']
            if len(captures) != n:
                raise ValueError('FOLD_CAPTURE_COUNT_MISMATCH')
            mapping = {}
            for c in captures:
                h = c['captureKeySha256']
                if h not in lookup or not lookup[h].startswith(performer+'|') or h in mapping:
                    raise ValueError('CAPTURE_IDENTITY_MISMATCH')
                frames = c['audit']['frames']
                if type(frames) is not int or frames < 200:
                    raise ValueError('CAPTURE_FRAME_COUNT_INVALID')
                if c['audit']['validPositions'] + c['audit']['maskedPositions'] != 6 * frames:
                    raise ValueError('FRAME_AND_STRING_POSITIONS_MISMATCH')
                mapping[h] = frames
            by_version[version] = mapping
        if by_version['v8'] != by_version['v9']:
            raise ValueError('V8_V9_FRAME_COUNT_DISAGREEMENT')
        if set(found) & set(by_version['v9']):
            raise ValueError('REPEATED_CAPTURE_ACROSS_FOLDS')
        found.update(by_version['v9'])
        frame_sum = sum(by_version['v9'].values())
        stated = published['folds'][fold]
        if (frame_sum != stated['frames'] or frame_sum*6 != stated['stringPositions']
                or len(by_version['v9']) != stated['captures']):
            raise ValueError('PUBLISHED_FOLD_FRAME_SUM_MISMATCH')
        fold_result[fold] = {'captureCount':n,'frames':frame_sum,'minCaptureFrames':min(by_version['v9'].values()),
                             'maxCaptureFrames':max(by_version['v9'].values()),'stringPositions':frame_sum*6}
    if set(found) != set(lookup):
        raise ValueError('FULL_POPULATION_INCOMPLETE')
    if len(found) != published['aggregate']['captures'] or sum(found.values())*6 != published['aggregate']['v9EvaluatedStringPositions']:
        raise ValueError('PUBLISHED_AGGREGATE_FRAME_SUM_MISMATCH')
    archive = {name:[] for name in ARCHIVE_ORDER}
    views = {name:[] for name in ('directinput','micamp','ego','exo')}
    for h, frames in found.items():
        performer, category, _, view = lookup[h].split('|',3)
        bucket=f'{performer}_{category}.zip'
        if bucket not in archive or view not in views:
            raise ValueError('UNEXPECTED_ACCEPTED_GROUP_OR_VIEW')
        archive[bucket].append(frames)
        views[view].append(frames)
    def pack(xs):
        return {'captures':len(xs),'totalFrames':sum(xs),'minFrames':min(xs) if xs else None,'maxFrames':max(xs) if xs else None,
                'featureAndLabelPayloadBytes':sum(xs)*BYTES_PER_FRAME}
    totals = list(found.values())
    return {'schema':'astra-h1-prior-scalar-exact-prepared-frame-recovery-v1',
            'historicalArtifactId':11580776876,'sourceRunId':37836761676,
            'scalarArtifactZipSha256':ZIP_SHA256,'scalarArtifactJsonSha256':JSON_SHA256,
            'population':pack(totals),'medianCaptureFrames':median(totals),
            'folds':fold_result,'byArchive':{k:pack(v) for k,v in archive.items()},
            'byView':{k:pack(v) for k,v in views.items()},
            'identitiesMatched':len(found),'referenceManifestSha256':audit['manifestSha256'],
            'allFramesFromPreviouslyAuthorizedScalarAudit':True,
            'originalMP3FileDurationsKnown':False,'physicalRunnerDiskPeakKnown':False,
            'peakRuntimeRAMKnown':False,'launchPermission':False,'readiness':'NO_GO_INSUFFICIENT_EVIDENCE'}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-zip',type=Path,required=True)
    parser.add_argument('--accepted-json',type=Path,required=True)
    parser.add_argument('--published-json',type=Path,required=True)
    x=parser.parse_args()
    report=reconcile(scalar_zip(x.audit_zip),json.loads(x.accepted_json.read_text()),
                     json.loads(x.published_json.read_text()))
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=='__main__':
    main()
