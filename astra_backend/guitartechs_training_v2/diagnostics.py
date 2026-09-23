from __future__ import annotations

from collections import defaultdict
import math

import numpy as np

NUM_STRINGS = 6
MASK = -100
DEFAULT_HOP_SECONDS = 0.02
DEFAULT_ONSET_TOLERANCE_SECONDS = 0.05
OPEN_MIDI = (40, 45, 50, 55, 59, 64)


def _validate_states(states, mask):
    states = np.asarray(states)
    mask = np.asarray(mask, dtype=bool)
    if states.ndim != 2 or states.shape[1] != NUM_STRINGS:
        raise ValueError("states must be T x 6")
    if mask.shape != states.shape:
        raise ValueError("mask must match states")
    return states, mask


def events_from_states(states, mask, hop_seconds=DEFAULT_HOP_SECONDS):
    states, mask = _validate_states(states, mask)
    events = []
    for string in range(NUM_STRINGS):
        x = states[:, string]
        valid = (~mask[:, string]) & (x >= 0)
        frame = 0
        while frame < len(x):
            if not valid[frame]:
                frame += 1
                continue
            fret = int(x[frame])
            end = frame + 1
            while end < len(x) and valid[end] and int(x[end]) == fret:
                end += 1
            events.append({
                "string": string,
                "fret": fret,
                "startFrame": frame,
                "endFrame": end,
                "start": frame * hop_seconds,
                "end": end * hop_seconds,
            })
            frame = end
    events.sort(key=lambda e: (e["start"], e["string"], e["fret"], e["end"]))
    return events


def _ordered_match(pred_indices, ref_indices, pred_events, ref_events, onset_tolerance):
    p = sorted(pred_indices, key=lambda i: (pred_events[i]["start"], pred_events[i]["end"], i))
    r = sorted(ref_indices, key=lambda i: (ref_events[i]["start"], ref_events[i]["end"], i))
    n, m = len(p), len(r)
    dp = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = (0, 0.0, ())
    for j in range(m + 1):
        dp[0][j] = (0, 0.0, ())
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            opts = [dp[i - 1][j], dp[i][j - 1]]
            pi, rj = p[i - 1], r[j - 1]
            d = abs(pred_events[pi]["start"] - ref_events[rj]["start"])
            if d <= onset_tolerance:
                c, cost, pairs = dp[i - 1][j - 1]
                opts.append((c + 1, cost + d, pairs + ((pi, rj),)))
            dp[i][j] = min(opts, key=lambda z: (-z[0], z[1], z[2]))
    return list(dp[n][m][2])


def _greedy_time_pairs(pred_indices, ref_indices, pred_events, ref_events, onset_tolerance):
    p = sorted(pred_indices, key=lambda i: (pred_events[i]["start"], i))
    r = sorted(ref_indices, key=lambda i: (ref_events[i]["start"], i))
    pairs = []
    i = j = 0
    while i < len(p) and j < len(r):
        ps = pred_events[p[i]]["start"]
        rs = ref_events[r[j]]["start"]
        if abs(ps - rs) <= onset_tolerance:
            pairs.append((p[i], r[j]))
            i += 1
            j += 1
        elif ps < rs - onset_tolerance:
            i += 1
        else:
            j += 1
    return pairs


def _group_match(pred_events, ref_events, pred_indices, ref_indices, key_fn, onset_tolerance, *, exact=False):
    pg = defaultdict(list)
    rg = defaultdict(list)
    for i in pred_indices:
        pg[key_fn(pred_events[i])].append(i)
    for i in ref_indices:
        rg[key_fn(ref_events[i])].append(i)
    pairs = []
    for key in sorted(set(pg) | set(rg), key=repr):
        matcher = _ordered_match if exact else _greedy_time_pairs
        pairs.extend(matcher(pg.get(key, []), rg.get(key, []), pred_events, ref_events, onset_tolerance))
    return pairs


def _remove_pairs(available_pred, available_ref, pairs):
    used_p = {p for p, _ in pairs}
    used_r = {r for _, r in pairs}
    return available_pred - used_p, available_ref - used_r


def _time_only_max_cardinality(pred_events, ref_events, onset_tolerance):
    p = sorted(range(len(pred_events)), key=lambda i: (pred_events[i]["start"], i))
    r = sorted(range(len(ref_events)), key=lambda i: (ref_events[i]["start"], i))
    i = j = 0
    count = 0
    while i < len(p) and j < len(r):
        ps = pred_events[p[i]]["start"]
        rs = ref_events[r[j]]["start"]
        if abs(ps - rs) <= onset_tolerance:
            count += 1
            i += 1
            j += 1
        elif ps < rs - onset_tolerance:
            i += 1
        else:
            j += 1
    return count


def staged_onset_label_matches(pred_events, ref_events, onset_tolerance=DEFAULT_ONSET_TOLERANCE_SECONDS):
    available_pred = set(range(len(pred_events)))
    available_ref = set(range(len(ref_events)))

    exact = _group_match(
        pred_events, ref_events, available_pred, available_ref,
        lambda e: (e["string"], e["fret"]), onset_tolerance, exact=True,
    )
    available_pred, available_ref = _remove_pairs(available_pred, available_ref, exact)

    same_string = _group_match(
        pred_events, ref_events, available_pred, available_ref,
        lambda e: e["string"], onset_tolerance,
    )
    same_string = [(p, r) for p, r in same_string if pred_events[p]["fret"] != ref_events[r]["fret"]]
    available_pred, available_ref = _remove_pairs(available_pred, available_ref, same_string)

    same_fret = _group_match(
        pred_events, ref_events, available_pred, available_ref,
        lambda e: e["fret"], onset_tolerance,
    )
    same_fret = [(p, r) for p, r in same_fret if pred_events[p]["string"] != ref_events[r]["string"]]
    available_pred, available_ref = _remove_pairs(available_pred, available_ref, same_fret)

    both_wrong = _greedy_time_pairs(
        available_pred, available_ref, pred_events, ref_events, onset_tolerance
    )
    available_pred, available_ref = _remove_pairs(available_pred, available_ref, both_wrong)

    return {
        "exactStringFret": exact,
        "fretWrongSameString": same_string,
        "stringWrongSameFret": same_fret,
        "bothStringAndFretWrong": both_wrong,
        "unmatchedPredicted": sorted(available_pred),
        "unmatchedReference": sorted(available_ref),
    }


def _quantiles(values):
    if not values:
        return {"mean": 0.0, "median": 0.0, "p90": 0.0, "max": 0.0}
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "p90": float(np.quantile(arr, 0.9)),
        "max": float(np.max(arr)),
    }


def temporal_run_diagnostics(pred_events, ref_events, exact_pairs, hop_seconds=DEFAULT_HOP_SECONDS):
    start_ms = []
    end_ms = []
    duration_ms = []
    overlap_fraction = []
    for pi, ri in exact_pairs:
        p, r = pred_events[pi], ref_events[ri]
        start_ms.append(abs(p["start"] - r["start"]) * 1000.0)
        end_ms.append(abs(p["end"] - r["end"]) * 1000.0)
        duration_ms.append(abs((p["end"] - p["start"]) - (r["end"] - r["start"])) * 1000.0)
        overlap = max(0.0, min(p["end"], r["end"]) - max(p["start"], r["start"]))
        ref_duration = max(1e-12, r["end"] - r["start"])
        overlap_fraction.append(overlap / ref_duration)

    pred_by_id = defaultdict(list)
    ref_by_id = defaultdict(list)
    for i, e in enumerate(pred_events):
        pred_by_id[(e["string"], e["fret"])].append(i)
    for i, e in enumerate(ref_events):
        ref_by_id[(e["string"], e["fret"])].append(i)

    fragmented_ref = 0
    merged_pred = 0
    for key, refs in ref_by_id.items():
        preds = pred_by_id.get(key, [])
        for ri in refs:
            r = ref_events[ri]
            overlaps = sum(
                pred_events[pi]["start"] < r["end"] and pred_events[pi]["end"] > r["start"]
                for pi in preds
            )
            if overlaps > 1:
                fragmented_ref += 1
    for key, preds in pred_by_id.items():
        refs = ref_by_id.get(key, [])
        for pi in preds:
            p = pred_events[pi]
            overlaps = sum(
                ref_events[ri]["start"] < p["end"] and ref_events[ri]["end"] > p["start"]
                for ri in refs
            )
            if overlaps > 1:
                merged_pred += 1

    one_frame_ms = hop_seconds * 1000.0
    return {
        "exactMatchedPairs": len(exact_pairs),
        "startAbsoluteErrorMs": _quantiles(start_ms),
        "endAbsoluteErrorMs": _quantiles(end_ms),
        "durationAbsoluteErrorMs": _quantiles(duration_ms),
        "referenceOverlapFraction": _quantiles(overlap_fraction),
        "exactPairsEndErrorOverOneFrame": sum(x > one_frame_ms + 1e-9 for x in end_ms),
        "fragmentedReferenceRuns": fragmented_ref,
        "mergedPredictedRuns": merged_pred,
        "predictedToReferenceRunRatio": (len(pred_events) / len(ref_events)) if ref_events else (1.0 if not pred_events else math.inf),
    }


def frame_activity_diagnostics(pred_states, ref_labels):
    pred = np.asarray(pred_states)
    ref = np.asarray(ref_labels)
    if ref.ndim != 2 or ref.shape[0] != NUM_STRINGS:
        raise ValueError("reference labels must be 6 x T")
    if pred.shape != (ref.shape[1], NUM_STRINGS):
        raise ValueError("predictions must be T x 6 and align to reference")
    pt = pred.T
    valid = ref != MASK
    ref_active = valid & (ref >= 0)
    pred_active = valid & (pt >= 0)
    exact = ref_active & pred_active & (ref == pt)
    wrong_fret = ref_active & pred_active & (ref != pt)
    fp = valid & (~ref_active) & pred_active
    fn = ref_active & (~pred_active)
    silent_correct = valid & (~ref_active) & (~pred_active)

    def counts_for_string(s):
        return {
            "valid": int(np.sum(valid[s])),
            "referenceActive": int(np.sum(ref_active[s])),
            "predictedActive": int(np.sum(pred_active[s])),
            "exactActive": int(np.sum(exact[s])),
            "wrongFretWhileActive": int(np.sum(wrong_fret[s])),
            "activityFalsePositive": int(np.sum(fp[s])),
            "activityFalseNegative": int(np.sum(fn[s])),
            "silentCorrect": int(np.sum(silent_correct[s])),
        }

    totals = {k: 0 for k in counts_for_string(0)}
    per_string = []
    for s in range(NUM_STRINGS):
        c = counts_for_string(s)
        per_string.append(c)
        for k, v in c.items():
            totals[k] += v
    ref_active_count = totals["referenceActive"]
    pred_active_count = totals["predictedActive"]
    totals["activeExactRecall"] = totals["exactActive"] / ref_active_count if ref_active_count else 1.0
    totals["activeExactPrecision"] = totals["exactActive"] / pred_active_count if pred_active_count else (1.0 if not ref_active_count else 0.0)
    totals["activityFpToFnRatio"] = (
        totals["activityFalsePositive"] / totals["activityFalseNegative"]
        if totals["activityFalseNegative"] else (0.0 if not totals["activityFalsePositive"] else math.inf)
    )
    return {"totals": totals, "perString": per_string}


def diagnose_capture(pred_states, ref_labels, hop_seconds=DEFAULT_HOP_SECONDS, onset_tolerance=DEFAULT_ONSET_TOLERANCE_SECONDS):
    ref = np.asarray(ref_labels)
    pred = np.asarray(pred_states)
    if ref.ndim != 2 or ref.shape[0] != NUM_STRINGS:
        raise ValueError("reference labels must be 6 x T")
    if pred.shape != (ref.shape[1], NUM_STRINGS):
        raise ValueError("predictions must be T x 6")
    mask = (ref == MASK).T
    masked_pred = pred.copy()
    masked_pred[mask] = -1
    ref_states = ref.T
    pred_events = events_from_states(masked_pred, mask, hop_seconds)
    ref_events = events_from_states(ref_states, mask, hop_seconds)

    staged = staged_onset_label_matches(pred_events, ref_events, onset_tolerance)
    exact_pairs = staged["exactStringFret"]
    exact_tp = len(exact_pairs)
    predicted_count = len(pred_events)
    reference_count = len(ref_events)
    fp = predicted_count - exact_tp
    fn = reference_count - exact_tp
    precision = exact_tp / predicted_count if predicted_count else (1.0 if not reference_count else 0.0)
    recall = exact_tp / reference_count if reference_count else (1.0 if not predicted_count else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    onset_matches = _time_only_max_cardinality(pred_events, ref_events, onset_tolerance)

    string_confusion = [[0 for _ in range(NUM_STRINGS)] for _ in range(NUM_STRINGS)]
    fret_confusion = [[0 for _ in range(20)] for _ in range(20)]
    pitch_correct_wrong_string = 0
    all_pairs = []
    for key in ("exactStringFret", "fretWrongSameString", "stringWrongSameFret", "bothStringAndFretWrong"):
        all_pairs.extend(staged[key])
    for pi, ri in all_pairs:
        p, r = pred_events[pi], ref_events[ri]
        string_confusion[r["string"]][p["string"]] += 1
        if 0 <= r["fret"] < 20 and 0 <= p["fret"] < 20:
            fret_confusion[r["fret"]][p["fret"]] += 1
        if p["string"] != r["string"]:
            pred_pitch = OPEN_MIDI[p["string"]] + p["fret"]
            ref_pitch = OPEN_MIDI[r["string"]] + r["fret"]
            if pred_pitch == ref_pitch:
                pitch_correct_wrong_string += 1

    label_counts = {
        "exactStringFret": len(staged["exactStringFret"]),
        "fretWrongSameString": len(staged["fretWrongSameString"]),
        "stringWrongSameFret": len(staged["stringWrongSameFret"]),
        "bothStringAndFretWrong": len(staged["bothStringAndFretWrong"]),
        "pitchCorrectWrongString": pitch_correct_wrong_string,
        "stagedMatched": len(all_pairs),
        "unmatchedPredicted": len(staged["unmatchedPredicted"]),
        "unmatchedReference": len(staged["unmatchedReference"]),
    }
    label_counts["stagedMatchCoverageVsOnsetMaximum"] = (
        label_counts["stagedMatched"] / onset_matches if onset_matches else 1.0
    )

    event_micro = {
        "referenceEvents": reference_count,
        "predictedEvents": predicted_count,
        "exactTruePositive": exact_tp,
        "falsePositive": fp,
        "falseNegative": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "onsetOnlyMatched": onset_matches,
        "onsetOnlyPrecision": onset_matches / predicted_count if predicted_count else (1.0 if not reference_count else 0.0),
        "onsetOnlyRecall": onset_matches / reference_count if reference_count else (1.0 if not predicted_count else 0.0),
    }
    op, or_ = event_micro["onsetOnlyPrecision"], event_micro["onsetOnlyRecall"]
    event_micro["onsetOnlyF1"] = 2 * op * or_ / (op + or_) if op + or_ else 0.0

    return {
        "eventMicro": event_micro,
        "onsetLabelDecomposition": label_counts,
        "stringConfusionRefRowsPredColumns": string_confusion,
        "fretConfusionRefRowsPredColumns": fret_confusion,
        "temporalRun": temporal_run_diagnostics(pred_events, ref_events, exact_pairs, hop_seconds),
        "frameActivity": frame_activity_diagnostics(masked_pred, ref),
    }


def merge_count_dicts(records, keys):
    out = {key: 0 for key in keys}
    for rec in records:
        for key in keys:
            out[key] += int(rec.get(key, 0))
    return out
