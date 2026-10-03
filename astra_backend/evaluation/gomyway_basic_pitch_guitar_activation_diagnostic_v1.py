"""Post-freeze descriptive diagnostic for raw Basic Pitch guitar activations.

This script is deliberately diagnostic-only:
- raw activations must already be frozen;
- professional rhythm/lead references are read only after freeze;
- no threshold search, no candidate mutation, no pitch correction;
- V4-origin timing remains fixed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

MIDI_OFFSET = 21
ONSET_THRESHOLD = 0.5
FRAME_THRESHOLD = 0.3
TOL_SECONDS = 0.05
EXPECTED = {
    "rhythm": "d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555",
    "lead": "8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be",
}
EXPECTED_TIMING_SHA256 = "b87f122a007070d5a2abf0b676693c5ea7872ffcb04a06958ef103269c5f85f3"

def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

def excluded(ref):
    p = ref.get("normalizationPolicy", {})
    s = set(int(x) for x in p.get("excludedSourceMeasures", []))
    if p.get("measure88Excluded") is True:
        s.add(88)
    return s

def targets(ref, timing):
    bm = {int(r["measureNumber"]): r for r in timing["measureBoundaries"]}
    ex = excluded(ref)
    out = []
    for n in ref["notes"]:
        m = int(n["measure"])
        if m in ex or m not in bm:
            continue
        b = bm[m]
        t = float(b["startSeconds"]) + (float(n["step"]) / 16.0) * float(b["durationSeconds"])
        out.append({"midi": int(n["midi"]), "time": t, "measure": m})
    return out, ex

def thresholded_present(target, preds):
    for p in preds:
        if int(p["midi"]) == int(target["midi"]) and abs(float(p["start"]) - target["time"]) <= TOL_SECONDS:
            return True
    return False

def finite(v):
    return float(v) if np.isfinite(v) else None

def summarize(values):
    a = np.asarray(values, dtype=float)
    if not len(a):
        return {"n": 0}
    return {
        "n": int(len(a)),
        "mean": finite(np.mean(a)),
        "median": finite(np.median(a)),
        "p25": finite(np.percentile(a, 25)),
        "p75": finite(np.percentile(a, 75)),
        "p90": finite(np.percentile(a, 90)),
        "max": finite(np.max(a)),
    }

def sample_pitch(arr, frame, midi):
    idx = int(midi) - MIDI_OFFSET
    if idx < 0 or idx >= arr.shape[1]:
        return None
    lo = max(0, frame - 2)
    hi = min(arr.shape[0], frame + 3)
    return float(np.max(arr[lo:hi, idx]))

def frame_for_time(t, nframes, duration):
    if duration <= 0:
        raise ValueError("invalid duration")
    # Frozen model output is already unwrapped to the source duration.  Use the
    # artifact's exact frame count and duration, avoiding a second inference.
    x = int(round((float(t) / duration) * max(0, nframes - 1)))
    return min(max(x, 0), nframes - 1)

def role_diagnostic(role, ref, timing, preds, note, onset, duration):
    targs, _ = targets(ref, timing)
    rows = []
    for t in targs:
        frame = frame_for_time(t["time"], note.shape[0], duration)
        midi = t["midi"]
        note_exact = sample_pitch(note, frame, midi)
        onset_exact = sample_pitch(onset, frame, midi)

        octave_vals_note = [sample_pitch(note, frame, midi + d) for d in (-24, -12, 12, 24)]
        octave_vals_onset = [sample_pitch(onset, frame, midi + d) for d in (-24, -12, 12, 24)]
        octave_vals_note = [v for v in octave_vals_note if v is not None]
        octave_vals_onset = [v for v in octave_vals_onset if v is not None]

        local_note = [sample_pitch(note, frame, midi + d) for d in (-5,-4,-3,-2,-1,1,2,3,4,5)]
        local_onset = [sample_pitch(onset, frame, midi + d) for d in (-5,-4,-3,-2,-1,1,2,3,4,5)]
        local_note = [v for v in local_note if v is not None]
        local_onset = [v for v in local_onset if v is not None]

        pitch_vec = note[max(0, frame-2):min(note.shape[0], frame+3)].max(axis=0)
        idx = midi - MIDI_OFFSET
        if 0 <= idx < len(pitch_vec):
            rank = int(1 + np.sum(pitch_vec > pitch_vec[idx]))
        else:
            rank = None

        present = thresholded_present(t, preds)
        rows.append({
            "midi": midi,
            "time": t["time"],
            "measure": t["measure"],
            "thresholdedExactEventPresent": present,
            "noteExact": note_exact,
            "onsetExact": onset_exact,
            "noteOctaveAliasMax": max(octave_vals_note) if octave_vals_note else None,
            "onsetOctaveAliasMax": max(octave_vals_onset) if octave_vals_onset else None,
            "noteNearbySemitoneMax": max(local_note) if local_note else None,
            "onsetNearbySemitoneMax": max(local_onset) if local_onset else None,
            "notePitchRank": rank,
        })

    missing = [r for r in rows if not r["thresholdedExactEventPresent"]]
    def vals(key, source=rows):
        return [r[key] for r in source if r[key] is not None]

    return {
        "targetCount": len(rows),
        "thresholdedExactEventPresentCount": sum(1 for r in rows if r["thresholdedExactEventPresent"]),
        "thresholdedExactEventMissingCount": len(missing),
        "allTargets": {
            "noteExact": summarize(vals("noteExact")),
            "onsetExact": summarize(vals("onsetExact")),
            "noteOctaveAliasMax": summarize(vals("noteOctaveAliasMax")),
            "onsetOctaveAliasMax": summarize(vals("onsetOctaveAliasMax")),
            "noteNearbySemitoneMax": summarize(vals("noteNearbySemitoneMax")),
            "onsetNearbySemitoneMax": summarize(vals("onsetNearbySemitoneMax")),
            "notePitchRank": summarize(vals("notePitchRank")),
        },
        "missingThresholdedExactEvents": {
            "count": len(missing),
            "noteExact": summarize(vals("noteExact", missing)),
            "onsetExact": summarize(vals("onsetExact", missing)),
            "noteAtOrAboveFrozenFrameThreshold": sum(
                1 for r in missing if r["noteExact"] is not None and r["noteExact"] >= FRAME_THRESHOLD
            ),
            "onsetAtOrAboveFrozenOnsetThreshold": sum(
                1 for r in missing if r["onsetExact"] is not None and r["onsetExact"] >= ONSET_THRESHOLD
            ),
            "eitherAtOrAboveFrozenThreshold": sum(
                1 for r in missing
                if (r["noteExact"] is not None and r["noteExact"] >= FRAME_THRESHOLD)
                or (r["onsetExact"] is not None and r["onsetExact"] >= ONSET_THRESHOLD)
            ),
            "fixedDescriptiveBins": {
                "note": {
                    "lt_0_10": sum(1 for r in missing if r["noteExact"] is not None and r["noteExact"] < 0.10),
                    "0_10_to_0_20": sum(1 for r in missing if r["noteExact"] is not None and 0.10 <= r["noteExact"] < 0.20),
                    "0_20_to_0_30": sum(1 for r in missing if r["noteExact"] is not None and 0.20 <= r["noteExact"] < 0.30),
                    "ge_0_30": sum(1 for r in missing if r["noteExact"] is not None and r["noteExact"] >= 0.30),
                },
                "onset": {
                    "lt_0_10": sum(1 for r in missing if r["onsetExact"] is not None and r["onsetExact"] < 0.10),
                    "0_10_to_0_30": sum(1 for r in missing if r["onsetExact"] is not None and 0.10 <= r["onsetExact"] < 0.30),
                    "0_30_to_0_50": sum(1 for r in missing if r["onsetExact"] is not None and 0.30 <= r["onsetExact"] < 0.50),
                    "ge_0_50": sum(1 for r in missing if r["onsetExact"] is not None and r["onsetExact"] >= 0.50),
                },
            },
        },
        "rows": rows,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--activations-npz", required=True)
    ap.add_argument("--activations-meta", required=True)
    ap.add_argument("--note-evidence", required=True)
    ap.add_argument("--timing-map", required=True)
    ap.add_argument("--rhythm-reference", required=True)
    ap.add_argument("--lead-reference", required=True)
    ap.add_argument("--output-json", required=True)
    a = ap.parse_args()

    meta = json.loads(Path(a.activations_meta).read_text())
    if sha(a.activations_npz) != meta["npzSha256"]:
        raise RuntimeError("activation NPZ hash mismatch")
    if sha(a.timing_map) != EXPECTED_TIMING_SHA256:
        raise RuntimeError("V4-origin timing hash mismatch")

    z = np.load(a.activations_npz)
    if "note" not in z.files or "onset" not in z.files:
        raise RuntimeError(f"required arrays missing: {z.files}")
    note = np.asarray(z["note"], dtype=float)
    onset = np.asarray(z["onset"], dtype=float)
    if note.ndim != 2 or onset.ndim != 2 or note.shape != onset.shape:
        raise RuntimeError(f"unexpected note/onset shapes: {note.shape}, {onset.shape}")
    if note.shape[1] != 88:
        raise RuntimeError(f"unexpected Basic Pitch note-bin count: {note.shape[1]}")

    timing = json.loads(Path(a.timing_map).read_text())
    evidence = json.loads(Path(a.note_evidence).read_text())
    guitar_preds = evidence["predictions"]["guitar"]
    duration = float(meta["audioDurationSeconds"])

    roles = {}
    for role in ("rhythm", "lead"):
        rp = getattr(a, f"{role}_reference")
        if sha(rp) != EXPECTED[role]:
            raise RuntimeError(f"{role} reference hash mismatch")
        ref = json.loads(Path(rp).read_text())
        roles[role] = role_diagnostic(role, ref, timing, guitar_preds, note, onset, duration)

    out = {
        "schemaVersion": 1,
        "kind": "gomyway-basic-pitch-guitar-activation-diagnostic-v1",
        "diagnosticOnly": True,
        "referenceReadOnlyAfterActivationFreeze": True,
        "thresholdSearch": False,
        "candidateMutation": False,
        "frozenThresholdsForAttributionOnly": {
            "onset": ONSET_THRESHOLD,
            "frame": FRAME_THRESHOLD,
        },
        "activationNpZSha256": sha(a.activations_npz),
        "activationMetaSha256": sha(a.activations_meta),
        "timingMapSha256": sha(a.timing_map),
        "roles": roles,
        "interpretationBoundary": (
            "Descriptive attribution only. Fixed bins and frozen Basic Pitch defaults are not "
            "optimized thresholds and do not constitute a new decoder."
        ),
    }
    Path(a.output_json).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: {x: v[x] for x in ("targetCount","thresholdedExactEventPresentCount","thresholdedExactEventMissingCount")} for k,v in roles.items()}, indent=2))

if __name__ == "__main__":
    main()
