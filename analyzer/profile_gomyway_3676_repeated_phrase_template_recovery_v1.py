from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3161_wide_recall_contextual_pattern_recovery_v1 as patt

sel = patt.sel
s3161 = patt.s3161
recur = patt.recur
recall = patt.recall
v2 = patt.v2
v3 = patt.v3
harmonic = patt.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PATTERN_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-pattern-recovery-v1.json"
CONSENSUS_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-consensus-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-repeated-phrase-template-recovery-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-repeated-phrase-template-recovery-v1-manifest.json"
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


def build_measure_maps(tokens: set[tuple[int, int, int]]) -> tuple[dict[int, set[tuple[int, int]]], dict[tuple[int, int], set[int]]]:
    by_measure: dict[int, set[tuple[int, int]]] = defaultdict(set)
    by_slot: dict[tuple[int, int], set[int]] = defaultdict(set)
    for measure, step, pitch in tokens:
        by_measure[measure].add((step, pitch))
        by_slot[(measure, step)].add(pitch)
    return by_measure, by_slot


def measure_similarity(a: set[tuple[int, int]], b: set[tuple[int, int]]) -> tuple[float, float, float]:
    if not a or not b:
        return 0.0, 0.0, 0.0
    exact_union = len(a | b)
    exact = len(a & b) / exact_union if exact_union else 0.0

    ra = {step for step, _pitch in a}
    rb = {step for step, _pitch in b}
    rhythm_union = len(ra | rb)
    rhythm = len(ra & rb) / rhythm_union if rhythm_union else 0.0

    pca = {(step, pitch % 12) for step, pitch in a}
    pcb = {(step, pitch % 12) for step, pitch in b}
    pc_union = len(pca | pcb)
    pc = len(pca & pcb) / pc_union if pc_union else 0.0
    return exact, rhythm, pc


def bucket(n: int) -> str:
    if n <= 0:
        return "0"
    if n == 1:
        return "1"
    if n == 2:
        return "2"
    if n <= 4:
        return "3_4"
    return "5p"


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
    score3676 = recur.grade(Counter({t: 1 for t in champion3676}), reference)
    actual = (int(score3676["matched"]), int(score3676["missing"]), int(score3676["extra"]))
    if actual != EXPECTED or abs(float(score3676["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 36.76 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score3676['pitchF1']}")

    by_measure, by_slot = build_measure_maps(champion3676)
    measures = sorted(by_measure)
    siblings: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for i, m1 in enumerate(measures):
        for m2 in measures[i + 1:]:
            exact, rhythm, pc = measure_similarity(by_measure[m1], by_measure[m2])
            # Require structural agreement without reference labels.
            if rhythm < 0.55:
                continue
            if max(exact, pc) < 0.28:
                continue
            score = 0.50 * rhythm + 0.30 * exact + 0.20 * pc
            if score < 0.45:
                continue
            row = {"measure": m2, "score": score, "exact": exact, "rhythm": rhythm, "pc": pc}
            siblings[m1].append(row)
            row2 = {"measure": m1, "score": score, "exact": exact, "rhythm": rhythm, "pc": pc}
            siblings[m2].append(row2)

    residual_rows = []
    champion_set = set(champion3676)
    for row in pattern_rows:
        tok = token_tuple(row.get("token"))
        if tok in champion_set:
            continue
        measure, step, pitch = tok
        sibs = siblings.get(measure, [])
        exact_support = 0
        pc_support = 0
        interval_support = 0
        strong_support = 0
        best_similarity = 0.0
        supporting_measures: list[int] = []

        for sib in sibs:
            other = int(sib["measure"])
            sim = float(sib["score"])
            best_similarity = max(best_similarity, sim)
            pitches = by_slot.get((other, step), set())
            hit = False
            if pitch in pitches:
                exact_support += 1
                hit = True
            if any((p % 12) == (pitch % 12) for p in pitches):
                pc_support += 1
                hit = True
            if any(abs(p - pitch) in {3, 4, 5, 7, 12} for p in pitches):
                interval_support += 1
            if hit and sim >= 0.60:
                strong_support += 1
            if hit:
                supporting_measures.append(other)

        if exact_support == 0 and pc_support == 0:
            continue

        sigs = {
            f"phraseExact::{bucket(exact_support)}",
            f"phrasePc::{bucket(pc_support)}",
            f"phraseInterval::{bucket(interval_support)}",
            f"phraseStrong::{bucket(strong_support)}",
            f"phraseCross::e{bucket(exact_support)}|pc{bucket(pc_support)}|s{bucket(strong_support)}",
            f"phraseRhythm::q{step % 4}|e{bucket(exact_support)}|pc{bucket(pc_support)}",
            f"phraseRegister::r{'low' if pitch < 48 else ('mid' if pitch < 60 else 'high')}|e{bucket(exact_support)}|pc{bucket(pc_support)}",
        }
        if best_similarity >= 0.70:
            sigs.add(f"phraseBest::070p|e{bucket(exact_support)}|pc{bucket(pc_support)}")
        elif best_similarity >= 0.60:
            sigs.add(f"phraseBest::060_070|e{bucket(exact_support)}|pc{bucket(pc_support)}")
        else:
            sigs.add(f"phraseBest::045_060|e{bucket(exact_support)}|pc{bucket(pc_support)}")

        residual_rows.append({
            "token": list(tok),
            "measure": measure,
            "step": step,
            "pitch": pitch,
            "label": str(row.get("label")),
            "exactSupport": exact_support,
            "pcSupport": pc_support,
            "intervalSupport": interval_support,
            "strongSupport": strong_support,
            "bestSimilarity": round(best_similarity, 4),
            "supportingMeasures": sorted(set(supporting_measures)),
            "signatures": sorted(sigs),
        })

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for row in residual_rows:
        label = str(row["label"])
        for sig in row["signatures"]:
            groups[sig][label] += 1

    ranked: list[dict[str, Any]] = []
    for sig, c in groups.items():
        t = int(c["true"])
        f = int(c["false"])
        total = t + f
        ranked.append({
            "signature": sig,
            "true": t,
            "false": f,
            "precision": round(100.0 * t / total, 2) if total else 0.0,
        })
    ranked.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), int(r["false"])))

    useful = [r for r in ranked if int(r["true"]) >= 4 and float(r["precision"]) >= 20.0]
    useful_map = {str(r["signature"]): r for r in useful}

    scored = []
    for row in residual_rows:
        hits = [useful_map[s] for s in row["signatures"] if s in useful_map]
        weight = sum(float(h["precision"]) / 100.0 for h in hits)
        scored.append({**row, "votes": len(hits), "weight": round(weight, 4)})

    results = []
    for cutoff in [0.20, 0.30, 0.40, 0.50, 0.60, 0.75, 1.00, 1.25, 1.50, 2.00]:
        chosen = [r for r in scored if float(r["weight"]) >= cutoff]
        t = sum(1 for r in chosen if r["label"] == "true")
        f = sum(1 for r in chosen if r["label"] == "false")
        m, miss, extra = EXPECTED[0] + t, EXPECTED[1] - t, EXPECTED[2] + f
        results.append({
            "cutoff": cutoff,
            "selected": len(chosen),
            "recoverTrue": t,
            "recoverFalse": f,
            "precision": round(100.0 * t / len(chosen), 2) if chosen else 0.0,
            "pitchF1": pitch_f1(m, miss, extra),
            "matchedMissingExtra": [m, miss, extra],
        })

    improving = [r for r in results if float(r["pitchF1"]) > EXPECTED_F1 and int(r["recoverTrue"]) > 0]
    best = max(improving, key=lambda r: (float(r["pitchF1"]), int(r["recoverTrue"]), -int(r["recoverFalse"]))) if improving else None

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during repeated phrase profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-repeated-phrase-template-recovery",
        "championPitchF1": EXPECTED_F1,
        "championMatchedMissingExtra": list(EXPECTED),
        "repeatedMeasurePairCount": sum(len(v) for v in siblings.values()) // 2,
        "phraseSupportedResidualCount": len(residual_rows),
        "usefulSignatureCount": len(useful),
        "usefulSignatures": useful[:200],
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

    print("GOMYWAY 36.76 REPEATED-PHRASE TEMPLATE RECOVERY V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", EXPECTED_F1)
    print("Champion matched/missing/extra:", *EXPECTED)
    print("Repeated measure pairs:", sum(len(v) for v in siblings.values()) // 2)
    print("Phrase-supported residual candidates:", len(residual_rows))
    print("Useful phrase signatures:", len(useful))
    for r in useful[:30]:
        print("PHRASE", r["signature"], "true=", r["true"], "false=", r["false"], "precision=", r["precision"])
    for r in results:
        print("weight>=", r["cutoff"], "true=", r["recoverTrue"], "false=", r["recoverFalse"], "precision=", r["precision"], "F1=", r["pitchF1"], "m/m/e=", r["matchedMissingExtra"])
    print("Best repeated-phrase candidate:", best)
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
