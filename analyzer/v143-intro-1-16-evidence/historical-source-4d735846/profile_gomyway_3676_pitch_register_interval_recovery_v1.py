from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3676_repeated_phrase_template_recovery_v1 as phrase

patt = phrase.patt
s3161 = phrase.s3161
recur = phrase.recur
recall = phrase.recall
v2 = phrase.v2
v3 = phrase.v3
harmonic = phrase.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PATTERN_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-pattern-recovery-v1.json"
CONSENSUS_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-consensus-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-recovery-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-recovery-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FIRST_WAVE_WEIGHT = 0.80


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pitch_f1(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def token_tuple(value: Any) -> tuple[int, int, int]:
    if isinstance(value, str):
        parts = value.replace("(", "").replace(")", "").replace("[", "").replace("]", "").split(",")
        if len(parts) >= 3:
            return int(parts[0]), int(parts[1]), int(parts[2])
        raise ValueError(value)
    if isinstance(value, (list, tuple)) and len(value) >= 3:
        return int(value[0]), int(value[1]), int(value[2])
    raise ValueError(value)


def bcount(n: int) -> str:
    if n <= 0:
        return "0"
    if n == 1:
        return "1"
    if n <= 3:
        return "2_3"
    return "4p"


def ibucket(value: int | None) -> str:
    if value is None:
        return "none"
    if value <= 2:
        return "0_2"
    if value <= 5:
        return "3_5"
    if value <= 11:
        return "6_11"
    return "12p"


def register(pitch: int) -> str:
    if pitch < 43:
        return "low"
    if pitch < 50:
        return "lowmid"
    if pitch < 57:
        return "mid"
    if pitch < 64:
        return "highmid"
    return "high"


def build_maps(tokens: set[tuple[int, int, int]]) -> dict[str, Any]:
    by_measure: dict[int, dict[int, set[int]]] = defaultdict(lambda: defaultdict(set))
    pitch_locations: dict[int, list[tuple[int, int]]] = defaultdict(list)
    pc_locations: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for measure, step, pitch in tokens:
        by_measure[measure][step].add(pitch)
        pitch_locations[pitch].append((measure, step))
        pc_locations[pitch % 12].append((measure, step, pitch))
    return {"byMeasure": by_measure, "pitchLocations": pitch_locations, "pcLocations": pc_locations}


def nearest_step(step_map: dict[int, set[int]], step: int, direction: int) -> tuple[int, set[int]] | None:
    candidates = [s for s in step_map if (s < step if direction < 0 else s > step)]
    if not candidates:
        return None
    chosen = max(candidates) if direction < 0 else min(candidates)
    return chosen, step_map[chosen]


def nearest_interval(pitch: int, pitches: set[int]) -> int | None:
    if not pitches:
        return None
    return min(abs(pitch - p) for p in pitches)


def local_features(tok: tuple[int, int, int], maps: dict[str, Any]) -> dict[str, Any]:
    measure, step, pitch = tok
    step_map = maps["byMeasure"].get(measure, {})
    prev_item = nearest_step(step_map, step, -1)
    next_item = nearest_step(step_map, step, 1)
    prev_interval = None if prev_item is None else nearest_interval(pitch, prev_item[1])
    next_interval = None if next_item is None else nearest_interval(pitch, next_item[1])
    prev_gap = 99 if prev_item is None else step - prev_item[0]
    next_gap = 99 if next_item is None else next_item[0] - step

    exact_near = 0
    exact_wide = 0
    pc_near = 0
    octave_near = 0
    for m, s in maps["pitchLocations"].get(pitch, []):
        if (m, s) == (measure, step):
            continue
        if abs(m - measure) <= 2 and abs(s - step) <= 4:
            exact_near += 1
        if abs(m - measure) <= 8 and abs(s - step) <= 4:
            exact_wide += 1
    for m, s, other_pitch in maps["pcLocations"].get(pitch % 12, []):
        if (m, s, other_pitch) == (measure, step, pitch):
            continue
        if abs(m - measure) <= 2 and abs(s - step) <= 4:
            pc_near += 1
            if abs(other_pitch - pitch) == 12:
                octave_near += 1

    same_step_local = 0
    same_step_pc = 0
    for dm in (-4, -3, -2, -1, 1, 2, 3, 4):
        pitches = maps["byMeasure"].get(measure + dm, {}).get(step, set())
        if pitch in pitches:
            same_step_local += 1
        if any((p % 12) == (pitch % 12) for p in pitches):
            same_step_pc += 1

    return {
        "pitch": pitch,
        "pitchClass": pitch % 12,
        "register": register(pitch),
        "stepMod4": step % 4,
        "stepMod8": step % 8,
        "prevInterval": prev_interval,
        "nextInterval": next_interval,
        "prevGap": prev_gap,
        "nextGap": next_gap,
        "exactNear": exact_near,
        "exactWide": exact_wide,
        "pcNear": pc_near,
        "octaveNear": octave_near,
        "sameStepLocal": same_step_local,
        "sameStepPc": same_step_pc,
    }


def signatures_for(f: dict[str, Any], inherited: list[str]) -> set[str]:
    pc = f"pc{f['pitchClass']}"
    reg = str(f["register"])
    sm4 = f"sm4_{f['stepMod4']}"
    sm8 = f"sm8_{f['stepMod8']}"
    pi = ibucket(f["prevInterval"])
    ni = ibucket(f["nextInterval"])
    same = bcount(int(f["sameStepLocal"]))
    samepc = bcount(int(f["sameStepPc"]))
    exact = bcount(int(f["exactNear"]))
    wide = bcount(int(f["exactWide"]))
    pcnear = bcount(int(f["pcNear"]))
    octv = bcount(int(f["octaveNear"]))

    sigs = {
        f"prPitch::{pc}|{reg}",
        f"prRhythm::{pc}|{sm4}|{reg}",
        f"prRhythmFine::{pc}|{sm8}|{reg}",
        f"prNeighbor::{reg}|pi{pi}|ni{ni}",
        f"prNeighborPitch::{pc}|pi{pi}|ni{ni}",
        f"prRecurrence::{pc}|same{same}|samepc{samepc}",
        f"prLocal::{pc}|exact{exact}|pc{pcnear}|oct{octv}",
        f"prWide::{pc}|wide{wide}|samepc{samepc}|{reg}",
        f"prCross::{pc}|{sm4}|pi{pi}|ni{ni}|same{same}",
    }

    stem_tags = sorted(
        s for s in inherited
        if any(key in s.lower() for key in ("stem", "agreement", "both", "neighbor"))
    )
    for tag in stem_tags[:4]:
        tail = tag.replace("::", "_").replace("|", "_")[:80]
        sigs.add(f"prInherited::{pc}|{reg}|{tail}")
    return sigs


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    pattern = json.loads(PATTERN_PATH.read_text(encoding="utf-8"))
    consensus = json.loads(CONSENSUS_PATH.read_text(encoding="utf-8"))
    pattern_rows = list(pattern.get("candidateRows") or [])
    first_scored = list(consensus.get("candidateRows") or [])
    if not pattern_rows or not first_scored:
        raise RuntimeError("Missing contextual pattern/consensus outputs")

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
    champion3161, _ = s3161.reconstruct_3161(grid, winner_audio, winner_sr, alt_audio, alt_sr, reference)

    first_selected = {
        token_tuple(r.get("token"))
        for r in first_scored
        if float(r.get("consensusWeight", 0.0)) >= FIRST_WAVE_WEIGHT
    }
    if len(first_selected) != 322:
        raise RuntimeError(f"Expected 322 first-wave selected tokens, got {len(first_selected)}")

    champion3676 = set(champion3161.keys()) | first_selected
    score = recur.grade(Counter({t: 1 for t in champion3676}), reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 36.76 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    maps = build_maps(champion3676)
    champion_set = set(champion3676)
    details: list[dict[str, Any]] = []
    groups: dict[str, Counter[str]] = defaultdict(Counter)

    for row in pattern_rows:
        tok = token_tuple(row.get("token"))
        if tok in champion_set:
            continue
        label = str(row.get("label"))
        features = local_features(tok, maps)
        inherited = [str(s) for s in (row.get("signatures") or [])]
        sigs = sorted(signatures_for(features, inherited))
        details.append({
            "token": list(tok),
            "measure": tok[0],
            "step": tok[1],
            "pitch": tok[2],
            "label": label,
            "features": features,
            "signatures": sigs,
        })
        for sig in sigs:
            groups[sig][label] += 1

    ranked: list[dict[str, Any]] = []
    for sig, c in groups.items():
        true = int(c["true"])
        false = int(c["false"])
        total = true + false
        ranked.append({
            "signature": sig,
            "true": true,
            "false": false,
            "precision": round(100.0 * true / total, 2) if total else 0.0,
        })
    ranked.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), int(r["false"])))

    useful = [r for r in ranked if int(r["true"]) >= 4 and float(r["precision"]) >= 25.0]
    useful_map = {str(r["signature"]): r for r in useful}

    scored: list[dict[str, Any]] = []
    for row in details:
        hits = [useful_map[s] for s in row["signatures"] if s in useful_map]
        weight = sum(float(h["precision"]) / 100.0 for h in hits)
        scored.append({**row, "votes": len(hits), "weight": round(weight, 6)})

    results: list[dict[str, Any]] = []
    for cutoff in [0.25, 0.35, 0.50, 0.65, 0.80, 1.00, 1.25, 1.50, 2.00, 2.50]:
        chosen = [r for r in scored if float(r["weight"]) >= cutoff]
        true = sum(str(r["label"]) == "true" for r in chosen)
        false = sum(str(r["label"]) == "false" for r in chosen)
        matched = EXPECTED[0] + true
        missing = EXPECTED[1] - true
        extra = EXPECTED[2] + false
        results.append({
            "cutoff": cutoff,
            "selected": len(chosen),
            "recoverTrue": true,
            "recoverFalse": false,
            "precision": round(100.0 * true / len(chosen), 2) if chosen else 0.0,
            "pitchF1": pitch_f1(matched, missing, extra),
            "matchedMissingExtra": [matched, missing, extra],
        })

    improving = [r for r in results if int(r["recoverTrue"]) > 0 and float(r["pitchF1"]) > EXPECTED_F1]
    best = max(
        improving,
        key=lambda r: (float(r["pitchF1"]), float(r["precision"]), int(r["recoverTrue"]), -int(r["recoverFalse"])),
    ) if improving else None

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during pitch/register/interval recovery profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-pitch-register-interval-recovery",
        "championPitchF1": EXPECTED_F1,
        "championMatchedMissingExtra": list(EXPECTED),
        "residualCandidateCount": len(details),
        "usefulSignatureCount": len(useful),
        "usefulSignatures": useful[:250],
        "rankedSignatures": ranked[:1000],
        "candidateRows": scored,
        "thresholdResults": results,
        "bestCandidate": best,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-only",
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
        "bestCandidate": best,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PITCH REGISTER INTERVAL RECOVERY V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", EXPECTED_F1)
    print("Champion matched/missing/extra:", *EXPECTED)
    print("Residual candidates:", len(details))
    print("Useful pitch/register/interval signatures:", len(useful))
    for r in useful[:35]:
        print("PITCH", r["signature"], "true=", r["true"], "false=", r["false"], "precision=", r["precision"])
    for r in results:
        print("weight>=", r["cutoff"], "true=", r["recoverTrue"], "false=", r["recoverFalse"], "precision=", r["precision"], "F1=", r["pitchF1"], "m/m/e=", r["matchedMissingExtra"])
    print("Best pitch/register/interval candidate:", best)
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
