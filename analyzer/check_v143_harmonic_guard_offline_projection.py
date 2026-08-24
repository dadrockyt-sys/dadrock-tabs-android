#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import math
import os
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
OLD_PRODUCT = ROOT / "debug" / "v143-contextual-prune" / "repaired-timing-precision-candidate-product.json"
OUTPUT = ROOT / "debug" / "v143-contextual-prune" / "harmonic-guard-offline-projection-proof.json"
RETIRED_RENDER_SHA = "a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb"
EXPECTED_PROTECTED = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"
HARMONIC_INTERVALS = {12, 19, 24, 28, 31, 36}


def finite(value: Any, fallback: float = -99.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    return number if math.isfinite(number) else fallback


def key_of(event: Mapping[str, Any]) -> tuple[int, int]:
    return int(event["measure"]), int(event["step"])


def strongest_hypothesis(group: list[dict[str, Any]]) -> int | None:
    raw = group[0].get("pitchHypotheses")
    hypotheses = raw if isinstance(raw, list) else []
    by_midi: dict[int, Mapping[str, Any]] = {}
    for item in hypotheses:
        if isinstance(item, Mapping) and item.get("midi") is not None:
            by_midi[int(item["midi"])] = item
    if not by_midi:
        return None
    return max(
        by_midi,
        key=lambda midi: (
            finite(by_midi[midi].get("physicalScore")),
            finite(by_midi[midi].get("physicalAttack")),
            -int(midi),
        ),
    )


def projection_sha(product_path: Path, work: Path, label: str) -> tuple[str, int]:
    freeze_path = work / f"{label}-freeze-input.json"
    log_path = work / f"{label}-prepare.log"
    with log_path.open("w", encoding="utf-8") as log:
        result = subprocess.run(
            [
                "node",
                "validation/rhythm_holdout/prepare_repaired_timing_precision_candidate_freeze_payload.mjs",
                str(product_path),
                str(freeze_path),
            ],
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    if result.returncode != 0:
        tail = log_path.read_text(encoding="utf-8")[-6000:]
        raise RuntimeError(f"{label} freeze-payload preparation failed ({result.returncode}):\n{tail}")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    sys.path.insert(0, str(ROOT / "validation" / "rhythm_holdout"))
    from canonical import canonical_events, sha256_json
    events = canonical_events(freeze.get("renderEvents") or [])
    return sha256_json(events), len(events)


def main() -> int:
    old = json.loads(OLD_PRODUCT.read_text(encoding="utf-8"))
    old_events = old.get("events")
    if not isinstance(old_events, list) or not old_events:
        raise SystemExit("retired candidate contains no events")

    by_key: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for raw in old_events:
        if not isinstance(raw, Mapping):
            raise SystemExit("retired candidate has non-object event")
        by_key[key_of(raw)].append(dict(raw))

    suppress: set[tuple[int, int, int]] = set()
    interval_histogram: dict[int, int] = defaultdict(int)
    promoted_count = 0
    for key, group in sorted(by_key.items()):
        primaries = {int(event.get("dominantMidi")) for event in group}
        if len(primaries) != 1:
            raise SystemExit(f"inconsistent dominantMidi at {key}")
        primary = next(iter(primaries))
        strongest = strongest_hypothesis(group)
        if strongest is None or strongest == primary:
            continue
        promoted_count += 1
        interval = int(strongest) - int(primary)
        rendered_midis = {int(event["midi"]) for event in group}
        if interval in HARMONIC_INTERVALS and int(strongest) in rendered_midis:
            suppress.add((key[0], key[1], int(strongest)))
            interval_histogram[interval] += 1

    simulated = copy.deepcopy(old)
    new_events = [
        event
        for event in simulated.get("events") or []
        if (int(event["measure"]), int(event["step"]), int(event["midi"])) not in suppress
    ]
    simulated["events"] = new_events
    simulated["noteCount"] = len(new_events)
    simulated["schemaVersion"] = 4
    simulated.setdefault("assembly", {})["version"] = 6
    simulated["assembly"]["renderNoteCount"] = len(new_events)
    simulated["assembly"]["selectedAttackCount"] = int(simulated.get("selectedCount") or 0)
    simulated["assembly"]["polyphonicExpansion"] = len(new_events) > int(simulated.get("selectedCount") or 0)
    simulated.setdefault("liveV143", {})["version"] = 7
    simulated.setdefault("candidate", {})["schemaVersion"] = 4
    simulated["promotedHarmonicGuardDiagnostics"] = {
        "schemaVersion": 1,
        "guard": "v143-reference-free-promoted-fundamental-strongest-harmonic-offline-equivalence",
        "inspectedAttackCount": len(by_key),
        "promotedPrimaryCount": promoted_count,
        "harmonicStrongestAbovePromotedPrimaryCount": len(suppress),
        "suppressedStrongestHarmonicCount": len(suppress),
        "attackIdentityChanged": False,
        "primaryMidiChanged": False,
        "addsUnobservedAttack": False,
        "addsUnobservedPitch": False,
        "relocatesAttack": False,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }

    old_attack_keys = {key_of(event) for event in old_events}
    new_attack_keys = {key_of(event) for event in new_events}
    protected = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        cwd=ROOT,
        text=True,
    ).strip()

    with tempfile.TemporaryDirectory(prefix="v143-harmonic-offline-") as temp_dir:
        work = Path(temp_dir)
        simulated_path = work / "simulated-harmonic-guard-product.json"
        simulated_path.write_text(json.dumps(simulated, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        old_sha, old_render_count = projection_sha(OLD_PRODUCT, work, "retired")
        new_sha, new_render_count = projection_sha(simulated_path, work, "simulated")

    checks = {
        "retiredProjectionReproducesScoredIdentity": old_sha == RETIRED_RENDER_SHA,
        "retiredRenderCount985": old_render_count == 985,
        "promotedPrimaryCount144": promoted_count == 144,
        "suppressionCount96": len(suppress) == 96,
        "octaveSuppressionCount78": interval_histogram.get(12, 0) == 78,
        "rawEventCountDropsBy96": len(new_events) == len(old_events) - 96,
        "simulatedRawEventCount889": len(new_events) == 889,
        "attackIdentityUnchanged": new_attack_keys == old_attack_keys,
        "selectedAttackCount725": int(simulated.get("selectedCount") or 0) == 725,
        "simulatedRenderCount889": new_render_count == 889,
        "simulatedRenderIdentityIsNew": new_sha != RETIRED_RENDER_SHA,
        "protectedPipelineExact": protected == EXPECTED_PROTECTED,
    }
    failed = [name for name, passed in checks.items() if not passed]
    report = {
        "schemaVersion": 1,
        "gate": "v143-harmonic-guard-retired-candidate-offline-render-projection",
        "retiredCandidateRawEventCount": len(old_events),
        "retiredProjectedRenderEventCount": old_render_count,
        "retiredProjectedRenderEventSha256": old_sha,
        "expectedRetiredScoredRenderEventSha256": RETIRED_RENDER_SHA,
        "promotedPrimaryCount": promoted_count,
        "suppressedStrongestHarmonicCount": len(suppress),
        "suppressionIntervalHistogram": {str(k): v for k, v in sorted(interval_histogram.items())},
        "simulatedRawEventCount": len(new_events),
        "simulatedSelectedAttackCount": int(simulated.get("selectedCount") or 0),
        "simulatedProjectedRenderEventCount": new_render_count,
        "simulatedProjectedRenderEventSha256": new_sha,
        "simulatedProjectedRenderIdentityIsNew": new_sha != RETIRED_RENDER_SHA,
        "protectedPipelineBlob": protected,
        "checks": checks,
        "failedChecks": failed,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "modalImported": False,
        "modalInvoked": False,
        "modalGpuUsed": False,
        "simulationAcceptedAsCandidate": False,
        "passed": not failed,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
