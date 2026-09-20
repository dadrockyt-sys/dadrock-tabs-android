"""Reference-blind octave-supported fundamental refinement for bend candidates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from extract_raw_bend_starts import (
    EARLY_PITCH_TOLERANCE_SEMITONES,
    EARLY_WINDOW_SECONDS,
    FRAME_SALIENCE_THRESHOLD,
    LATE_WINDOW_SECONDS,
    MAX_RISE_SEMITONES,
    MIDI_OFFSET,
    MIN_MIDI,
    MIN_RISE_SEMITONES,
    contour_summary,
    deduplicate,
    model_frame_times,
    require,
    sha256,
    validate_raw,
)

OCTAVE_SEMITONES = 12
LOWER_ONSET_SUPPORT_THRESHOLD = FRAME_SALIENCE_THRESHOLD
LOWER_ONSET_FRAME_RADIUS = 1

def refine(raw, candidates):
    validate_raw(raw)
    require(isinstance(candidates, list), "candidates must be a list")
    onset = raw["onset"]
    contour = raw["contour"]
    times = model_frame_times(onset.shape[0])
    refined = []
    changes = []
    for source in candidates:
        require(isinstance(source, dict), "candidate must be an object")
        midi = source.get("midi")
        frame = source.get("frame")
        require(isinstance(midi, int) and not isinstance(midi, bool), "invalid candidate midi")
        require(isinstance(frame, int) and not isinstance(frame, bool) and 0 <= frame < len(times), "invalid candidate frame")
        chosen = dict(source)
        lower = midi - OCTAVE_SEMITONES
        if lower >= MIN_MIDI:
            left = max(0, frame - LOWER_ONSET_FRAME_RADIUS)
            right = min(onset.shape[0], frame + LOWER_ONSET_FRAME_RADIUS + 1)
            values = onset[left:right, lower - MIDI_OFFSET]
            relative = int(np.argmax(values))
            lower_frame = left + relative
            lower_onset = float(values[relative])
            lower_time = float(times[lower_frame])
            early = contour_summary(contour, times, lower_time, lower, EARLY_WINDOW_SECONDS)
            late = contour_summary(contour, times, lower_time, lower, LATE_WINDOW_SECONDS)
            if early is not None and late is not None:
                rise = late["medianPitch"] - early["medianPitch"]
                supported = (
                    lower_onset >= LOWER_ONSET_SUPPORT_THRESHOLD
                    and abs(early["medianPitch"] - lower) <= EARLY_PITCH_TOLERANCE_SEMITONES
                    and MIN_RISE_SEMITONES <= rise <= MAX_RISE_SEMITONES
                    and max(early["maxSalience"], late["maxSalience"]) >= FRAME_SALIENCE_THRESHOLD
                )
                if supported:
                    chosen.update({
                        "frame": int(lower_frame), "time": lower_time, "midi": lower,
                        "onsetActivation": lower_onset,
                        "earlyPitch": early["medianPitch"], "earlyMedianSalience": early["medianSalience"],
                        "earlyMaxSalience": early["maxSalience"],
                        "latePitch": late["medianPitch"], "lateMedianSalience": late["medianSalience"],
                        "lateMaxSalience": late["maxSalience"], "riseSemitones": rise,
                        "octaveSupport": True, "octaveSupportSourceMidi": midi,
                    })
                    changes.append({
                        "sourceMidi": midi, "refinedMidi": lower,
                        "sourceFrame": frame, "refinedFrame": int(lower_frame),
                        "lowerOnsetActivation": lower_onset,
                    })
        refined.append(chosen)
    return deduplicate(refined), changes

def build_report(raw_path, candidate_path, *, expected_raw_sha256=None, expected_candidate_sha256=None):
    if expected_raw_sha256 is not None:
        require(sha256(raw_path) == expected_raw_sha256, "raw activation SHA256 mismatch")
    if expected_candidate_sha256 is not None:
        require(sha256(candidate_path) == expected_candidate_sha256, "candidate SHA256 mismatch")
    z = np.load(raw_path)
    raw = {k: z[k] for k in z.files}
    source = json.loads(Path(candidate_path).read_text())
    require(source.get("kind") == "basic-pitch-raw-attacked-bend-candidates", "unexpected candidate kind")
    require(source.get("customerDeliveryEligible") is False, "source cannot authorize delivery")
    require(source.get("policy", {}).get("referenceLabelsRead") is False, "source must be reference-blind")
    refined, changes = refine(raw, source.get("candidates"))
    return {
        "kind": "basic-pitch-octave-supported-bend-candidates",
        "version": 1,
        "rawActivationSha256": sha256(raw_path),
        "sourceCandidateSha256": sha256(candidate_path),
        "sourceCandidateCount": len(source.get("candidates", [])),
        "candidateCount": len(refined),
        "candidates": refined,
        "octaveSupportChangeCount": len(changes),
        "octaveSupportChanges": changes,
        "policy": {
            "referenceLabelsRead": False,
            "octaveSemitones": OCTAVE_SEMITONES,
            "lowerOnsetSupportThreshold": LOWER_ONSET_SUPPORT_THRESHOLD,
            "lowerOnsetFrameRadius": LOWER_ONSET_FRAME_RADIUS,
            "fundamentalContourMustSatisfySameBendSemantics": True,
        },
        "customerDeliveryEligible": False,
        "limitations": [
            "A stronger upper-octave bend candidate may be reassigned to a lower fundamental only when the lower octave has independent onset and contour support.",
            "This refinement does not assign rhythm-versus-lead role truth.",
            "No reviewed label, measure number, target pitch or score is read by the refinement.",
        ],
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", required=True)
    p.add_argument("--candidates", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--raw-sha256")
    p.add_argument("--candidate-sha256")
    a = p.parse_args()
    output = Path(a.output)
    require(not output.exists(), "refusing to overwrite output")
    report = build_report(a.raw, a.candidates, expected_raw_sha256=a.raw_sha256, expected_candidate_sha256=a.candidate_sha256)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"candidateCount": report["candidateCount"], "octaveSupportChangeCount": report["octaveSupportChangeCount"]}, sort_keys=True))

if __name__ == "__main__":
    main()
