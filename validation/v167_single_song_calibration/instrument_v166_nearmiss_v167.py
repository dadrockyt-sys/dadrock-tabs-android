#!/usr/bin/env python3
"""V167 reference-blind instrumentation of the exact pinned V166 CPU front-end.

This is an observer, not a generator. It:
1. loads the exact V166 transcriber wrapper by Git-blob identity,
2. calls the frozen V166 front-end functions on reproduced sealed stems,
3. proves the resulting musical streams equal the frozen V166 candidate streams,
4. independently records candidate objects discarded by the existing Guitar/Bass
   segmentation, admission, recovery, proposal, grid-dedupe, and cap gates.

The professional reference/scorer are not inputs and must not be opened here.
No gate, threshold, ranking rule, MIDI, timing, or output event is modified.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

EXPECTED_V166_TRANSCRIBER_BLOB = "f04ca86525b2ce71680a90b84ed476943e9e6426"
EXPECTED_V166_CANDIDATE_BLOB = "c36a4d1e14ca66235b51a866ad3908322834efff"
EXPECTED_V166_COUNTS = {"combinedGuitar": 1050, "bass": 402}
EXPECTED_SOURCE_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
STEPS_PER_MEASURE = 16
EPS = 1e-12


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def native(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return [native(x) for x in value.tolist()]
    if isinstance(value, dict):
        return {str(k): native(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [native(v) for v in value]
    return value


def load_v166_module(path: Path):
    if git_blob_sha(path) != EXPECTED_V166_TRANSCRIBER_BLOB:
        raise RuntimeError("V166 transcriber blob identity mismatch")
    parent = str(path.parent)
    inserted = parent not in sys.path
    if inserted:
        sys.path.insert(0, parent)
    try:
        spec = importlib.util.spec_from_file_location("_v167_pinned_v166_transcriber", path)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load V166 transcriber")
        wrapper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wrapper)
        module = wrapper.build_adapted_module()
    finally:
        if inserted:
            sys.path.remove(parent)
    return module


def local_admission_support(module, env: np.ndarray, frame: int) -> tuple[float, dict[str, Any]]:
    for name in ("_v166_local_support_at_frame", "_v165_local_support_at_frame", "_v164_local_support_at_frame"):
        fn = getattr(module, name, None)
        if callable(fn):
            support, provenance = fn(env, frame)
            return float(support), native(provenance)
    support = module.support_unit(float(env[min(int(frame), len(env) - 1)]), env)
    return float(support), {"fallbackGlobalSupport": True}


def segment_guitar_with_observer(module, raw: list[dict[str, Any]], env: np.ndarray):
    ordered = sorted((copy.deepcopy(row) for row in raw), key=lambda r: (int(r["midi"]), float(r["startSeconds"]), float(r["endSeconds"])))
    result: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for row in ordered:
        row.setdefault("segmentedRawCount", 1)
        if current is None:
            current = row
            continue
        if int(row["midi"]) != int(current["midi"]):
            result.append(current)
            current = row
            continue
        gap = float(row["startSeconds"]) - float(current["endSeconds"])
        should_merge = gap <= EPS
        attack_meta = None
        reason = "OVERLAP_OR_TOUCHING" if should_merge else "SEPARATE_LONG_GAP"
        if 0.0 < gap <= float(module.GUITAR_MAX_UNSUPPORTED_GAP_SECONDS) + EPS:
            center = module.seconds_to_nearest_frame(float(row["startSeconds"]), len(env))
            attack, attack_meta = module.supported_attack(
                env,
                center,
                radius=module.GUITAR_REATTACK_RADIUS_FRAMES,
                positive_q=module.GUITAR_REATTACK_POSITIVE_QUANTILE,
                minimum_support=module.GUITAR_REATTACK_MIN_SUPPORT,
            )
            should_merge = not attack
            reason = "UNSUPPORTED_REATTACK" if should_merge else "SUPPORTED_REATTACK_SPLIT"
        decisions.append({
            "stage": "guitar_segmentation",
            "decision": "MERGED_CHILD" if should_merge else "SEPARATE_EVENT",
            "reason": reason,
            "midi": int(row["midi"]),
            "gapSeconds": gap,
            "parentBefore": copy.deepcopy(current),
            "child": copy.deepcopy(row),
            "reattackEvidence": copy.deepcopy(attack_meta),
        })
        if should_merge:
            current["startSeconds"] = min(float(current["startSeconds"]), float(row["startSeconds"]))
            current["endSeconds"] = max(float(current["endSeconds"]), float(row["endSeconds"]))
            current["durationSeconds"] = max(0.0, float(current["endSeconds"]) - float(current["startSeconds"]))
            current["confidence"] = max(float(current.get("confidence", 0.0)), float(row.get("confidence", 0.0)))
            current["segmentedRawCount"] = int(current.get("segmentedRawCount", 1)) + int(row.get("segmentedRawCount", 1))
            current.setdefault("suppressedReattackChecks", []).append(attack_meta)
        else:
            if attack_meta is not None:
                row["reattackEvidence"] = attack_meta
            result.append(current)
            current = row
    if current is not None:
        result.append(current)
    for row in result:
        row.setdefault("durationSeconds", max(0.0, float(row["endSeconds"]) - float(row["startSeconds"])))
        row.setdefault("segmentedRawCount", 1)
    result = sorted(result, key=lambda r: (float(r["startSeconds"]), int(r["midi"]), float(r["endSeconds"])))
    frozen = module.segment_guitar_rows(raw, env)
    if native(result) != native(frozen):
        raise AssertionError("instrumented Guitar segmentation diverged from frozen V166 behavior")
    return result, decisions


def observe_guitar(module, path: Path):
    import librosa
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import predict

    y = module.load_mono(path)
    env = module.onset_env(y)
    rms = module.rms_env(y)
    cqt, freqs = module.harmonic_cqt(y, module.GUITAR_RANGE[0], module.GUITAR_RANGE[1])
    _, _, notes = predict(
        path,
        model_or_model_path=Path(ICASSP_2022_MODEL_PATH),
        onset_threshold=0.50,
        frame_threshold=0.30,
        minimum_note_length=90.0,
        minimum_frequency=librosa.midi_to_hz(module.GUITAR_RANGE[0]),
        maximum_frequency=librosa.midi_to_hz(module.GUITAR_RANGE[1]),
        multiple_pitch_bends=False,
        melodia_trick=True,
    )
    raw: list[dict[str, Any]] = []
    malformed = 0
    out_of_range_or_nonfinite = 0
    for note in notes:
        if len(note) < 4:
            malformed += 1
            continue
        start, end = float(note[0]), float(note[1])
        midi = int(round(float(note[2])))
        confidence = float(note[3])
        if module.GUITAR_RANGE[0] <= midi <= module.GUITAR_RANGE[1] and math.isfinite(start) and math.isfinite(end) and math.isfinite(confidence):
            raw.append({"midi": midi, "startSeconds": start, "endSeconds": end, "durationSeconds": max(0.0, end - start), "confidence": confidence})
        else:
            out_of_range_or_nonfinite += 1

    segmented, segmentation_decisions = segment_guitar_with_observer(module, raw, env)
    admission_rows: list[dict[str, Any]] = []
    admitted_count = 0
    rejected_activity = 0
    rejected_score = 0
    for index, row in enumerate(segmented):
        original_start = float(row["startSeconds"])
        duration = max(0.0, float(row["endSeconds"]) - original_start)
        original_frame = int(np.clip(round(original_start * module.SR / module.HOP), 0, cqt.shape[1] - 1))
        refined_frame, refine_meta = module.refine_onset_frame(env, original_frame, 6)
        scores, fundamentals = module.three_frame_template(cqt, freqs, refined_frame, module.GUITAR_RANGE[0], module.GUITAR_RANGE[1])
        raw_midi = int(row["midi"])
        candidate_midis = [raw_midi] + [m for m in (raw_midi - 12, raw_midi + 12) if module.GUITAR_RANGE[0] <= m <= module.GUITAR_RANGE[1]]
        rank_map = {m: module.template_rank(scores, m - module.GUITAR_RANGE[0]) for m in candidate_midis}
        med_fund = float(np.median(fundamentals))
        fund_map = {m: bool(fundamentals[m - module.GUITAR_RANGE[0]] > med_fund) for m in candidate_midis}
        chosen, register_meta = module.choose_sequence_register(segmented, index, rank_map, fund_map, module.GUITAR_RANGE[0], module.GUITAR_RANGE[1])
        chosen_offset = chosen - module.GUITAR_RANGE[0]
        rank = module.template_rank(scores, chosen_offset)
        onset_support, onset_prov = local_admission_support(module, env, refined_frame)
        activity_support = module.support_unit(float(rms[int(np.clip(refined_frame, 0, len(rms) - 1))]), rms)
        persistence = float(np.clip(duration / 0.250, 0.0, 1.0))
        confidence = float(np.clip(float(row.get("confidence", 0.0)), 0.0, 1.0))
        admission = module.guitar_admission_score(confidence, rank, onset_support, persistence, activity_support)
        if activity_support + EPS < 0.05:
            decision, reason = "REJECTED", "ACTIVITY_BELOW_0_05"
            rejected_activity += 1
        elif admission + EPS < 0.50:
            decision, reason = "REJECTED", "ADMISSION_BELOW_0_50"
            rejected_score += 1
        else:
            decision, reason = "ADMITTED", "PASS"
            admitted_count += 1
        admission_rows.append({
            "stage": "guitar_segmented_admission",
            "decision": decision,
            "reason": reason,
            "segmentedIndex": index,
            "midi": int(chosen),
            "basicPitchOriginalMidi": raw_midi,
            "startSeconds": original_start,
            "durationSeconds": duration,
            "confidence": confidence,
            "templateScore": float(scores[chosen_offset]),
            "templateRank": float(rank),
            "fundamentalPresent": bool(fundamentals[chosen_offset] > med_fund),
            "onsetSupport": float(onset_support),
            "onsetNormalization": onset_prov,
            "activitySupport": float(activity_support),
            "persistenceSupport": persistence,
            "admissionScore": float(admission),
            "registerContext": native(register_meta),
            "segmentedRawCount": int(row.get("segmentedRawCount", 1)),
            "originalOnsetFrame": original_frame,
            "refinedOnsetFrame": int(refined_frame),
            "onsetRefinement": native(refine_meta),
        })

    independent = np.asarray(librosa.onset.onset_detect(onset_envelope=env, sr=module.SR, hop_length=module.HOP, backtrack=False, units="frames"), dtype=int)
    independent = np.asarray(module.collapse_onsets(independent, 0.040), dtype=int)
    pitch_evidence: dict[tuple[int, int], dict[str, Any]] = {}
    peak_frames: set[int] = set()
    for frame in independent:
        peak_frame, _ = module.local_peak(env, int(frame), 3)
        peak_frames.add(int(peak_frame))
    for frame in sorted(peak_frames):
        scores, fundamentals = module.three_frame_template(cqt, freqs, frame, module.GUITAR_RANGE[0], module.GUITAR_RANGE[1])
        med_fund = float(np.median(fundamentals))
        seconds = float(librosa.frames_to_time(frame, sr=module.SR, hop_length=module.HOP))
        active_midis = sorted({int(row["midi"]) for row in raw if float(row["startSeconds"]) - EPS <= seconds <= float(row["endSeconds"]) + EPS})
        for midi in active_midis:
            offset = midi - module.GUITAR_RANGE[0]
            pitch_evidence[(frame, midi)] = {
                "templateRank": module.template_rank(scores, offset),
                "fundamentalPresent": bool(fundamentals[offset] > med_fund),
            }

    recovery_decisions: list[dict[str, Any]] = []
    accepted_pre_cap: dict[int, list[dict[str, Any]]] = {}
    existing = segmented
    for onset_frame in sorted(set(int(x) for x in independent.tolist())):
        supported, attack_meta = module.supported_attack(
            env,
            onset_frame,
            radius=module.GUITAR_REATTACK_RADIUS_FRAMES,
            positive_q=module.GUITAR_RECOVERY_POSITIVE_QUANTILE,
            minimum_support=module.GUITAR_RECOVERY_MIN_SUPPORT,
        )
        attack_seconds = module.frame_to_seconds(int(attack_meta["peakFrame"]))
        if not supported:
            recovery_decisions.append({"stage":"guitar_recovery_onset","decision":"REJECTED","reason":"ONSET_UNSUPPORTED","onsetFrame":onset_frame,"attackSeconds":attack_seconds,"onsetEvidence":native(attack_meta)})
            continue
        if any(abs(float(row["startSeconds"]) - attack_seconds) <= module.GUITAR_RECOVERY_EXISTING_ATTACK_SECONDS + EPS for row in existing):
            recovery_decisions.append({"stage":"guitar_recovery_onset","decision":"REJECTED","reason":"NEAR_EXISTING_ATTACK","onsetFrame":onset_frame,"attackSeconds":attack_seconds,"onsetEvidence":native(attack_meta)})
            continue
        by_midi: dict[int, dict[str, Any]] = {}
        raw_candidates = [row for row in raw if float(row["startSeconds"]) - EPS <= attack_seconds <= float(row["endSeconds"]) + EPS]
        if not raw_candidates:
            recovery_decisions.append({"stage":"guitar_recovery_onset","decision":"REJECTED","reason":"NO_ACTIVE_BASIC_PITCH_PARENT","onsetFrame":onset_frame,"attackSeconds":attack_seconds,"onsetEvidence":native(attack_meta)})
        for parent_index, row in enumerate(raw_candidates):
            confidence = float(row.get("confidence", 0.0))
            midi = int(row["midi"])
            base = {
                "stage":"guitar_recovery_candidate","onsetFrame":onset_frame,"attackSeconds":attack_seconds,
                "midi":midi,"parentIndexWithinActive":parent_index,"parentConfidence":confidence,
                "onsetSupport":float(attack_meta["normalizedSupport"]),"onsetEvidence":native(attack_meta),
            }
            if confidence + EPS < module.GUITAR_RECOVERY_MIN_PARENT_CONFIDENCE:
                recovery_decisions.append({**base,"decision":"REJECTED","reason":"PARENT_CONFIDENCE_BELOW_MIN"})
                continue
            evidence = pitch_evidence.get((int(attack_meta["peakFrame"]), midi))
            if not isinstance(evidence, Mapping):
                recovery_decisions.append({**base,"decision":"REJECTED","reason":"NO_PITCH_EVIDENCE"})
                continue
            rank = float(evidence.get("templateRank", 0.0))
            fundamental = bool(evidence.get("fundamentalPresent", False))
            score = module.recovery_score(confidence, rank, float(attack_meta["normalizedSupport"]))
            enriched = {**base,"templateRank":rank,"fundamentalPresent":fundamental,"recoveryScore":float(score)}
            if rank + EPS < module.GUITAR_RECOVERY_MIN_TEMPLATE_RANK:
                recovery_decisions.append({**enriched,"decision":"REJECTED","reason":"TEMPLATE_RANK_BELOW_MIN"})
                continue
            if not fundamental:
                recovery_decisions.append({**enriched,"decision":"REJECTED","reason":"FUNDAMENTAL_ABSENT"})
                continue
            if score + EPS < module.GUITAR_RECOVERY_MIN_SCORE:
                recovery_decisions.append({**enriched,"decision":"REJECTED","reason":"RECOVERY_SCORE_BELOW_MIN"})
                continue
            candidate = {
                "midi":midi,"startSeconds":attack_seconds,"parentConfidence":confidence,"templateRank":rank,
                "onsetSupport":float(attack_meta["normalizedSupport"]),"recoveryScore":float(score),"fundamentalPresent":True,
                "source":"basic_pitch_active_state_reattack","recoveryOnsetFrame":int(attack_meta["peakFrame"]),
            }
            old = by_midi.get(midi)
            if old is None or (-score, -confidence, -rank, midi) < (-float(old["recoveryScore"]), -float(old["parentConfidence"]), -float(old["templateRank"]), int(old["midi"])):
                if old is not None:
                    recovery_decisions.append({"stage":"guitar_recovery_candidate","decision":"REJECTED","reason":"DUPLICATE_MIDI_LOWER_EVIDENCE","onsetFrame":onset_frame,"attackSeconds":attack_seconds,**old})
                by_midi[midi] = candidate
            else:
                recovery_decisions.append({**enriched,"decision":"REJECTED","reason":"DUPLICATE_MIDI_LOWER_EVIDENCE"})
        ranked = sorted(by_midi.values(), key=lambda r: (-float(r["recoveryScore"]), -float(r["parentConfidence"]), -float(r["templateRank"]), int(r["midi"])))
        winners = ranked[:module.GUITAR_RECOVERY_CAP]
        losers = ranked[module.GUITAR_RECOVERY_CAP:]
        for row in winners:
            recovery_decisions.append({"stage":"guitar_recovery_candidate","decision":"ADMITTED_PRE_GRID","reason":"PASS_RECOVERY_CAP","onsetFrame":onset_frame,"attackSeconds":attack_seconds,**row})
        for row in losers:
            recovery_decisions.append({"stage":"guitar_recovery_candidate","decision":"REJECTED","reason":"RECOVERY_CAP_LOSER","onsetFrame":onset_frame,"attackSeconds":attack_seconds,**row})
        accepted_pre_cap[onset_frame] = winners

    frozen_recovered = module.active_state_reattack_candidates(raw, segmented, independent.tolist(), env, pitch_evidence)
    observed_recovered = [row for frame in sorted(accepted_pre_cap) for row in accepted_pre_cap[frame]]
    observed_recovered = sorted(observed_recovered, key=lambda r: (float(r["startSeconds"]), int(r["midi"])))
    key = lambda r: (int(r["midi"]), float(r["startSeconds"]), float(r["parentConfidence"]), float(r["templateRank"]), float(r["onsetSupport"]), float(r["recoveryScore"]))
    if [key(r) for r in observed_recovered] != [key(r) for r in frozen_recovered]:
        raise AssertionError("instrumented Guitar recovery decisions diverged from frozen V166 behavior")

    return {
        "rawBasicPitch": raw,
        "rawFilterCounts": {"malformed": malformed, "outOfRangeOrNonfinite": out_of_range_or_nonfinite},
        "segmentationDecisions": segmentation_decisions,
        "segmentedCandidates": segmented,
        "segmentedAdmissionDecisions": admission_rows,
        "recoveryDecisions": recovery_decisions,
        "counts": {
            "raw": len(raw), "segmented": len(segmented), "segmentedAdmitted": admitted_count,
            "rejectedActivity": rejected_activity, "rejectedAdmissionScore": rejected_score,
            "independentOnsets": len(independent), "recovered": len(frozen_recovered),
        },
        "basicPitchVersion": importlib.metadata.version("basic-pitch"),
        "basicPitchModelSha256": sha256_file(Path(ICASSP_2022_MODEL_PATH)),
    }


def observe_bass_states(module, smoothed: np.ndarray, voiced_prob: np.ndarray):
    midi = np.asarray(smoothed, dtype=float)
    vp = np.asarray(voiced_prob, dtype=float)
    labels: list[int | None] = []
    for m, v in zip(midi, vp):
        if math.isfinite(float(m)) and math.isfinite(float(v)) and float(v) + EPS >= module.BASS_STATE_MIN_VOICED:
            labels.append(int(round(float(m))))
        else:
            labels.append(None)
    bridged: list[dict[str, Any]] = []
    i = 0
    while i < len(labels):
        if labels[i] is not None:
            i += 1
            continue
        start = i
        while i < len(labels) and labels[i] is None:
            i += 1
        end = i
        gap = end - start
        left = labels[start - 1] if start > 0 else None
        right = labels[end] if end < len(labels) else None
        if gap <= module.BASS_BRIDGE_GAP_FRAMES and left is not None and left == right:
            bridged.append({"startFrame":start,"endFrameExclusive":end,"frameCount":gap,"midi":int(left)})
            for j in range(start, end):
                labels[j] = left
    decisions: list[dict[str, Any]] = []
    accepted: list[dict[str, Any]] = []
    i = 0
    while i < len(labels):
        if labels[i] is None:
            i += 1
            continue
        start = i
        state = int(labels[i])
        while i < len(labels) and labels[i] == state:
            i += 1
        end = i
        finite_vp = vp[start:end][np.isfinite(vp[start:end])]
        median_vp = float(np.median(finite_vp)) if finite_vp.size else 0.0
        row = {"midi":state,"startFrame":start,"endFrameExclusive":end,"frameCount":end-start,"medianVoicedProbability":median_vp}
        if end - start < module.BASS_STATE_MIN_FRAMES:
            decisions.append({"stage":"bass_state","decision":"REJECTED","reason":"RUN_TOO_SHORT",**row})
            continue
        if median_vp + EPS < module.BASS_STATE_MIN_MEDIAN_VOICED:
            decisions.append({"stage":"bass_state","decision":"REJECTED","reason":"MEDIAN_VOICED_BELOW_MIN",**row})
            continue
        decisions.append({"stage":"bass_state","decision":"ADMITTED","reason":"PASS",**row})
        accepted.append(row)
    frozen = module.stable_bass_states(smoothed, voiced_prob)
    if native(accepted) != native(frozen):
        raise AssertionError("instrumented Bass state construction diverged from frozen V166 behavior")
    return accepted, decisions, bridged


def observe_bass_proposals(module, states: list[dict[str, Any]], onset_frames: Iterable[int], env: np.ndarray):
    proposals: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    prior = None
    for state in states:
        if prior is not None:
            gap = int(state["startFrame"]) - int(prior["endFrameExclusive"])
            changed = abs(int(state["midi"]) - int(prior["midi"])) >= module.BASS_STATE_CHANGE_SEMITONES
            new_after_silence = gap >= module.BASS_SILENCE_NEW_STATE_FRAMES
            if changed or new_after_silence:
                frame = int(state["startFrame"])
                support, prov = module.local_support_unit(float(env[min(frame, len(env)-1)]), env, frame)
                proposal = {"frame":frame,"kind":"state_change","midi":int(state["midi"]),"onsetSupport":float(support),"stateVoicedProbability":float(state["medianVoicedProbability"]),"priority":2,"normalizationLoFrame":prov["loFrame"],"normalizationHiFrame":prov["hiFrame"]}
                proposals.append(proposal)
                decisions.append({"stage":"bass_proposal","decision":"CANDIDATE_PRE_MERGE","reason":"STATE_CHANGE_OR_NEW_AFTER_SILENCE",**proposal})
        prior = state

    last_event_by_state: dict[tuple[int,int], int] = {}
    for frame in sorted(set(int(x) for x in onset_frames)):
        state = module.state_for_frame(states, frame)
        if state is None:
            decisions.append({"stage":"bass_proposal","decision":"REJECTED","reason":"NO_NEARBY_STABLE_STATE","frame":frame})
            continue
        peak_frame, peak = module.local_peak(env, frame, 3)
        support, prov = module.local_support_unit(peak, env, frame)
        base = {"stage":"bass_proposal","frame":frame,"peakFrame":int(peak_frame),"stateMidi":int(state["midi"]),"onsetSupport":float(support),"stateVoicedProbability":float(state["medianVoicedProbability"]),"normalizationLoFrame":prov["loFrame"],"normalizationHiFrame":prov["hiFrame"]}
        if support + EPS < module.BASS_ONSET_MIN_SUPPORT:
            decisions.append({**base,"decision":"REJECTED","reason":"ONSET_SUPPORT_BELOW_MIN"})
            continue
        key = (int(state["startFrame"]), int(state["midi"]))
        kind, priority = "detected_onset", 0
        prior_frame = last_event_by_state.get(key)
        if prior_frame is not None:
            ioi = module.frame_to_seconds(peak_frame - prior_frame)
            if ioi + EPS < module.BASS_REATTACK_MIN_IOI_SECONDS:
                decisions.append({**base,"decision":"REJECTED","reason":"REATTACK_IOI_TOO_SHORT","ioiSeconds":float(ioi)})
                continue
            threshold, threshold_prov = module.local_positive_quantile(env, frame, module.BASS_REATTACK_POSITIVE_QUANTILE)
            if threshold is None:
                decisions.append({**base,"decision":"REJECTED","reason":"REATTACK_NO_POSITIVE_THRESHOLD","thresholdProvenance":native(threshold_prov)})
                continue
            if peak + EPS < threshold:
                decisions.append({**base,"decision":"REJECTED","reason":"REATTACK_PEAK_BELOW_THRESHOLD","positiveThreshold":float(threshold)})
                continue
            if support + EPS < module.BASS_REATTACK_MIN_SUPPORT:
                decisions.append({**base,"decision":"REJECTED","reason":"REATTACK_SUPPORT_BELOW_MIN","positiveThreshold":float(threshold)})
                continue
            kind, priority = "same_pitch_reattack", 1
        proposal = {"frame":int(peak_frame),"kind":kind,"midi":int(state["midi"]),"onsetSupport":float(support),"stateVoicedProbability":float(state["medianVoicedProbability"]),"priority":priority,"normalizationLoFrame":prov["loFrame"],"normalizationHiFrame":prov["hiFrame"]}
        proposals.append(proposal)
        decisions.append({"stage":"bass_proposal","decision":"CANDIDATE_PRE_MERGE","reason":"PASS_ONSET_GATE",**proposal})
        last_event_by_state[key] = int(peak_frame)

    merge_frames = module.seconds_to_frames(module.BASS_PROPOSAL_MERGE_SECONDS)
    ordered = sorted(proposals, key=lambda r:(int(r["frame"]),int(r["priority"]),-float(r["onsetSupport"])))
    groups: list[list[dict[str, Any]]] = []
    for row in ordered:
        if not groups or int(row["frame"]) - max(int(x["frame"]) for x in groups[-1]) > merge_frames:
            groups.append([row])
        else:
            groups[-1].append(row)
    winners: list[dict[str, Any]] = []
    merge_decisions: list[dict[str, Any]] = []
    for group_index, group in enumerate(groups):
        winner = min(group, key=lambda r:(int(r["priority"]),-float(r["onsetSupport"]),-float(r["stateVoicedProbability"]),int(r["frame"])))
        item = dict(winner); item["mergedProposalCount"] = len(group); winners.append(item)
        for row in group:
            merge_decisions.append({"stage":"bass_proposal_merge","decision":"WINNER" if row is winner else "REJECTED","reason":"MERGE_WINNER" if row is winner else "MERGE_GROUP_LOSER","groupIndex":group_index,"mergedProposalCount":len(group),**row})
    winners = sorted(winners, key=lambda r:(int(r["frame"]),int(r["midi"])))
    frozen = module.bass_state_proposals(states, onset_frames, env)
    if native(winners) != native(frozen):
        raise AssertionError("instrumented Bass proposals diverged from frozen V166 behavior")
    return winners, decisions, merge_decisions


def observe_bass(module, path: Path):
    import librosa
    y = module.load_mono(path)
    env = module.onset_env(y)
    rms = module.rms_env(y)
    raw_onsets = np.asarray(librosa.onset.onset_detect(onset_envelope=env, sr=module.SR, hop_length=module.HOP, backtrack=True, units="frames"), dtype=int)
    retained_onsets = module.collapse_onsets(raw_onsets, 0.035)
    harmonic, _ = librosa.effects.hpss(y)
    f0, _flag, voiced_prob = librosa.pyin(harmonic, fmin=librosa.midi_to_hz(module.BASS_RANGE[0]), fmax=librosa.midi_to_hz(module.BASS_RANGE[1]), sr=module.SR, frame_length=2048, hop_length=256)
    pyin_midi = librosa.hz_to_midi(np.asarray(f0,dtype=float))
    voiced_prob = np.asarray(voiced_prob,dtype=float)
    smoothed = module.median_smooth_midi(pyin_midi)
    states, state_decisions, bridged = observe_bass_states(module, smoothed, voiced_prob)
    proposals, proposal_decisions, merge_decisions = observe_bass_proposals(module, states, retained_onsets, env)
    cqt, freqs = module.harmonic_cqt(y, module.BASS_RANGE[0], module.BASS_RANGE[1])
    half_frames = max(1, int(round((0.120/2.0)*module.SR/module.HOP)))
    admission_rows: list[dict[str, Any]] = []
    admitted = rejected_activity = rejected_additional = rejected_score = 0
    for index, proposal in enumerate(proposals):
        original_frame = int(proposal["frame"])
        refined_frame, refine_meta = module.refine_onset_frame(env, original_frame, 8)
        lo=max(0,refined_frame-half_frames); hi=min(cqt.shape[1],refined_frame+half_frames+1); frames=list(range(lo,hi)) or [refined_frame]
        hscores, fundamentals = module.template_scores(cqt,freqs,frames,module.BASS_RANGE[0],module.BASS_RANGE[1])
        harmonic_z = module.z_across_candidates(hscores)
        p_lo=max(0,lo); p_hi=min(len(pyin_midi),hi); finite=np.isfinite(pyin_midi[p_lo:p_hi])
        if np.any(finite):
            pm=float(np.median(pyin_midi[p_lo:p_hi][finite])); vp=float(np.nanmedian(voiced_prob[p_lo:p_hi][finite])); vp=0.0 if not math.isfinite(vp) else float(np.clip(vp,0.0,1.0))
            midi_candidates=np.arange(module.BASS_RANGE[0],module.BASS_RANGE[1]+1,dtype=float); proximity=np.exp(-0.5*((midi_candidates-pm)/0.75)**2); combined=harmonic_z+0.75*vp*proximity
        else:
            pm=None; vp=0.0; combined=harmonic_z
        best_value=float(np.max(combined)); best_offset=int(np.where(np.abs(combined-best_value)<=EPS)[0][0]); midi=module.BASS_RANGE[0]+best_offset
        rank=module.template_rank(combined,best_offset); fundamental_present=bool(fundamentals[best_offset]>float(np.median(fundamentals)))
        onset_support,onset_prov=local_admission_support(module,env,refined_frame)
        activity_support=module.support_unit(float(rms[int(np.clip(refined_frame,0,len(rms)-1))]),rms)
        admission=module.bass_admission_score(vp,rank,onset_support,activity_support)
        if activity_support+EPS<0.04:
            decision,reason="REJECTED","ACTIVITY_BELOW_0_04"; rejected_activity+=1
        elif not (fundamental_present or vp+EPS>=0.60):
            decision,reason="REJECTED","FUNDAMENTAL_ABSENT_AND_VOICING_BELOW_0_60"; rejected_additional+=1
        elif admission+EPS<0.42:
            decision,reason="REJECTED","ADMISSION_BELOW_0_42"; rejected_score+=1
        else:
            decision,reason="ADMITTED","PASS"; admitted+=1
        admission_rows.append({"stage":"bass_admission","decision":decision,"reason":reason,"proposalIndex":index,"proposal":native(proposal),"midi":int(midi),"stateMidi":int(proposal["midi"]),"originalOnsetFrame":original_frame,"refinedOnsetFrame":int(refined_frame),"onsetRefinement":native(refine_meta),"harmonicTemplateScore":float(hscores[best_offset]),"fundamentalMeanMagnitude":float(fundamentals[best_offset]),"fundamentalPresent":fundamental_present,"medianPyinMidi":pm,"medianPyinVoicedProbability":float(vp),"combinedPitchScore":best_value,"templateRank":float(rank),"onsetSupport":float(onset_support),"onsetNormalization":onset_prov,"activitySupport":float(activity_support),"admissionScore":float(admission)})
    return {
        "rawDetectedOnsets": [int(x) for x in raw_onsets.tolist()],
        "retainedOnsets": [int(x) for x in retained_onsets],
        "bridgedStateGaps": bridged,
        "stateDecisions": state_decisions,
        "proposalDecisions": proposal_decisions,
        "proposalMergeDecisions": merge_decisions,
        "mergedProposals": proposals,
        "admissionDecisions": admission_rows,
        "counts": {"rawOnsets":len(raw_onsets),"retainedOnsets":len(retained_onsets),"stableStates":len(states),"mergedProposals":len(proposals),"admitted":admitted,"rejectedActivity":rejected_activity,"rejectedAdditionalGate":rejected_additional,"rejectedAdmissionScore":rejected_score},
    }


def observe_grid(module, events: list[dict[str, Any]], lattice: list[float], instrument_env: np.ndarray, shared_env: np.ndarray, stream: str):
    mapped: dict[tuple[int,int], dict[str, Any]] = {}
    decisions: list[dict[str, Any]] = []
    first_half=0.5*float(lattice[1]-lattice[0])
    for event_index,row in enumerate(events):
        event_time=float(row["startSeconds"])
        if event_time < float(lattice[0])-first_half:
            decisions.append({"stage":f"{stream}_grid","decision":"REJECTED","reason":"PRE_GRID","eventIndex":event_index,"event":native(row)})
            continue
        step,selection=module.select_event_step(event_time,lattice,instrument_env,shared_env)
        item=dict(row); item.update({"absoluteGridStep":int(step),"measure":int(step)//16+1,"step":int(step)%16,"stream":stream,"nearestLatticeStep":int(selection["nearestStep"]),"selectedLatticeTimeSeconds":float(lattice[step]),"gridCorrectionSteps":int(step-int(selection["nearestStep"])),"stepSelection":selection})
        key=(int(step),int(item["midi"])); old=mapped.get(key)
        if old is None:
            mapped[key]=item
        else:
            new_evidence=float(item.get("admissionScore",item.get("recoveryScore",0.0))); old_evidence=float(old.get("admissionScore",old.get("recoveryScore",0.0)))
            new_conf=float(item.get("confidence",item.get("medianPyinVoicedProbability",0.0))); old_conf=float(old.get("confidence",old.get("medianPyinVoicedProbability",0.0)))
            if (-new_evidence,-new_conf,int(item["midi"])) < (-old_evidence,-old_conf,int(old["midi"])):
                decisions.append({"stage":f"{stream}_grid_dedupe","decision":"REJECTED","reason":"SAME_STEP_MIDI_LOWER_EVIDENCE","loser":native(old),"winner":native(item)})
                mapped[key]=item
            else:
                decisions.append({"stage":f"{stream}_grid_dedupe","decision":"REJECTED","reason":"SAME_STEP_MIDI_LOWER_EVIDENCE","loser":native(item),"winner":native(old)})
    pre_cap=list(mapped.values()); by_step:dict[int,list[dict[str,Any]]]={}
    for row in pre_cap: by_step.setdefault(int(row["absoluteGridStep"]),[]).append(row)
    cap=int(module.GUITAR_POLYPHONY_CAP if stream=="combinedGuitar" else module.BASS_GRID_CAP)
    kept=[]
    for step in sorted(by_step):
        if stream=="bass": ranked=sorted(by_step[step],key=lambda r:(-float(r.get("admissionScore",0.0)),-float(r.get("medianPyinVoicedProbability",0.0)),int(r["midi"])))
        else: ranked=sorted(by_step[step],key=lambda r:(-float(r.get("admissionScore",r.get("recoveryScore",0.0))),-float(r.get("confidence",r.get("parentConfidence",0.0))),int(r["midi"])))
        kept.extend(ranked[:cap])
        for loser in ranked[cap:]: decisions.append({"stage":f"{stream}_grid_cap","decision":"REJECTED","reason":"GRID_CAP_LOSER","cap":cap,"loser":native(loser),"keptAtStep":[native(x) for x in ranked[:cap]]})
    kept=sorted(kept,key=lambda r:(int(r["absoluteGridStep"]),int(r["midi"])))
    frozen,pregrid,corrected=module.map_events(events,lattice,instrument_env,shared_env,stream)
    if native(kept)!=native(frozen): raise AssertionError(f"instrumented {stream} grid decisions diverged from frozen V166 behavior")
    return {"decisions":decisions,"counts":{"inputEvents":len(events),"preCapUniqueStepMidi":len(pre_cap),"finalEvents":len(kept),"preGridExcluded":int(pregrid),"evidenceStepCorrections":int(corrected),"cap":cap}}


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--mix",type=Path,required=True); ap.add_argument("--guitar",type=Path,required=True); ap.add_argument("--bass",type=Path,required=True); ap.add_argument("--drums",type=Path,required=True)
    ap.add_argument("--timebase",type=Path,required=True); ap.add_argument("--frozen-v166-candidate",type=Path,required=True); ap.add_argument("--v166-transcriber",type=Path,required=True)
    ap.add_argument("--source-audio",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); ap.add_argument("--receipt",type=Path,required=True)
    args=ap.parse_args()
    if args.output.exists() or args.receipt.exists(): raise RuntimeError("instrumentation outputs are write-once")
    for path in (args.mix,args.guitar,args.bass,args.drums,args.timebase,args.frozen_v166_candidate,args.v166_transcriber,args.source_audio):
        if not path.is_file(): raise RuntimeError(f"missing instrumentation input: {path}")
    if sha256_file(args.source_audio)!=EXPECTED_SOURCE_SHA256: raise RuntimeError("sealed source audio identity mismatch")
    if git_blob_sha(args.frozen_v166_candidate)!=EXPECTED_V166_CANDIDATE_BLOB: raise RuntimeError("frozen V166 candidate blob mismatch")

    module=load_v166_module(args.v166_transcriber); frozen=load_json(args.frozen_v166_candidate); timebase=load_json(args.timebase)
    lattice=[float(x) for x in timebase["subdivisionTimesSeconds"]]
    mix_y=module.load_mono(args.mix); drums_y=module.load_mono(args.drums); shared_env=module.shared_onset_env(mix_y,drums_y)
    bass_raw,bass_meta,bass_env=module.bass_events(args.bass); guitar_raw,guitar_meta,guitar_env=module.guitar_events(args.guitar)
    guitar_final,guitar_pre,guitar_corrected=module.map_events(guitar_raw,lattice,guitar_env,shared_env,"combinedGuitar")
    bass_final,bass_pre,bass_corrected=module.map_events(bass_raw,lattice,bass_env,shared_env,"bass")
    reproduced={"combinedGuitar":native(guitar_final),"bass":native(bass_final)}
    frozen_streams=frozen.get("streams") or {}
    if reproduced != {"combinedGuitar":frozen_streams.get("combinedGuitar"),"bass":frozen_streams.get("bass")}:
        raise AssertionError("V167 observer did not reproduce exact frozen V166 musical streams")
    if {k:len(v) for k,v in reproduced.items()}!=EXPECTED_V166_COUNTS: raise AssertionError("reproduced V166 stream counts drifted")

    guitar_observed=observe_guitar(module,args.guitar); bass_observed=observe_bass(module,args.bass)
    if guitar_observed["counts"]["raw"]!=int(guitar_meta["basicPitchRawEventCount"]): raise AssertionError("Guitar raw count observer mismatch")
    if guitar_observed["counts"]["segmented"]!=int(guitar_meta["segmentedCandidateCount"]): raise AssertionError("Guitar segmented count observer mismatch")
    if guitar_observed["counts"]["segmentedAdmitted"]!=int(guitar_meta["segmentedAdmittedCount"]): raise AssertionError("Guitar admission observer mismatch")
    if guitar_observed["counts"]["rejectedActivity"]!=int(guitar_meta["rejectedByActivity"]) or guitar_observed["counts"]["rejectedAdmissionScore"]!=int(guitar_meta["rejectedByAdmissionScore"]): raise AssertionError("Guitar rejection observer mismatch")
    if bass_observed["counts"]["stableStates"]!=int(bass_meta["stablePitchStateCount"]): raise AssertionError("Bass state observer mismatch")
    if bass_observed["counts"]["mergedProposals"]!=int(bass_meta["mergedProposalCount"]): raise AssertionError("Bass proposal observer mismatch")
    if bass_observed["counts"]["admitted"]!=int(bass_meta["admittedEventCountBeforeGridDedupe"]): raise AssertionError("Bass admission observer mismatch")
    if bass_observed["counts"]["rejectedActivity"]!=int(bass_meta["rejectedByActivity"]) or bass_observed["counts"]["rejectedAdditionalGate"]!=int(bass_meta["rejectedByAdditionalGate"]) or bass_observed["counts"]["rejectedAdmissionScore"]!=int(bass_meta["rejectedByAdmissionScore"]): raise AssertionError("Bass rejection observer mismatch")

    guitar_grid=observe_grid(module,guitar_raw,lattice,guitar_env,shared_env,"combinedGuitar"); bass_grid=observe_grid(module,bass_raw,lattice,bass_env,shared_env,"bass")
    if guitar_grid["counts"]["preGridExcluded"]!=int(guitar_pre) or bass_grid["counts"]["preGridExcluded"]!=int(bass_pre): raise AssertionError("grid observer pre-grid mismatch")
    if guitar_grid["counts"]["evidenceStepCorrections"]!=int(guitar_corrected) or bass_grid["counts"]["evidenceStepCorrections"]!=int(bass_corrected): raise AssertionError("grid observer correction mismatch")

    output={
        "schema":"dadrock.tabs.v167.reference-blind-nearmiss-evidence-pool.v1","version":"V167","label":"SINGLE_SONG_TRAINING_CALIBRATION",
        "source":{"v166CandidateGitBlob":EXPECTED_V166_CANDIDATE_BLOB,"v166TranscriberGitBlob":EXPECTED_V166_TRANSCRIBER_BLOB,"sourceAudioSha256":EXPECTED_SOURCE_SHA256,"timebaseSha256":sha256_file(args.timebase),"guitarStemSha256":sha256_file(args.guitar),"bassStemSha256":sha256_file(args.bass),"drumsStemSha256":sha256_file(args.drums),"mixSha256":sha256_file(args.mix)},
        "reproduction":{"exactFrozenV166MusicalStreams":True,"counts":EXPECTED_V166_COUNTS,"guitarMetadata":native(guitar_meta),"bassMetadata":native(bass_meta)},
        "guitar":guitar_observed,"bass":bass_observed,"grid":{"combinedGuitar":guitar_grid,"bass":bass_grid},
        "policy":{"referenceRead":False,"scorerRead":False,"referenceFacingScoreCalls":0,"thresholdTuningPerformed":False,"candidateGenerationBehaviorModified":False,"frozenV166CandidateModified":False,"gpuCudaModalUsed":False,"mainOrProductionModified":False},
    }
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(native(output),indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    receipt={"schema":"dadrock.tabs.v167.reference-blind-nearmiss-evidence-receipt.v1","version":"V167","status":"EVIDENCE_POOL_OBSERVED","evidencePoolSha256":sha256_file(args.output),"evidencePoolGitBlob":git_blob_sha(args.output),"exactFrozenV166MusicalStreams":True,"counts":EXPECTED_V166_COUNTS,"inputIdentities":output["source"],"policy":output["policy"]}
    args.receipt.parent.mkdir(parents=True,exist_ok=True); args.receipt.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"evidencePoolSha256":receipt["evidencePoolSha256"],"exactFrozenV166MusicalStreams":True,"counts":EXPECTED_V166_COUNTS,"guitarObserved":guitar_observed["counts"],"bassObserved":bass_observed["counts"]},sort_keys=True))
    return 0


if __name__=="__main__": raise SystemExit(main())
