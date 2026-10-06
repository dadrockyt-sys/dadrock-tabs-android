"""Ambiguity-aware post-quantization pitch/voicing diagnostic for Go My Way.

Model-free and mutation-free. Compares frozen original Basic Pitch V4-origin guitar
predictions with the frozen 1/16-per-measure quantized candidate under identical
onset-only matching semantics.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import heapq
import json
import math
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

ONSET_TOLERANCE_SECONDS = 0.05
EXPECTED = {
    "candidate": "880446f4e93898395b91fa2b27a081817e93e7ed1883cf0d64940d22a453400e",
    "timing": "b87f122a007070d5a2abf0b676693c5ea7872ffcb04a06958ef103269c5f85f3",
    "rhythm": "d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555",
    "lead": "8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be",
}
EXPECTED_EVENT_COUNT = 1065


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sha(path: Path | str, expected: str, label: str) -> str:
    actual = sha256_file(path)
    if actual != expected:
        raise RuntimeError(f"{label} SHA-256 mismatch: expected {expected}, got {actual}")
    return actual


def verify_manifest_entry(manifest_path: Path | str, payload_path: Path | str) -> None:
    payload = Path(payload_path)
    target_name = payload.name
    entries = {}
    for raw in Path(manifest_path).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        digest, name = parts
        name = name.lstrip("*")
        entries[Path(name).name] = digest.lower()
    if target_name not in entries:
        raise RuntimeError(f"frozen evidence manifest has no entry for {target_name}")
    actual = sha256_file(payload)
    if actual != entries[target_name]:
        raise RuntimeError(
            f"frozen evidence manifest mismatch for {target_name}: expected {entries[target_name]}, got {actual}"
        )


def _finite_number(value, label: str) -> float:
    try:
        out = float(value)
    except Exception as exc:
        raise RuntimeError(f"{label} is not numeric") from exc
    if not math.isfinite(out):
        raise RuntimeError(f"{label} is not finite")
    return out


def _event_identity(event: dict, index: int) -> str:
    return str(event.get("id", f"index:{index}"))


def validate_events(events: Sequence[dict], label: str) -> None:
    seen = set()
    for i, event in enumerate(events):
        ident = _event_identity(event, i)
        if ident in seen:
            raise RuntimeError(f"{label} duplicate event identity: {ident}")
        seen.add(ident)
        midi = event.get("midi")
        if isinstance(midi, bool) or not isinstance(midi, int) or not 0 <= midi <= 127:
            raise RuntimeError(f"{label} invalid MIDI at {ident}: {midi}")
        start = _finite_number(event.get("start"), f"{label}.{ident}.start")
        if "end" in event:
            end = _finite_number(event.get("end"), f"{label}.{ident}.end")
            if end < start:
                raise RuntimeError(f"{label} end before start at {ident}")


def validate_frozen_pair(original: Sequence[dict], quantized: Sequence[dict], tol: float = 1e-8) -> dict:
    if len(original) != EXPECTED_EVENT_COUNT or len(quantized) != EXPECTED_EVENT_COUNT:
        raise RuntimeError(
            f"expected {EXPECTED_EVENT_COUNT} original and quantized events, got {len(original)} and {len(quantized)}"
        )
    validate_events(original, "original")
    validate_events(quantized, "quantized")
    max_duration_error = 0.0
    for i, (old, new) in enumerate(zip(original, quantized)):
        old_id = _event_identity(old, i)
        new_id = _event_identity(new, i)
        if old_id != new_id:
            raise RuntimeError(f"event identity/order mismatch at index {i}: {old_id} != {new_id}")
        if int(old["midi"]) != int(new["midi"]):
            raise RuntimeError(f"MIDI mutation at {old_id}")
        if "originalStart" in new and abs(float(new["originalStart"]) - float(old["start"])) > tol:
            raise RuntimeError(f"quantized originalStart mismatch at {old_id}")
        if ("end" in old) != ("end" in new):
            raise RuntimeError(f"duration schema mismatch at {old_id}")
        if "end" in old:
            old_duration = float(old["end"]) - float(old["start"])
            new_duration = float(new["end"]) - float(new["start"])
            err = abs(old_duration - new_duration)
            max_duration_error = max(max_duration_error, err)
            if err > tol:
                raise RuntimeError(f"duration mutation at {old_id}: error={err}")
    return {"count": len(original), "orderedIdentityMidiEqual": True, "maxDurationErrorSeconds": max_duration_error}


def excluded_measures(ref: dict) -> set[int]:
    policy = ref.get("normalizationPolicy", {})
    out = set(int(x) for x in policy.get("excludedSourceMeasures", []))
    if policy.get("measure88Excluded") is True:
        out.add(88)
    return out


def boundaries_map(timing: dict) -> Dict[int, dict]:
    rows = {int(r["measureNumber"]): r for r in timing["measureBoundaries"]}
    if set(rows) != set(range(1, 114)):
        raise RuntimeError("timing map must cover measures 1..113")
    for m, row in rows.items():
        start = _finite_number(row["startSeconds"], f"timing.m{m}.start")
        end = _finite_number(row["endSeconds"], f"timing.m{m}.end")
        duration = _finite_number(row["durationSeconds"], f"timing.m{m}.duration")
        if end <= start or abs((end - start) - duration) > 1e-6:
            raise RuntimeError(f"invalid timing boundary for measure {m}")
    return rows


def scorer_targets(role: str, ref: dict, timing: dict) -> Tuple[List[dict], set[int]]:
    bounds = boundaries_map(timing)
    excluded = excluded_measures(ref)
    targets = []
    for i, note in enumerate(ref.get("notes", [])):
        m = int(note["measure"])
        if m in excluded:
            raise RuntimeError(f"{role} scorer unexpectedly contains excluded measure {m}")
        step = _finite_number(note["step"], f"{role}.target.{i}.step")
        b = bounds[m]
        start = float(b["startSeconds"]) + (step / 16.0) * float(b["durationSeconds"])
        midi = int(note["midi"])
        if not 0 <= midi <= 127:
            raise RuntimeError(f"{role} invalid target MIDI {midi}")
        targets.append(
            {
                "id": f"{role}:{i}:m{m}:s{step}",
                "role": role,
                "midi": midi,
                "start": start,
                "measure": m,
                "step": step,
            }
        )
    targets.sort(key=lambda x: (x["start"], x["midi"], x["id"]))
    return targets, excluded


def measure_for_time(t: float, timing: dict) -> int | None:
    for row in timing["measureBoundaries"]:
        if float(row["startSeconds"]) <= t < float(row["endSeconds"]):
            return int(row["measureNumber"])
    return None


def classify_event_for_role(event: dict, timing: dict, excluded: set[int]) -> dict:
    t = float(event["start"])
    first = float(timing["measureBoundaries"][0]["startSeconds"])
    last = float(timing["measureBoundaries"][-1]["endSeconds"])
    if t < first:
        return {"eligible": False, "reason": "beforeWindow", "measure": None}
    if t >= last:
        return {"eligible": False, "reason": "atOrAfterFinalEndpoint", "measure": None}
    measure = measure_for_time(t, timing)
    if measure is None:
        return {"eligible": False, "reason": "unmapped", "measure": None}
    if measure in excluded:
        return {"eligible": False, "reason": "excludedMeasure", "measure": measure}
    return {"eligible": True, "reason": "eligible", "measure": measure}


def filter_predictions(events: Sequence[dict], timing: dict, excluded: set[int]) -> Tuple[List[dict], dict]:
    out = []
    counts = collections.Counter()
    by_identity = {}
    for i, event in enumerate(events):
        status = classify_event_for_role(event, timing, excluded)
        counts[status["reason"]] += 1
        by_identity[_event_identity(event, i)] = status
        if status["eligible"]:
            row = dict(event)
            row["measure"] = status["measure"]
            row["id"] = _event_identity(event, i)
            out.append(row)
    return out, {"counts": dict(counts), "byIdentity": by_identity}


def boundary_migration_audit(original: Sequence[dict], quantized: Sequence[dict], timing: dict, excluded: set[int]) -> dict:
    migrations = []
    for i, (old, new) in enumerate(zip(original, quantized)):
        ident = _event_identity(old, i)
        a = classify_event_for_role(old, timing, excluded)
        b = classify_event_for_role(new, timing, excluded)
        if (a["eligible"], a["reason"], a["measure"]) != (b["eligible"], b["reason"], b["measure"]):
            migrations.append(
                {
                    "id": ident,
                    "midi": int(old["midi"]),
                    "originalStart": float(old["start"]),
                    "quantizedStart": float(new["start"]),
                    "from": a,
                    "to": b,
                }
            )
    return {
        "count": len(migrations),
        "eligibleToIneligible": sum(1 for x in migrations if x["from"]["eligible"] and not x["to"]["eligible"]),
        "ineligibleToEligible": sum(1 for x in migrations if not x["from"]["eligible"] and x["to"]["eligible"]),
        "measureOrExclusionStatusChanged": len(migrations),
        "events": migrations,
    }


def candidate_edges(preds: Sequence[dict], targets: Sequence[dict], tol: float = ONSET_TOLERANCE_SECONDS) -> List[Tuple[float, int, int]]:
    edges = []
    for pi, pred in enumerate(preds):
        ps = float(pred["start"])
        for ti, target in enumerate(targets):
            d = abs(ps - float(target["start"]))
            if d <= tol + 1e-12:
                edges.append((d, pi, ti))
    return edges


def legacy_greedy_match(preds: Sequence[dict], targets: Sequence[dict], tol: float = ONSET_TOLERANCE_SECONDS) -> List[dict]:
    edges = candidate_edges(preds, targets, tol)
    edges.sort(key=lambda x: (x[0], x[1], x[2]))
    used_p = set()
    used_t = set()
    chosen = []
    for d, pi, ti in edges:
        if pi in used_p or ti in used_t:
            continue
        used_p.add(pi)
        used_t.add(ti)
        chosen.append((d, pi, ti))
    return match_rows(preds, targets, chosen)


class _Edge:
    __slots__ = ("to", "rev", "cap", "cost", "meta")
    def __init__(self, to, rev, cap, cost, meta=None):
        self.to = to
        self.rev = rev
        self.cap = cap
        self.cost = cost
        self.meta = meta


def _add_edge(graph, u, v, cap, cost, meta=None):
    fwd = _Edge(v, len(graph[v]), cap, cost, meta)
    rev = _Edge(u, len(graph[u]), 0, -cost, None)
    graph[u].append(fwd)
    graph[v].append(rev)


def max_cardinality_min_time_match(preds: Sequence[dict], targets: Sequence[dict], tol: float = ONSET_TOLERANCE_SECONDS) -> List[dict]:
    edges = candidate_edges(preds, targets, tol)
    p_count = len(preds)
    t_count = len(targets)
    source = 0
    p0 = 1
    t0 = p0 + p_count
    sink = t0 + t_count
    n = sink + 1
    graph = [[] for _ in range(n)]
    for pi in range(p_count):
        _add_edge(graph, source, p0 + pi, 1, 0)
    for ti in range(t_count):
        _add_edge(graph, t0 + ti, sink, 1, 0)
    max_matches = min(p_count, t_count)
    tie_base = (p_count + 1) * (t_count + 1) * (max_matches + 1) + 1
    for d, pi, ti in edges:
        nanos = int(round(d * 1_000_000_000))
        tie = pi * (t_count + 1) + ti
        _add_edge(graph, p0 + pi, t0 + ti, 1, nanos * tie_base + tie, (d, pi, ti))

    potential = [0] * n
    while True:
        inf = 10**80
        dist = [inf] * n
        prev_v = [-1] * n
        prev_e = [-1] * n
        dist[source] = 0
        heap = [(0, source)]
        while heap:
            cur, u = heapq.heappop(heap)
            if cur != dist[u]:
                continue
            for ei, e in enumerate(graph[u]):
                if e.cap <= 0:
                    continue
                nd = cur + e.cost + potential[u] - potential[e.to]
                if nd < dist[e.to] or (nd == dist[e.to] and (u, ei) < (prev_v[e.to], prev_e[e.to])):
                    dist[e.to] = nd
                    prev_v[e.to] = u
                    prev_e[e.to] = ei
                    heapq.heappush(heap, (nd, e.to))
        if dist[sink] == inf:
            break
        for v in range(n):
            if dist[v] < inf:
                potential[v] += dist[v]
        v = sink
        while v != source:
            u = prev_v[v]
            ei = prev_e[v]
            if u < 0:
                raise RuntimeError("internal matching path reconstruction failure")
            e = graph[u][ei]
            e.cap -= 1
            graph[v][e.rev].cap += 1
            v = u

    chosen = []
    for pi in range(p_count):
        for e in graph[p0 + pi]:
            if e.meta is not None and e.cap == 0:
                chosen.append(e.meta)
    chosen.sort(key=lambda x: (x[1], x[2]))
    return match_rows(preds, targets, chosen)


def match_rows(preds: Sequence[dict], targets: Sequence[dict], chosen: Iterable[Tuple[float, int, int]]) -> List[dict]:
    rows = []
    for d, pi, ti in chosen:
        pred = preds[pi]
        target = targets[ti]
        delta = int(pred["midi"]) - int(target["midi"])
        rows.append(
            {
                "predictionIndex": pi,
                "targetIndex": ti,
                "predictionId": pred["id"],
                "targetId": target["id"],
                "predictionStart": float(pred["start"]),
                "targetStart": float(target["start"]),
                "onsetErrorSeconds": float(d),
                "predictionMidi": int(pred["midi"]),
                "targetMidi": int(target["midi"]),
                "midiDelta": delta,
                "measure": int(target["measure"]),
                "step": float(target["step"]),
            }
        )
    rows.sort(key=lambda r: (r["predictionStart"], r["predictionMidi"], r["predictionId"], r["targetId"]))
    return rows


def matching_components(preds: Sequence[dict], targets: Sequence[dict], tol: float = ONSET_TOLERANCE_SECONDS) -> Tuple[List[dict], Dict[Tuple[str, int], int]]:
    edges = candidate_edges(preds, targets, tol)
    p_adj = collections.defaultdict(set)
    t_adj = collections.defaultdict(set)
    for _, pi, ti in edges:
        p_adj[pi].add(ti)
        t_adj[ti].add(pi)
    seen_p = set()
    seen_t = set()
    components = []
    membership = {}
    for seed in sorted(p_adj):
        if seed in seen_p:
            continue
        queue = [("p", seed)]
        p_nodes = set()
        t_nodes = set()
        while queue:
            side, idx = queue.pop()
            if side == "p":
                if idx in seen_p:
                    continue
                seen_p.add(idx)
                p_nodes.add(idx)
                for ti in p_adj[idx]:
                    queue.append(("t", ti))
            else:
                if idx in seen_t:
                    continue
                seen_t.add(idx)
                t_nodes.add(idx)
                for pi in t_adj[idx]:
                    queue.append(("p", pi))
        comp_id = len(components)
        for pi in p_nodes:
            membership[("p", pi)] = comp_id
        for ti in t_nodes:
            membership[("t", ti)] = comp_id
        pred_midis = collections.Counter(int(preds[i]["midi"]) for i in p_nodes)
        target_midis = collections.Counter(int(targets[i]["midi"]) for i in t_nodes)
        multiset_overlap = sum(min(pred_midis[m], target_midis[m]) for m in pred_midis.keys() | target_midis.keys())
        p_degrees = [len(p_adj[i]) for i in p_nodes]
        t_degrees = [len(t_adj[i]) for i in t_nodes]
        ambiguous = any(x > 1 for x in p_degrees + t_degrees)
        pred_starts = [float(preds[i]["start"]) for i in p_nodes]
        targ_starts = [float(targets[i]["start"]) for i in t_nodes]
        simultaneous_like = (
            len(p_nodes) >= 2
            and len(t_nodes) >= 2
            and (max(pred_starts) - min(pred_starts) <= 0.001 or max(targ_starts) - min(targ_starts) <= 0.001)
        )
        edge_count = sum(len(p_adj[i]) for i in p_nodes)
        components.append(
            {
                "componentId": comp_id,
                "predictionCount": len(p_nodes),
                "targetCount": len(t_nodes),
                "eligibleEdgeCount": edge_count,
                "ambiguous": ambiguous,
                "simultaneousChordLike": simultaneous_like,
                "pairingInvariantPitchMultisetExactOverlap": multiset_overlap,
                "pairingInvariantPitchMultisetMaxDenominator": min(len(p_nodes), len(t_nodes)),
                "predictionMidis": sorted(pred_midis.elements()),
                "targetMidis": sorted(target_midis.elements()),
            }
        )
    return components, membership


def delta_summary(rows: Sequence[dict]) -> dict:
    deltas = [int(r["midiDelta"]) for r in rows]
    hist = collections.Counter(deltas)
    abs_values = [abs(x) for x in deltas]
    buckets = {
        "exact": sum(1 for x in deltas if x == 0),
        "abs1": sum(1 for x in deltas if abs(x) == 1),
        "abs2": sum(1 for x in deltas if abs(x) == 2),
        "abs3to5": sum(1 for x in deltas if 3 <= abs(x) <= 5),
        "abs12": sum(1 for x in deltas if abs(x) == 12),
        "other": sum(1 for x in deltas if not (x == 0 or abs(x) in (1, 2, 12) or 3 <= abs(x) <= 5)),
    }
    if sum(buckets.values()) != len(deltas):
        raise RuntimeError("internal bucket partition failure")
    pc_nonzero = sum(1 for x in deltas if x != 0 and x % 12 == 0)
    return {
        "exactMidi": buckets["exact"],
        "exactMidiRate": buckets["exact"] / len(deltas) if deltas else None,
        "pitchClassCorrectNonzeroOctaveError": pc_nonzero,
        "pitchClassCorrectNonzeroOctaveRate": pc_nonzero / len(deltas) if deltas else None,
        "meanAbsoluteMidiErrorSemitones": sum(abs_values) / len(abs_values) if abs_values else None,
        "buckets": buckets,
        "signedMidiDeltaHistogram": {str(k): hist[k] for k in sorted(hist)},
    }


def summarize_matching(preds: Sequence[dict], targets: Sequence[dict], rows: Sequence[dict], components: Sequence[dict], membership: dict) -> dict:
    matched_p = {int(r["predictionIndex"]) for r in rows}
    matched_t = {int(r["targetIndex"]) for r in rows}
    ambiguous_rows = []
    unambiguous_rows = []
    for row in rows:
        comp_id = membership.get(("p", int(row["predictionIndex"])))
        row["matchingComponentId"] = comp_id
        ambiguous = bool(comp_id is not None and components[comp_id]["ambiguous"])
        row["assignmentAmbiguousComponent"] = ambiguous
        (ambiguous_rows if ambiguous else unambiguous_rows).append(row)
    total_time_error = sum(float(r["onsetErrorSeconds"]) for r in rows)
    return {
        "eligiblePredictionCount": len(preds),
        "eligibleTargetCount": len(targets),
        "onsetMatchedCount": len(rows),
        "unmatchedPredictionCount": len(preds) - len(matched_p),
        "unmatchedTargetCount": len(targets) - len(matched_t),
        "onsetMatchedTargetRecall": len(rows) / len(targets) if targets else None,
        "onsetMatchedPredictionRate": len(rows) / len(preds) if preds else None,
        "totalAbsoluteOnsetErrorSeconds": total_time_error,
        "pitch": delta_summary(rows),
        "ambiguousMatched": {"count": len(ambiguous_rows), "pitch": delta_summary(ambiguous_rows)},
        "unambiguousMatched": {"count": len(unambiguous_rows), "pitch": delta_summary(unambiguous_rows)},
        "wrongMidiAmongMatched": sum(1 for r in rows if int(r["midiDelta"]) != 0),
    }


def analyze_variant(events: Sequence[dict], targets: Sequence[dict], timing: dict, excluded: set[int]) -> dict:
    preds, filter_audit = filter_predictions(events, timing, excluded)
    legacy_rows = legacy_greedy_match(preds, targets)
    primary_rows = max_cardinality_min_time_match(preds, targets)
    components, membership = matching_components(preds, targets)
    primary_summary = summarize_matching(preds, targets, primary_rows, components, membership)
    legacy_summary = summarize_matching(preds, targets, legacy_rows, components, membership)
    ambiguous_components = [c for c in components if c["ambiguous"]]
    return {
        "filterAudit": {"counts": filter_audit["counts"]},
        "legacyGreedyAssignmentDependent": {
            "summary": legacy_summary,
            "matches": legacy_rows,
        },
        "primaryMaxCardinalityMinTimeError": {
            "summary": primary_summary,
            "matches": primary_rows,
        },
        "matchingAmbiguity": {
            "componentCount": len(components),
            "ambiguousComponentCount": len(ambiguous_components),
            "simultaneousChordLikeAmbiguousComponentCount": sum(1 for c in ambiguous_components if c["simultaneousChordLike"]),
            "ambiguousComponents": ambiguous_components,
            "allComponentsPairingInvariantPitchMultisetOverlap": sum(c["pairingInvariantPitchMultisetExactOverlap"] for c in components),
            "ambiguousComponentsPairingInvariantPitchMultisetOverlap": sum(c["pairingInvariantPitchMultisetExactOverlap"] for c in ambiguous_components),
        },
    }


def meter_semantics_audit(timing: dict, refs: Dict[str, dict]) -> dict:
    rows = boundaries_map(timing)
    meter_keys = sorted({k for r in timing["measureBoundaries"] for k in r if "meter" in k.lower() or "time" in k.lower() and "seconds" not in k.lower()})
    focus = {}
    for m in (104, 105):
        row = rows[m]
        focus[str(m)] = {
            "startSeconds": float(row["startSeconds"]),
            "endSeconds": float(row["endSeconds"]),
            "durationSeconds": float(row["durationSeconds"]),
            "sourceSteps": {
                role: sorted({float(n["step"]) for n in refs[role].get("notes", []) if int(n["measure"]) == m})
                for role in ("rhythm", "lead")
            },
        }
    return {
        "gridSemantics": "Both quantizer and scorer use 16 equal subdivisions of each measure duration via step/16; this is not asserted to equal notated sixteenth notes in non-4/4 meter.",
        "timingMapMeterMetadataKeysObserved": meter_keys,
        "measures104And105": focus,
    }


def combined_convention_audit(rhythm_targets: Sequence[dict], lead_targets: Sequence[dict], rhythm_ex: set[int], lead_ex: set[int]) -> dict:
    key_r = collections.Counter((round(float(t["start"]), 12), int(t["midi"])) for t in rhythm_targets)
    key_l = collections.Counter((round(float(t["start"]), 12), int(t["midi"])) for t in lead_targets)
    duplicates = []
    for key in sorted(key_r.keys() & key_l.keys()):
        overlap = min(key_r[key], key_l[key])
        if overlap:
            duplicates.append({"startSeconds": key[0], "midi": key[1], "crossRoleCoincidentMultiplicity": overlap})
    return {
        "legacyConvention": "Combined scoring concatenates rhythm and lead targets and filters predictions using the union of role exclusions; coincident same-pitch targets are not deduplicated.",
        "rhythmExclusions": sorted(rhythm_ex),
        "leadExclusions": sorted(lead_ex),
        "unionExclusions": sorted(rhythm_ex | lead_ex),
        "coincidentSamePitchCrossRoleTargetCount": sum(x["crossRoleCoincidentMultiplicity"] for x in duplicates),
        "coincidentSamePitchCrossRoleTargets": duplicates,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--note-evidence", required=True)
    ap.add_argument("--note-evidence-manifest", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--timing-map", required=True)
    ap.add_argument("--rhythm-reference", required=True)
    ap.add_argument("--lead-reference", required=True)
    ap.add_argument("--output-json", required=True)
    args = ap.parse_args()

    paths = {k: Path(getattr(args, k)) for k in ("note_evidence", "note_evidence_manifest", "candidate", "timing_map", "rhythm_reference", "lead_reference")}
    before_candidate_sha = verify_sha(paths["candidate"], EXPECTED["candidate"], "candidate")
    verify_sha(paths["timing_map"], EXPECTED["timing"], "timing map")
    verify_sha(paths["rhythm_reference"], EXPECTED["rhythm"], "rhythm reference")
    verify_sha(paths["lead_reference"], EXPECTED["lead"], "lead reference")
    verify_manifest_entry(paths["note_evidence_manifest"], paths["note_evidence"])

    evidence = json.loads(paths["note_evidence"].read_text())
    candidate = json.loads(paths["candidate"].read_text())
    timing = json.loads(paths["timing_map"].read_text())
    refs = {
        "rhythm": json.loads(paths["rhythm_reference"].read_text()),
        "lead": json.loads(paths["lead_reference"].read_text()),
    }

    if candidate.get("timingMapSha256") != EXPECTED["timing"]:
        raise RuntimeError("candidate timingMapSha256 mismatch")
    evidence_timing = evidence.get("timingMap", {}).get("sha256")
    if evidence_timing != EXPECTED["timing"]:
        raise RuntimeError(f"original evidence timing-map identity mismatch: {evidence_timing}")

    original_events = evidence["predictions"]["guitar"]
    quantized_events = candidate["predictions"]["guitar"]
    identity_audit = validate_frozen_pair(original_events, quantized_events)

    targets = {}
    exclusions = {}
    for role in ("rhythm", "lead"):
        targets[role], exclusions[role] = scorer_targets(role, refs[role], timing)

    roles = {}
    for role in ("rhythm", "lead"):
        roles[role] = {
            "original": analyze_variant(original_events, targets[role], timing, exclusions[role]),
            "quantized": analyze_variant(quantized_events, targets[role], timing, exclusions[role]),
            "boundaryMigrationAudit": boundary_migration_audit(original_events, quantized_events, timing, exclusions[role]),
        }

    after_candidate_sha = sha256_file(paths["candidate"])
    if after_candidate_sha != before_candidate_sha:
        raise RuntimeError("candidate bytes changed during diagnostic")

    out = {
        "schemaVersion": 2,
        "kind": "gomyway-post-quantization-pitch-voicing-diagnostic-v2",
        "modelFree": True,
        "predictionMutation": False,
        "onsetToleranceSeconds": ONSET_TOLERANCE_SECONDS,
        "identities": {
            "candidateArtifactId": 11391794891,
            "candidateSha256": before_candidate_sha,
            "noteEvidenceArtifactId": 11282827368,
            "noteEvidenceSha256": sha256_file(paths["note_evidence"]),
            "timingMapSha256": EXPECTED["timing"],
            "rhythmReferenceSha256": EXPECTED["rhythm"],
            "leadReferenceSha256": EXPECTED["lead"],
            "candidateSha256AfterDiagnostic": after_candidate_sha,
        },
        "frozenPairIdentityAudit": identity_audit,
        "matchingPolicy": {
            "legacy": "greedy by absolute onset error, then prediction index, then target index; assignment-dependent and retained only for historical comparability",
            "primary": "maximum-cardinality onset-only matching followed by minimum total absolute onset error; pitch is never used to choose a pair",
            "ambiguity": "connected eligibility components with any degree >1 are flagged ambiguous; pairing-invariant MIDI multiset overlap is reported for those components instead of treating a pitch-optimized assignment as unbiased accuracy",
        },
        "roles": roles,
        "meterSemanticsAudit": meter_semantics_audit(timing, refs),
        "combinedTargetConventionAudit": combined_convention_audit(targets["rhythm"], targets["lead"], exclusions["rhythm"], exclusions["lead"]),
        "historicalLegacyContextOnly": {
            "preQuantizationRhythmOnsetMatchedTargetRecall": 0.4693,
            "preQuantizationRhythmExactMidiAmongOnsetMatches": 0.3311,
            "preQuantizationLeadOnsetMatchedTargetRecall": 0.4966,
            "preQuantizationLeadExactMidiAmongOnsetMatches": 0.4054,
            "warning": "Do not compare these rounded historical percentages against V2 primary numbers as if matcher semantics were identical. V2 reports original and quantized under the same V2 rules.",
        },
        "legacyFrozenScoreContext": {
            "rhythm": {"originalF1": 0.3182496270512183, "quantizedF1": 0.33316757831924415},
            "lead": {"originalF1": 0.1784037558685446, "quantizedF1": 0.19047619047619047},
            "combinedGuitar": {"originalF1": 0.3504308576118178, "quantizedF1": 0.37012720558063195},
            "warning": "Frozen legacy scorer values are preserved unchanged and are not recomputed with V2 matching semantics.",
        },
        "interpretationBoundary": "Diagnostic only. Separate unmatched target events from wrong MIDI among onset-matched pairs. Ambiguous-component assignment-dependent pitch deltas are descriptive only. No pitch, timing, role, model, or threshold mutation is authorized by this result.",
    }
    Path(args.output_json).write_text(json.dumps(out, indent=2, sort_keys=True) + "
")
    print(json.dumps({role: {variant: roles[role][variant]["primaryMaxCardinalityMinTimeError"]["summary"] for variant in ("original", "quantized")} for role in roles}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
