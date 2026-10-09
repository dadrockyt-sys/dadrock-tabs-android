"""Read-only, model-free audit of the inactive H1 workflow's time budget.

Does not dispatch workflows, download media, or authorize a launch.
"""
from __future__ import annotations
import json
from pathlib import Path
import re

WALL_LIMIT_SECONDS=300*60
ARCHIVES={
    'P1_chords.zip':981741162,'P1_scales.zip':453349723,
    'P1_singlenotes.zip':108626613,'P1_techniques.zip':326280863,
    'P2_chords.zip':1150819056,'P2_scales.zip':471254783,
    'P2_singlenotes.zip':116133457,'P2_techniques.zip':395839610,
}
REQUIRED_STAGE_EVIDENCE=(
    'environmentAndDependencies', 'sourceAcquisition', 'archivesAndPreparation',
    'originalFold1Training', 'originalFold2Training',
    'treatmentFold1Training', 'treatmentFold2Training',
    'originalFold1Evaluation', 'originalFold2Evaluation',
    'treatmentFold1Evaluation', 'treatmentFold2Evaluation',
    'uploadCleanupReserve',
)


def workflow_budget_audit(workflow_text):
    """Audit observed workflow text; do not silently assume new retry semantics."""
    raw=[]
    for line in workflow_text.splitlines():
        columns=line.strip().split()
        if len(columns)==6 and columns[0].startswith(('P1_','P2_')) and columns[0].endswith('.zip'):
            if not columns[1].isdecimal():
                raise ValueError('invalid archive byte count')
            raw.append((columns[0],int(columns[1])))
    found=dict(raw)
    if len(raw)!=8 or len(found)!=8 or found!=ARCHIVES:
        raise RuntimeError('FROZEN_EIGHT_ARCHIVE_IDENTITY_MISMATCH')
    # These exact tokens are present in the currently frozen H1 workflow.
    # Fail closed if future workflow versions alter the retry grammar.
    for token in ('for url in ', 'for attempt in 1 2 3 4 5;',
                  '--max-time 1800','--retry 2', 'timeout-minutes: 300'):
        if token not in workflow_text:
            raise RuntimeError('UNKNOWN_WORKFLOW_RETRY_OR_TIMEOUT_SEMANTICS')
    urls=2
    outer_attempts=5
    inner_attempts=3  # curl --retry 2 means up to 3 requests
    max_seconds=1800
    attempts_per_archive=urls*outer_attempts*inner_attempts
    return {
        'schema':'astra-h1-static-workflow-budget-audit-v1',
        'archiveCount':len(ARCHIVES),
        'compressedInputBytes':sum(ARCHIVES.values()),
        'configuredRunnerLimitSeconds':WALL_LIMIT_SECONDS,
        'curlPotentialAttemptsPerArchive':attempts_per_archive,
        'singleArchiveRequestCeilingSeconds':attempts_per_archive*max_seconds,
        'allArchivesRequestCeilingSeconds':len(ARCHIVES)*attempts_per_archive*max_seconds,
        'downloadWorstCaseExceedsRunnerLimit':len(ARCHIVES)*attempts_per_archive*max_seconds>WALL_LIMIT_SECONDS,
        'readiness':'UNPROVEN_BLOCKED',
        'warning':'Conservative bound ignores additional backoffs, installs, preparation, 160 training steps and four evaluations.',
    }


def stage_budget_review(stage_seconds):
    """Return a structural forecast ONLY when real historical stage evidence exists."""
    missing=[name for name in REQUIRED_STAGE_EVIDENCE if name not in stage_seconds]
    if missing:
        return {'readiness':'UNPROVEN_BLOCKED', 'missingStages':missing}
    if set(stage_seconds)!=set(REQUIRED_STAGE_EVIDENCE):
        raise ValueError('unexpected timing stages')
    duration=0.0
    for stage in REQUIRED_STAGE_EVIDENCE:
        row=stage_seconds[stage]
        if not isinstance(row,dict) or set(row)!={'seconds','evidenceRunId'}:
            raise ValueError('stage lacks original run provenance')
        seconds=row['seconds']
        if type(seconds) not in (int,float) or not 0 <= seconds < float('inf'):
            raise ValueError('invalid stage duration')
        if type(row['evidenceRunId']) is not int or row['evidenceRunId']<=0:
            raise ValueError('missing authoritative timing run ID')
        duration+=seconds
    return {
        'readiness':'UNPROVEN_BLOCKED' if duration<=WALL_LIMIT_SECONDS else 'INFEASIBLE_BOUND',
        'evidenceTotalSeconds':duration,
        'remainingSeconds':WALL_LIMIT_SECONDS-duration,
        'warning':'Even a total below the ceiling needs runner comparability, disk/RAM, provenance and independent review.',
    }


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--workflow',required=True)
    p.add_argument('--timings')
    args=p.parse_args()
    audit=workflow_budget_audit(Path(args.workflow).read_text())
    audit['stageReview']=stage_budget_review(json.loads(Path(args.timings).read_text()) if args.timings else {})
    print(json.dumps(audit,sort_keys=True,indent=2))


if __name__=='__main__': main()
