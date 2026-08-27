#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
for entry in (ROOT, HOLDOUT_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from canonical import canonical_events, sha256_json  # noqa: E402
from modal.v147_phase_c_artifact_support import materialize_accepted_family  # noqa: E402

V5_PATH = ROOT / "debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json"
V149_PATH = ROOT / "debug/v149-singleton-confidence/candidate/candidate.json"
PREREG_PATH = ROOT / "debug/v150-contextual-singleton/phase-a-reference-free-preregistration.json"

EXPECTED = {
    "acceptedCount": 1144,
    "acceptedSha": "4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881",
    "v149Count": 1144,
    "v149Sha": "4dd13556d580a315c728e7333823eec9644195da5a345689cc44a566ef33d998",
    "v149FileSha": "1add3ffacf9048dd597a47820baeb3ef8cb0e67fa83d12b1b8d8303a8d808278",
    "changedCount": 54,
    "preregBlob": "33f382e4880fd5c563c712d0ad3f33b167a58e68",
    "supportBlob": "f4278ffaacaca3f66baf7a3112e2af0f3bc387cf",
    "canonicalBlob": "088d44827fb23e20d9aeeb4944a672989af5846c",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path.relative_to(ROOT))], cwd=ROOT, text=True).strip()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(n: int, d: int) -> float:
    return 0.0 if not d else 100.0 * n / d


def quantiles(values: Sequence[float]) -> dict[str, float | None]:
    ordered = sorted(float(v) for v in values if math.isfinite(float(v)))
    if not ordered:
        return {k: None for k in ("min", "p10", "p25", "p50", "p75", "p90", "max", "mean")}

    def q(frac: float) -> float:
        if len(ordered) == 1:
            return ordered[0]
        pos = frac * (len(ordered) - 1)
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            return ordered[lo]
        w = pos - lo
        return ordered[lo] * (1.0 - w) + ordered[hi] * w

    return {
        "min": ordered[0], "p10": q(0.10), "p25": q(0.25), "p50": q(0.50),
        "p75": q(0.75), "p90": q(0.90), "max": ordered[-1], "mean": sum(ordered) / len(ordered),
    }


def rows_for_counter(counter: Counter[str], total: int) -> list[dict[str, Any]]:
    return [{"key": k, "count": v, "percentOf54": pct(v, total)} for k, v in sorted(counter.items())]


def min_pitch_distance(midi: int, onset_rows: Sequence[Mapping[str, Any]]) -> int:
    if not onset_rows:
        raise RuntimeError("empty neighboring onset")
    return min(abs(midi - int(row["midi"])) for row in onset_rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Reference-free V150 local-context analysis of V149 changes.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise RuntimeError(f"output already exists: {output}")

    if git_blob(PREREG_PATH) != EXPECTED["preregBlob"]:
        raise RuntimeError("V150 preregistration blob mismatch")
    if git_blob(ROOT / "modal/v147_phase_c_artifact_support.py") != EXPECTED["supportBlob"]:
        raise RuntimeError("artifact support blob mismatch")
    if git_blob(ROOT / "validation/rhythm_holdout/canonical.py") != EXPECTED["canonicalBlob"]:
        raise RuntimeError("canonical blob mismatch")

    v149_bytes = V149_PATH.read_bytes()
    if sha256_bytes(v149_bytes) != EXPECTED["v149FileSha"]:
        raise RuntimeError("V149 candidate file SHA mismatch")

    accepted = canonical_events(materialize_accepted_family(load_json(V5_PATH)))
    if len(accepted) != EXPECTED["acceptedCount"] or sha256_json(accepted) != EXPECTED["acceptedSha"]:
        raise RuntimeError("accepted family identity mismatch")
    v149_doc = json.loads(v149_bytes)
    v149 = canonical_events(v149_doc.get("renderEvents") or [])
    if len(v149) != EXPECTED["v149Count"] or sha256_json(v149) != EXPECTED["v149Sha"]:
        raise RuntimeError("V149 identity mismatch")

    accepted_by_index = {int(row["eventIndex"]): row for row in accepted}
    v149_by_index = {int(row["eventIndex"]): row for row in v149}
    changed = [idx for idx in sorted(accepted_by_index) if accepted_by_index[idx] != v149_by_index[idx]]
    if len(changed) != EXPECTED["changedCount"]:
        raise RuntimeError(f"expected 54 changed V149 rows, got {len(changed)}")

    onset_rows: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in accepted:
        onset_rows[(int(row["measure"]), int(row["step"]))].append(row)
    onset_keys = sorted(onset_rows)
    onset_pos = {key: i for i, key in enumerate(onset_keys)}

    relationship = Counter()
    total_delta_class = Counter()
    pc_support = Counter()
    exact_support = Counter()
    deltas: list[float] = []
    details: list[dict[str, Any]] = []

    for idx in changed:
        before = accepted_by_index[idx]
        after = v149_by_index[idx]
        key = (int(before["measure"]), int(before["step"]))
        if len(onset_rows[key]) != 1:
            raise RuntimeError(f"changed V149 onset is not singleton: {key}")
        pos = onset_pos[key]
        if pos == 0 or pos == len(onset_keys) - 1:
            raise RuntimeError(f"changed V149 onset lacks two-sided context: {key}")
        prev_key = onset_keys[pos - 1]
        next_key = onset_keys[pos + 1]
        prev_rows = onset_rows[prev_key]
        next_rows = onset_rows[next_key]
        original_midi = int(before["midi"])
        selected_midi = int(after["midi"])

        original_prev = min_pitch_distance(original_midi, prev_rows)
        selected_prev = min_pitch_distance(selected_midi, prev_rows)
        original_next = min_pitch_distance(original_midi, next_rows)
        selected_next = min_pitch_distance(selected_midi, next_rows)
        prev_delta = selected_prev - original_prev
        next_delta = selected_next - original_next
        total_delta = prev_delta + next_delta

        if prev_delta > 0 and next_delta > 0:
            rel = "strict-both-sides-worse"
        elif prev_delta < 0 and next_delta < 0:
            rel = "strict-both-sides-better"
        elif prev_delta == 0 and next_delta == 0:
            rel = "both-sides-tied"
        else:
            rel = "mixed"
        relationship[rel] += 1

        if total_delta > 0:
            tclass = "selected-total-cost-higher"
        elif total_delta < 0:
            tclass = "selected-total-cost-lower"
        else:
            tclass = "selected-total-cost-tied"
        total_delta_class[tclass] += 1
        deltas.append(float(total_delta))

        window_keys = onset_keys[max(0, pos - 2):pos] + onset_keys[pos + 1:min(len(onset_keys), pos + 3)]
        window_notes = [row for wk in window_keys for row in onset_rows[wk]]
        orig_pc_count = sum(1 for row in window_notes if int(row["midi"]) % 12 == original_midi % 12)
        sel_pc_count = sum(1 for row in window_notes if int(row["midi"]) % 12 == selected_midi % 12)
        if sel_pc_count > orig_pc_count:
            pc_class = "selected-pitch-class-more-supported"
        elif sel_pc_count < orig_pc_count:
            pc_class = "original-pitch-class-more-supported"
        else:
            pc_class = "pitch-class-support-tied"
        pc_support[pc_class] += 1

        orig_exact = sum(1 for row in window_notes if int(row["midi"]) == original_midi)
        sel_exact = sum(1 for row in window_notes if int(row["midi"]) == selected_midi)
        if sel_exact > orig_exact:
            exact_class = "selected-exact-pitch-more-supported"
        elif sel_exact < orig_exact:
            exact_class = "original-exact-pitch-more-supported"
        else:
            exact_class = "exact-pitch-support-tied"
        exact_support[exact_class] += 1

        details.append({
            "eventIndex": idx,
            "measure": key[0],
            "step": key[1],
            "originalMidi": original_midi,
            "selectedMidi": selected_midi,
            "previousOnset": {"measure": prev_key[0], "step": prev_key[1], "midis": [int(r["midi"]) for r in prev_rows]},
            "nextOnset": {"measure": next_key[0], "step": next_key[1], "midis": [int(r["midi"]) for r in next_rows]},
            "originalPreviousDistance": original_prev,
            "selectedPreviousDistance": selected_prev,
            "originalNextDistance": original_next,
            "selectedNextDistance": selected_next,
            "previousDistanceDelta": prev_delta,
            "nextDistanceDelta": next_delta,
            "totalVoiceLeadingCostDelta": total_delta,
            "contextRelationship": rel,
            "windowOriginalPitchClassCount": orig_pc_count,
            "windowSelectedPitchClassCount": sel_pc_count,
            "pitchClassSupportClass": pc_class,
            "windowOriginalExactMidiCount": orig_exact,
            "windowSelectedExactMidiCount": sel_exact,
            "exactPitchSupportClass": exact_class,
        })

    total = len(details)
    strict_worse = [row for row in details if row["contextRelationship"] == "strict-both-sides-worse"]
    strict_better = [row for row in details if row["contextRelationship"] == "strict-both-sides-better"]
    report = {
        "schema": "dadrock.tabs.v150.contextual-singleton.phase-a-analysis.v1",
        "classification": "reference-free-local-context-profile",
        "gate": "GO",
        "population": {"eventCount": total, "percentOfAll1144Events": pct(total, 1144)},
        "identities": {
            "acceptedCanonicalEventSha256": EXPECTED["acceptedSha"],
            "v149CandidateFileSha256": EXPECTED["v149FileSha"],
            "v149CandidateCanonicalEventSha256": EXPECTED["v149Sha"],
            "preregistrationGitBlob": EXPECTED["preregBlob"],
        },
        "contextRelationship": rows_for_counter(relationship, total),
        "totalCostDeltaClass": rows_for_counter(total_delta_class, total),
        "pitchClassWindowSupport": rows_for_counter(pc_support, total),
        "exactPitchWindowSupport": rows_for_counter(exact_support, total),
        "totalVoiceLeadingCostDeltaQuantiles": quantiles(deltas),
        "strictBothSidesWorseEvents": strict_worse,
        "strictBothSidesBetterEvents": strict_better,
        "allRows": details,
        "safety": {
            "goldOrReferenceRead": False,
            "priorScoreResultRead": False,
            "scorerInvoked": False,
            "scoreCallCount": 0,
            "candidateConstructed": False,
            "candidateSearchOrVariants": False,
            "evidenceMarginThresholdSweep": False,
            "audioReadOrDecoded": False,
            "hpssOrCqtRecomputed": False,
            "modalOrGpuUsed": False,
            "mainOrProductionModified": False,
            "automaticPromotion": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": "GO",
        "population": report["population"],
        "contextRelationship": report["contextRelationship"],
        "totalCostDeltaClass": report["totalCostDeltaClass"],
        "pitchClassWindowSupport": report["pitchClassWindowSupport"],
        "totalVoiceLeadingCostDeltaQuantiles": report["totalVoiceLeadingCostDeltaQuantiles"],
        "scoreCallCount": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
