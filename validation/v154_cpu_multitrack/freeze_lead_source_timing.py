#!/usr/bin/env python3
"""Freeze V154 Lead source-local timing from the authenticated notation-only draft.

Reference-only. Never reads generated candidate output and never performs scoring.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "research" / "v154-professional-references"
SOURCE = REF / "lead-professional-reference-machine-readable.json"
DRAFT = REF / "lead-source-local-attack-timing-draft.json"
FINAL = REF / "lead-source-local-attack-timing.json"
RECEIPT = REF / "lead-source-local-attack-timing-receipt.json"
SOURCE_RECEIPT = REF / "lead-source-set-receipt.json"
MAPPING = REF / "source-meter-to-fixed-grid-mapping.json"

EXPECTED = {
    SOURCE: "122e0f6b2fa63fb2ea701e9cefe897dd4337fd08de0792e11579f4933804b716",
    DRAFT: "32107c2b09ec3d2322fa141c550a98569ea1b1a4c8e5ed92c6db062596e2df15",
    MAPPING: "1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648",
}
EXPECTED_RENDERED_SET = "e54a76bca81fdcfc8333d774a66175a00da5090fb32200a980c25f8e78b616cb"
EXPECTED_ORIGINAL_SET = "de2f20c330e52aca6125e29ca2cf5c4b719406fc267a98d43d98f3ab1453ff3c"
EXPECTED_SOURCE_EVENTS = 487
EXPECTED_PITCHED = 476
EXPECTED_DEAD = 11
EXPECTED_CONTINUATIONS = 23
EXPECTED_SCORER_ROWS = 447
EXCLUDED_MEASURES = {28, 39}
GRACE_OR_TUPLET_DUPLICATE_STEPS = {(78, 0), (81, 0), (81, 4), (92, 15)}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_pinned(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    actual = sha256_bytes(data)
    expected = EXPECTED[path]
    if actual != expected:
        raise RuntimeError(f"pinned input mismatch {path}: {actual} != {expected}")
    payload = json.loads(data)
    if not isinstance(payload, dict):
        raise TypeError(path)
    return payload


def measure_len(ts: str) -> int:
    if ts == "4/4":
        return 16
    if ts == "2/4":
        return 8
    raise ValueError(f"unsupported source meter {ts}")


def main() -> int:
    if FINAL.exists() or RECEIPT.exists():
        raise RuntimeError("Lead source timing final/receipt already exists; write-once")

    source = load_pinned(SOURCE)
    draft = load_pinned(DRAFT)
    mapping = load_pinned(MAPPING)
    source_receipt = json.loads(SOURCE_RECEIPT.read_text(encoding="utf-8"))
    if source_receipt.get("currentRenderedSetSha256") != EXPECTED_RENDERED_SET:
        raise ValueError("rendered Lead source-set identity drift")
    if source_receipt.get("previousFrozenSetSha256") != EXPECTED_ORIGINAL_SET:
        raise ValueError("original Lead source-set identity drift")
    if source_receipt.get("currentRenderedPageCount") != 22:
        raise ValueError("Lead page count drift")

    if draft.get("status") != "DRAFT_REFERENCE_ONLY_SOURCE_LOCAL_TIMING_PENDING_VALIDATION":
        raise ValueError("unexpected Lead draft status")
    policy = draft.get("policy") or {}
    for key in ("candidateRead", "scoringPerformed", "generatedCandidateModified", "candidateHumanCorrection", "thresholdSweep", "gpuUsed", "mainOrProductionModified"):
        if policy.get(key) is not False:
            raise ValueError(f"draft safety flag must be false: {key}")

    transform = mapping.get("transform") or {}
    if transform.get("generatedCandidateConsulted") is not False or transform.get("scoringPerformed") is not False:
        raise ValueError("mapping safety flags invalid")
    if transform.get("noPadding") is not True or transform.get("noStretching") is not True:
        raise ValueError("mapping must forbid padding/stretching")

    final = copy.deepcopy(draft)
    final["status"] = "FROZEN_REFERENCE_ONLY_SOURCE_LOCAL_TIMING"
    # Run-3 validator proved frozen source measure 89 has 16 events. The notation
    # shows two groups of eight 16th slots across the page wrap. Parenthesized
    # bend continuations at visualOrder 6 and 11 are continuation-only/null.
    final["stepsByMeasure"]["89"] = [0, 1, 2, 3, 4, 5, None, 7, 8, 9, 10, None, 12, 13, 14, 15]
    final["correctionsFromDraft"] = [{
        "measure": 89,
        "basis": "candidate-blind validator run 33134967960 against frozen source plus authenticated pages 99.jpg/100.jpg",
        "draftEntryCount": 15,
        "frozenSourceEventCount": 16,
        "action": "insert source-local step 10 for visualOrder 10 B15 attack; retain visualOrder 6 and 11 continuation-only as null",
        "candidateConsulted": False,
        "scoringPerformed": False,
    }]

    measures = source.get("measures")
    steps = final.get("stepsByMeasure")
    if not isinstance(measures, list) or len(measures) != 113:
        raise ValueError("source measure count")
    if not isinstance(steps, dict) or set(steps) != {str(i) for i in range(1, 114)}:
        raise ValueError("timing measure keys")

    source_events = pitched = dead = cont = 0
    scorer_rows = 0
    nonnull = 0
    excluded_counts = {28: 0, 39: 0}
    total_source_len = 0

    for mo in measures:
        m = int(mo["measure"])
        ts = str(mo.get("timeSignature"))
        if (m == 104 and ts != "2/4") or (m != 104 and ts != "4/4"):
            raise ValueError(f"unexpected source meter m{m}: {ts}")
        mlen = measure_len(ts)
        events = mo.get("events")
        local = steps[str(m)]
        if not isinstance(events, list) or not isinstance(local, list) or len(events) != len(local):
            raise ValueError(f"m{m} timing/event length mismatch {len(local)} != {len(events) if isinstance(events,list) else 'NA'}")
        source_events += len(events)
        seen: dict[int, list[dict[str, Any]]] = {}
        prior: int | None = None
        for i, (e, st) in enumerate(zip(events, local)):
            if int(e.get("visualOrder", i)) != i:
                raise ValueError(f"m{m} visualOrder drift at {i}")
            is_cont = bool(e.get("continuationOnly"))
            kind = e.get("kind")
            if kind == "note":
                pitched += 1
            elif kind == "deadNote":
                dead += 1
                if e.get("midi") is not None:
                    raise ValueError(f"m{m} dead note has MIDI")
            else:
                raise ValueError(f"m{m} unknown event kind {kind}")
            if is_cont:
                cont += 1
                if st is not None:
                    raise ValueError(f"m{m} continuation-only event {i} must be null")
                continue
            if m == 28:
                if st is not None:
                    raise ValueError("m28 must remain null/excluded because rhythm-stem line is absent")
                excluded_counts[28] += 1
                continue
            if st is None:
                raise ValueError(f"m{m} attack-like event {i} has null timing")
            st = int(st)
            if not 0 <= st < mlen:
                raise ValueError(f"m{m} step {st} outside {ts}")
            if prior is not None and st < prior:
                raise ValueError(f"m{m} non-monotonic timing {st} after {prior}")
            prior = st
            nonnull += 1
            seen.setdefault(st, []).append(e)
            if m in EXCLUDED_MEASURES:
                excluded_counts[m] += 1
                continue
            if kind == "deadNote":
                continue
            scorer_rows += 1

        for st, collocated in seen.items():
            if len(collocated) <= 1:
                continue
            groups = {e.get("chordGroup") for e in collocated}
            same_real_chord = len(groups) == 1 and None not in groups
            if not same_real_chord and (m, st) not in GRACE_OR_TUPLET_DUPLICATE_STEPS:
                raise ValueError(f"m{m} unapproved collocation at step {st}")
        total_source_len += mlen

    if source_events != EXPECTED_SOURCE_EVENTS or pitched != EXPECTED_PITCHED or dead != EXPECTED_DEAD or cont != EXPECTED_CONTINUATIONS:
        raise ValueError({"events": source_events, "pitched": pitched, "dead": dead, "cont": cont})
    if excluded_counts != {28: 10, 39: 1}:
        raise ValueError(f"excluded counts drift: {excluded_counts}")
    if scorer_rows != EXPECTED_SCORER_ROWS:
        raise ValueError(f"expected {EXPECTED_SCORER_ROWS} Lead scorer rows, got {scorer_rows}")
    if total_source_len != 1800:
        raise ValueError(f"source length drift: {total_source_len}")

    final["audit"] = {
        "sourceMeasures": 113,
        "sourceEvents": source_events,
        "pitchedEventsIncludingContinuations": pitched,
        "deadNoteEvents": dead,
        "continuationOnlyEvents": cont,
        "nonnullTimedOrGraceCollocatedEventsIncludingExcludedM39": nonnull,
        "nullEvents": source_events - nonnull,
        "excludedMeasure28Events": excluded_counts[28],
        "excludedMeasure39Events": excluded_counts[39],
        "expectedPitchedScorerRows": scorer_rows,
        "totalSourceLength16ths": total_source_len,
        "referenceFacingScoreCalls": 0,
    }
    final_bytes = (json.dumps(final, indent=2, sort_keys=True) + "\n").encode("utf-8")
    final_sha = sha256_bytes(final_bytes)

    receipt = {
        "schema": "dadrock.tabs.v154.lead-source-local-attack-timing-receipt.v1",
        "validation": "PASS",
        "outputPath": str(FINAL.relative_to(ROOT)),
        "outputSha256": final_sha,
        "inputs": {
            str(SOURCE.relative_to(ROOT)): EXPECTED[SOURCE],
            str(DRAFT.relative_to(ROOT)): EXPECTED[DRAFT],
            str(MAPPING.relative_to(ROOT)): EXPECTED[MAPPING],
            str(SOURCE_RECEIPT.relative_to(ROOT)): {
                "renderedPageSetSha256": EXPECTED_RENDERED_SET,
                "previousOriginalPageSetSha256": EXPECTED_ORIGINAL_SET,
                "pageCount": 22,
            },
        },
        "audit": final["audit"],
        "policy": {
            "referenceOnly": True,
            "candidateGenerationMayReadReference": False,
            "generatedCandidateRead": False,
            "generatedCandidateModified": False,
            "humanCandidateCorrection": False,
            "thresholdSweep": False,
            "scoringPerformed": False,
            "referenceFacingScoreCalls": 0,
            "modalL4CudaGpuUsed": False,
            "mainOrProductionModified": False,
            "screenshotBytesCommitted": False,
        },
    }
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    FINAL.write_bytes(final_bytes)
    RECEIPT.write_bytes(receipt_bytes)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
