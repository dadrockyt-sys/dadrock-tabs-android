#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
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
V148_PATH = ROOT / "debug/v148-singleton-only/candidate/candidate.json"
DECISIONS_PATH = ROOT / "debug/v147-phase-c-real-audio/preserved-run-33038518285/decisions.json"
PREREG_PATH = ROOT / "debug/v149-singleton-confidence/phase-a-reference-free-preregistration.json"

EXPECTED = {
    "acceptedCount": 1144,
    "acceptedSha": "4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881",
    "v148Count": 1144,
    "v148Sha": "1be67004dea62b14740241b536339bb7cad2ecf3ee9e98bfb6109f67e4e1b1fa",
    "v148FileSha": "b45034e2a4dd10a3d7784e584fccdbc7e49667a5b93c9a77ea42f5562ae139bb",
    "decisionsFileSha": "3ec6c42730bf571c29258eca131c4e32da257c1ac6073e5319073818e8ac49b9",
    "changedCount": 106,
    "preregBlob": "324e9f5bcd7264b3d50f54c51a86ebbf173b5ef6",
    "supportBlob": "f4278ffaacaca3f66baf7a3112e2af0f3bc387cf",
    "canonicalBlob": "088d44827fb23e20d9aeeb4944a672989af5846c",
}

MIN_ALT_FUNDAMENTAL_DB = 3.0
MIN_SCORE_MARGIN_DB = 3.0
MIN_FUNDAMENTAL_MARGIN_DB = 2.0
OCTAVE_WEIGHT = 0.25


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path.relative_to(ROOT))], cwd=ROOT, text=True).strip()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(n: int, d: int) -> float:
    return 0.0 if d == 0 else 100.0 * n / d


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
        "min": ordered[0],
        "p10": q(0.10),
        "p25": q(0.25),
        "p50": q(0.50),
        "p75": q(0.75),
        "p90": q(0.90),
        "max": ordered[-1],
        "mean": sum(ordered) / len(ordered),
    }


def candidate_evidence(decision: Mapping[str, Any], midi: int) -> Mapping[str, Any]:
    rows = [row for row in decision.get("candidates", []) if int(row.get("midi")) == midi]
    if len(rows) != 1:
        raise RuntimeError(f"eventIndex={decision.get('eventIndex')} missing unique evidence for MIDI {midi}")
    return rows[0]


def register_bucket(midi: int) -> str:
    if midi <= 51:
        return "40-51"
    if midi <= 63:
        return "52-63"
    if midi <= 75:
        return "64-75"
    return "76+"


def fret_bucket(move: int) -> str:
    move = abs(move)
    if move == 0:
        return "0"
    if move <= 3:
        return "1-3"
    if move <= 7:
        return "4-7"
    return "8+"


def gate_bucket(value: float) -> str:
    if value < 0.5:
        return "[0,0.5)"
    if value < 1.0:
        return "[0.5,1)"
    if value < 2.0:
        return "[1,2)"
    if value < 3.0:
        return "[2,3)"
    if value < 6.0:
        return "[3,6)"
    return "[6,+inf)"


def counter_rows(counter: Counter[str], total: int) -> list[dict[str, Any]]:
    return [
        {"key": key, "count": count, "percentOf106": pct(count, total)}
        for key, count in sorted(counter.items())
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Reference-free V149 analysis of the 106 V148 singleton edits.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise RuntimeError(f"output already exists: {output}")

    prereg_blob = git_blob(PREREG_PATH)
    if prereg_blob != EXPECTED["preregBlob"]:
        raise RuntimeError("V149 preregistration blob mismatch")
    if git_blob(ROOT / "modal/v147_phase_c_artifact_support.py") != EXPECTED["supportBlob"]:
        raise RuntimeError("artifact support blob mismatch")
    if git_blob(ROOT / "validation/rhythm_holdout/canonical.py") != EXPECTED["canonicalBlob"]:
        raise RuntimeError("canonical adapter blob mismatch")

    v148_bytes = V148_PATH.read_bytes()
    decisions_bytes = DECISIONS_PATH.read_bytes()
    if sha256_bytes(v148_bytes) != EXPECTED["v148FileSha"]:
        raise RuntimeError("V148 file SHA mismatch")
    if sha256_bytes(decisions_bytes) != EXPECTED["decisionsFileSha"]:
        raise RuntimeError("V147 decisions file SHA mismatch")

    accepted = canonical_events(materialize_accepted_family(load_json(V5_PATH)))
    if len(accepted) != EXPECTED["acceptedCount"] or sha256_json(accepted) != EXPECTED["acceptedSha"]:
        raise RuntimeError("accepted family identity mismatch")

    v148_doc = json.loads(v148_bytes)
    v148 = canonical_events(v148_doc.get("renderEvents") or [])
    if len(v148) != EXPECTED["v148Count"] or sha256_json(v148) != EXPECTED["v148Sha"]:
        raise RuntimeError("V148 candidate identity mismatch")

    decisions_raw = json.loads(decisions_bytes)
    if not isinstance(decisions_raw, list) or len(decisions_raw) != EXPECTED["acceptedCount"]:
        raise RuntimeError("decision cardinality mismatch")
    decisions = {int(row["eventIndex"]): row for row in decisions_raw}

    accepted_by_index = {int(row["eventIndex"]): row for row in accepted}
    v148_by_index = {int(row["eventIndex"]): row for row in v148}
    if set(accepted_by_index) != set(v148_by_index) or set(accepted_by_index) != set(decisions):
        raise RuntimeError("event index sets differ")

    changed_indices = [idx for idx in sorted(accepted_by_index) if accepted_by_index[idx] != v148_by_index[idx]]
    if len(changed_indices) != EXPECTED["changedCount"]:
        raise RuntimeError(f"expected 106 V148 changes, got {len(changed_indices)}")

    rows: list[dict[str, Any]] = []
    direction = Counter()
    register = Counter()
    pitch_class = Counter()
    original_string = Counter()
    reassignment = Counter()
    fret_move = Counter()
    gate_buckets = Counter()
    weak_flags = Counter()
    nearest_values: list[float] = []
    score_excess_values: list[float] = []
    fundamental_excess_values: list[float] = []
    alt_fund_excess_values: list[float] = []
    frame_counts: list[float] = []
    octave_contributions: list[float] = []

    for idx in changed_indices:
        before = accepted_by_index[idx]
        after = v148_by_index[idx]
        decision = decisions[idx]
        if decision.get("changed") is not True:
            raise RuntimeError(f"V148 changed row lacks changed=true decision eventIndex={idx}")
        original_midi = int(before["midi"])
        selected_midi = int(after["midi"])
        delta = selected_midi - original_midi
        if delta not in (-1, 1):
            raise RuntimeError(f"non +/-1 V148 change eventIndex={idx}")
        if int(decision.get("originalMidi")) != original_midi or int(decision.get("selectedMidi")) != selected_midi:
            raise RuntimeError(f"decision MIDI mismatch eventIndex={idx}")

        original_ev = candidate_evidence(decision, original_midi)
        selected_ev = candidate_evidence(decision, selected_midi)
        score_margin = float(selected_ev["scoreDb"]) - float(original_ev["scoreDb"])
        fundamental_margin = float(selected_ev["fundamentalDeltaDb"]) - float(original_ev["fundamentalDeltaDb"])
        alt_fund_excess = float(selected_ev["fundamentalDeltaDb"]) - MIN_ALT_FUNDAMENTAL_DB
        score_excess = score_margin - MIN_SCORE_MARGIN_DB
        fundamental_excess = fundamental_margin - MIN_FUNDAMENTAL_MARGIN_DB
        nearest = min(alt_fund_excess, score_excess, fundamental_excess)
        if nearest < -1e-8:
            raise RuntimeError(f"changed event below frozen V147 gate eventIndex={idx}: {nearest}")
        selected_octave_bonus = OCTAVE_WEIGHT * max(0.0, float(selected_ev["octaveDeltaDb"]))
        original_octave_bonus = OCTAVE_WEIGHT * max(0.0, float(original_ev["octaveDeltaDb"]))
        octave_contribution = selected_octave_bonus - original_octave_bonus

        old_string = int(before["stringIndex"])
        new_string = int(after["stringIndex"])
        old_fret = int(before["fret"])
        new_fret = int(after["fret"])
        abs_fret_move = abs(new_fret - old_fret)

        dkey = "up-one" if delta == 1 else "down-one"
        rkey = register_bucket(original_midi)
        pkey = str(original_midi % 12)
        skey = str(old_string)
        akey = "same-string" if old_string == new_string else "different-string"
        fkey = fret_bucket(abs_fret_move)
        gkey = gate_bucket(nearest)

        direction[dkey] += 1
        register[rkey] += 1
        pitch_class[pkey] += 1
        original_string[skey] += 1
        reassignment[akey] += 1
        fret_move[fkey] += 1
        gate_buckets[gkey] += 1
        for threshold in (0.5, 1.0, 2.0, 3.0, 6.0):
            if nearest < threshold:
                weak_flags[f"nearest<{threshold:g}dB"] += 1

        nearest_values.append(nearest)
        score_excess_values.append(score_excess)
        fundamental_excess_values.append(fundamental_excess)
        alt_fund_excess_values.append(alt_fund_excess)
        frame_counts.append(float(len(decision.get("frameIndices", []))))
        octave_contributions.append(octave_contribution)

        rows.append({
            "eventIndex": idx,
            "measure": int(before["measure"]),
            "step": int(before["step"]),
            "direction": dkey,
            "originalMidi": original_midi,
            "selectedMidi": selected_midi,
            "originalPitchClass": original_midi % 12,
            "originalRegister": rkey,
            "originalStringIndex": old_string,
            "selectedStringIndex": new_string,
            "stringReassignment": akey,
            "originalFret": old_fret,
            "selectedFret": new_fret,
            "absoluteFretMove": abs_fret_move,
            "frameCount": len(decision.get("frameIndices", [])),
            "alternateFundamentalGateExcessDb": alt_fund_excess,
            "scoreMarginGateExcessDb": score_excess,
            "fundamentalMarginGateExcessDb": fundamental_excess,
            "nearestGateExcessDb": nearest,
            "nearestGateBucket": gkey,
            "octaveMarginContributionDb": octave_contribution,
        })

    weakest = sorted(rows, key=lambda row: (row["nearestGateExcessDb"], row["eventIndex"]))[:20]
    strongest = sorted(rows, key=lambda row: (-row["nearestGateExcessDb"], row["eventIndex"]))[:20]

    total = len(rows)
    report = {
        "schema": "dadrock.tabs.v149.singleton-confidence.reference-free-analysis.v1",
        "classification": "reference-free-v148-singleton-risk-profile",
        "gate": "GO",
        "population": {
            "eventCount": total,
            "percentOfAll1144Events": pct(total, 1144),
            "source": "exactly V148 rows that differ from accepted family #10",
        },
        "identities": {
            "acceptedEventSha256": EXPECTED["acceptedSha"],
            "v148EventSha256": EXPECTED["v148Sha"],
            "v148FileSha256": EXPECTED["v148FileSha"],
            "v147DecisionsFileSha256": EXPECTED["decisionsFileSha"],
            "preregistrationGitBlob": prereg_blob,
        },
        "distributions": {
            "direction": counter_rows(direction, total),
            "originalRegister": counter_rows(register, total),
            "originalPitchClass": counter_rows(pitch_class, total),
            "originalString": counter_rows(original_string, total),
            "stringReassignment": counter_rows(reassignment, total),
            "absoluteFretMove": counter_rows(fret_move, total),
            "nearestGateBucket": counter_rows(gate_buckets, total),
            "cumulativeWeakGate": counter_rows(weak_flags, total),
        },
        "quantiles": {
            "nearestGateExcessDb": quantiles(nearest_values),
            "scoreMarginGateExcessDb": quantiles(score_excess_values),
            "fundamentalMarginGateExcessDb": quantiles(fundamental_excess_values),
            "alternateFundamentalGateExcessDb": quantiles(alt_fund_excess_values),
            "frameCount": quantiles(frame_counts),
            "octaveMarginContributionDb": quantiles(octave_contributions),
        },
        "weakestGateEvents": weakest,
        "strongestGateEvents": strongest,
        "allRows": rows,
        "safety": {
            "goldOrReferenceRead": False,
            "professionalImageRead": False,
            "audioReadOrDecoded": False,
            "hpssOrCqtRecomputed": False,
            "scorerInvoked": False,
            "scoreCallCount": 0,
            "candidateConstructed": False,
            "candidateSearchOrVariants": False,
            "modalOrGpuUsed": False,
            "mainOrProductionModified": False,
            "automaticPromotion": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": report["gate"],
        "population": report["population"],
        "nearestGateBuckets": report["distributions"]["nearestGateBucket"],
        "cumulativeWeakGate": report["distributions"]["cumulativeWeakGate"],
        "stringReassignment": report["distributions"]["stringReassignment"],
        "nearestGateQuantiles": report["quantiles"]["nearestGateExcessDb"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
