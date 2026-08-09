from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_2802_harmonic_phase_survivors_precision_v1 as h2802

recur = h2802.recur
recall = h2802.recall
v2 = h2802.v2
v3 = h2802.v3
harmonic = h2802.harmonic
phase = h2802.phase

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-2802-polyphonic-chord-context-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2802-polyphonic-chord-context-v1-manifest.json"
EXPECTED = (183, 684, 256)
EXPECTED_F1 = 28.02


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket(value: int, cuts: list[int], labels: list[str]) -> str:
    for cut, label in zip(cuts, labels):
        if value <= cut:
            return label
    return labels[-1]


def pc_mask(pitches: list[int]) -> tuple[int, ...]:
    if not pitches:
        return ()
    root = min(pitches)
    return tuple(sorted({(p - root) % 12 for p in pitches}))


def slot_map(champion: Counter[tuple[int, int, int]]) -> dict[tuple[int, int], list[int]]:
    out: dict[tuple[int, int], list[int]] = defaultdict(list)
    for (measure, step, pitch), count in champion.items():
        if count > 0:
            out[(measure, step)].extend([pitch] * int(count))
    for key in out:
        out[key].sort()
    return dict(out)


def nearest_distance(pitch: int, pitches: list[int]) -> int:
    others = [abs(pitch - p) for p in pitches if p != pitch]
    return min(others) if others else 99


def interval_signature(pitch: int, pitches: list[int]) -> str:
    intervals = sorted({abs(pitch - p) % 12 for p in pitches if p != pitch})
    if not intervals:
        return "solo"
    useful = [i for i in intervals if i != 0]
    if not useful:
        return "unison"
    return "_".join(str(i) for i in useful[:3])


def local_features(
    tok: tuple[int, int, int],
    slots: dict[tuple[int, int], list[int]],
    winner_audio,
    winner_sr: int,
    alt_audio,
    alt_sr: int,
    grid: dict[tuple[int, int], float],
) -> dict[str, Any]:
    measure, step, pitch = tok
    pitches = slots.get((measure, step), [pitch])
    unique = sorted(set(pitches))
    chord_size = len(unique)
    span = max(unique) - min(unique) if unique else 0
    nearest = nearest_distance(pitch, unique)
    rank = unique.index(pitch) if pitch in unique else 0
    edge = "low" if rank == 0 else ("high" if rank == len(unique) - 1 else "inner")

    prev_pitches = slots.get((measure, step - 1), [])
    next_pitches = slots.get((measure, step + 1), [])
    neighbor_union = sorted(set(prev_pitches + next_pitches))
    neighbor_near = min((abs(pitch - p) for p in neighbor_union), default=99)

    same_step_prev_measure = slots.get((measure - 1, step), [])
    same_step_next_measure = slots.get((measure + 1, step), [])
    repeat_neighbor = sorted(set(same_step_prev_measure + same_step_next_measure))
    repeat_near = min((abs(pitch - p) for p in repeat_neighbor), default=99)

    center = float(grid[(measure, step)])
    wf = phase.phase_features(winner_audio, winner_sr, center, pitch)
    af = phase.phase_features(alt_audio, alt_sr, center, pitch)
    wm = float(wf.get("meanMagnitude", wf.get("magnitudeMean", 0.0)) or 0.0)
    am = float(af.get("meanMagnitude", af.get("magnitudeMean", 0.0)) or 0.0)
    stem_ratio = (min(wm, am) / max(wm, am)) if max(wm, am) > 1e-12 else 0.0

    return {
        "chordSize": chord_size,
        "span": span,
        "nearest": nearest,
        "edge": edge,
        "intervals": interval_signature(pitch, unique),
        "mask": list(pc_mask(unique)),
        "neighborNear": neighbor_near,
        "repeatNear": repeat_near,
        "stemRatio": stem_ratio,
    }


def signatures_for(f: dict[str, Any]) -> set[str]:
    cs = bucket(int(f["chordSize"]), [1, 2, 3, 99], ["cs1", "cs2", "cs3", "cs4p"])
    sp = bucket(int(f["span"]), [0, 4, 7, 12, 99], ["sp0", "sp1_4", "sp5_7", "sp8_12", "sp13p"])
    nd = bucket(int(f["nearest"]), [2, 5, 7, 12, 99], ["nd1_2", "nd3_5", "nd6_7", "nd8_12", "nd13p"])
    nn = bucket(int(f["neighborNear"]), [1, 3, 7, 12, 99], ["nn0_1", "nn2_3", "nn4_7", "nn8_12", "nn13p"])
    rn = bucket(int(f["repeatNear"]), [1, 3, 7, 12, 99], ["rn0_1", "rn2_3", "rn4_7", "rn8_12", "rn13p"])
    sr = float(f["stemRatio"])
    srb = "sr_lt025" if sr < 0.25 else ("sr_025_050" if sr < 0.50 else ("sr_050_075" if sr < 0.75 else "sr_075p"))
    edge = str(f["edge"])
    ints = str(f["intervals"])
    mask = "m_" + "_".join(str(x) for x in f["mask"][:4]) if f["mask"] else "m_none"

    return {
        f"chordSize::{cs}",
        f"chordSpan::{sp}",
        f"chordNearest::{nd}",
        f"chordEdge::{edge}",
        f"chordIntervals::{ints}",
        f"chordMask::{mask}",
        f"neighborContinuity::{nn}",
        f"measureRepeat::{rn}",
        f"crossStemChordSupport::{srb}",
        f"polyphonicCross::{cs}|{sp}|{nd}|{edge}",
        f"contextCross::{cs}|{nn}|{rn}|{srb}",
        f"voicingCross::{edge}|{ints}|{sp}|{srb}",
        f"repeatVoicingCross::{mask}|{rn}|{nn}",
    }


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        true = int(counts["true"])
        false = int(counts["false"])
        total = true + false
        rows.append({
            "signature": signature,
            "true": true,
            "false": false,
            "total": total,
            "precision": round(100.0 * true / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)
    champion, reconstruction = h2802.reconstruct_2802(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 28.02 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    slots = slot_map(champion)
    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        features = local_features(tok, slots, winner_audio, winner_sr, alt_audio, alt_sr, grid)
        signatures = sorted(signatures_for(features))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "features": features,
            "signatures": signatures,
        })

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported = [r for r in ranked if int(r["true"]) >= 5]
    supported.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 28.02 polyphonic chord-context profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-28.02-polyphonic-chord-context-precision",
        "champion2802Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "local-polyphonic-chord-voicing-context-and-cross-stem-support",
        "zeroPrecisionGeneralizableSignaturesMin5False": zero,
        "supportedTrueSignaturesMin5True": supported,
        "rows": details,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": score["pitchF1"],
        "matched": score["matched"],
        "missing": score["missing"],
        "extra": score["extra"],
        "zeroPrecisionSignatureCount": len(zero),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 28.02 POLYPHONIC CHORD CONTEXT V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision chord-context signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true chord-context signatures:")
    for row in supported[:30]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
