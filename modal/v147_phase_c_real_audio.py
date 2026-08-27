"""Single-candidate V147 Phase-C real-audio artifact construction.

This runner implements only the already-frozen Phase-C protocol. Preflight mode
verifies the accepted event source and source-code identities without touching
real audio. Execute mode then verifies exact raw bytes before deterministic
CPU decode/HPSS/CQT construction. It never reads calibration/reference/gold.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
if str(HOLDOUT_DIR) not in sys.path:
    sys.path.insert(0, str(HOLDOUT_DIR))

from canonical import canonical_events, sha256_json  # noqa: E402
from modal.v147_phase_c_artifact_support import (  # noqa: E402
    EXPECTED_ACCEPTED_EVENT_COUNT,
    EXPECTED_ACCEPTED_EVENT_SHA256,
    EXPECTED_MEASURE_COUNT,
    EXPECTED_RAW_AUDIO_SHA256,
    OPEN_MIDI_BY_STRING_INDEX,
    apply_fixed_time_pitch_decisions,
    decide_event_from_prepared_cqt,
    event_onset_seconds,
    materialize_accepted_family,
    timing_and_metadata_violations,
    verify_raw_audio_identity,
)

EXPECTED_RAW_AUDIO_BYTES = 3_478_611
SAMPLE_RATE = 22_050
HOP_LENGTH = 128
BINS_PER_OCTAVE = 48
FMIN_MIDI = 40
N_BINS = 243
HPSS_MARGIN = (1.0, 6.0)
EXPECTED_BLOBS = {
    "modal/v145_rhythm_decoder.py": "2fd979aebb4685e86c7f24a0162f69de306c06e9",
    "modal/v147_pitch_hypothesis.py": "49bce8b968406bb0d61ab61394954ef8a8303eb7",
    "modal/v147_phase_c_artifact_support.py": "f4278ffaacaca3f66baf7a3112e2af0f3bc387cf",
    "validation/rhythm_holdout/canonical.py": "088d44827fb23e20d9aeeb4944a672989af5846c",
    "validation/rhythm_holdout/verify_pdf_event_fidelity.py": "5e1564216873046237fb545078a04a6b18f72b27",
    "lib/v143RenderContract.js": "ccbb93c48982798cc474309fd981f6ca02d5c8d4",
}


def _blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", path], cwd=ROOT, text=True).strip()


def _verify_source_blobs() -> dict[str, str]:
    actual = {path: _blob(path) for path in EXPECTED_BLOBS}
    mismatches = {
        path: {"expected": EXPECTED_BLOBS[path], "actual": actual_sha}
        for path, actual_sha in actual.items()
        if actual_sha != EXPECTED_BLOBS[path]
    }
    if mismatches:
        raise ValueError(f"frozen source identity mismatch: {mismatches}")
    return actual


def _load_accepted(v5_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = json.loads(v5_path.read_text(encoding="utf-8"))
    events = materialize_accepted_family(payload)
    canonical = canonical_events(events)
    digest = sha256_json(canonical)
    if len(canonical) != EXPECTED_ACCEPTED_EVENT_COUNT or digest != EXPECTED_ACCEPTED_EVENT_SHA256:
        raise ValueError("accepted source identity mismatch after materialization")
    measures = sorted({int(event["measure"]) for event in canonical})
    if len(measures) != EXPECTED_MEASURE_COUNT or measures != list(range(1, EXPECTED_MEASURE_COUNT + 1)):
        raise ValueError("accepted source measure set mismatch")
    return events, {
        "eventCount": len(canonical),
        "eventSha256": digest,
        "generatedMeasureCount": len(measures),
    }


def _next_onset_map(events: Sequence[Mapping[str, Any]]) -> dict[tuple[int, int], float | None]:
    keyed = sorted({(int(event["measure"]), int(event["step"])) for event in events})
    times = {
        key: event_onset_seconds({"measure": key[0], "step": key[1]})
        for key in keyed
    }
    output: dict[tuple[int, int], float | None] = {}
    for index, key in enumerate(keyed):
        output[key] = times[keyed[index + 1]] if index + 1 < len(keyed) else None
    return output


def _decision_category(reason: str) -> str:
    if reason == "insufficient-frames":
        return "insufficient"
    if reason == "tied-best-score":
        return "ambiguous"
    if reason in {
        "alternate-fundamental-too-weak",
        "alternate-score-margin-too-small",
        "alternate-fundamental-margin-too-small",
    }:
        return "weak"
    if reason in {
        "malformed-evidence",
        "missing-or-malformed-candidate",
        "non-finite-evidence",
        "cqt-evidence-unavailable",
        "invalid-original-midi",
        "alternate-out-of-range",
    }:
        return "malformed"
    return "normal"


def _construct_from_prepared_cqt(
    accepted: Sequence[Mapping[str, Any]],
    cqt_magnitude: Any,
    midi_bins: Any,
    frame_times: Sequence[float],
) -> dict[str, Any]:
    next_by_onset = _next_onset_map(accepted)
    selected: dict[int, int] = {}
    decisions: list[dict[str, Any]] = []
    reason_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()

    for row in accepted:
        onset = (int(row["measure"]), int(row["step"]))
        decision = decide_event_from_prepared_cqt(
            row,
            cqt_magnitude,
            midi_bins,
            frame_times,
            next_onset_seconds=next_by_onset[onset],
        )
        event_index = int(row["eventIndex"])
        selected[event_index] = int(decision["selectedMidi"])
        reason = str(decision.get("reason") or "")
        reason_counts[reason] += 1
        category_counts[_decision_category(reason)] += 1
        decisions.append(
            {
                "eventIndex": event_index,
                "measure": int(row["measure"]),
                "step": int(row["step"]),
                "originalMidi": int(row["midi"]),
                "selectedMidi": int(decision["selectedMidi"]),
                "changed": bool(decision.get("changed")),
                "semitoneDelta": int(decision.get("semitoneDelta") or 0),
                "reason": reason,
                "frameIndices": [int(value) for value in decision.get("frameIndices", [])],
                "candidates": decision.get("candidates", []),
            }
        )

    source_snapshot = copy.deepcopy(list(accepted))
    applied = apply_fixed_time_pitch_decisions(accepted, selected)
    candidate = applied["events"]
    input_mutations = [] if list(accepted) == source_snapshot else [{"reason": "accepted-input-mutated"}]
    canonical_candidate = canonical_events(candidate)
    candidate_sha = sha256_json(canonical_candidate)

    timing_violations = timing_and_metadata_violations(accepted, candidate)
    position_violations: list[dict[str, Any]] = []
    pitch_delta_violations: list[dict[str, Any]] = []
    order_violations: list[dict[str, Any]] = []
    changed_indices: list[int] = []
    down_one = 0
    up_one = 0

    for index, (before, after) in enumerate(zip(accepted, candidate)):
        if int(before["eventIndex"]) != int(after["eventIndex"]):
            order_violations.append(
                {
                    "index": index,
                    "before": before["eventIndex"],
                    "after": after["eventIndex"],
                }
            )
        midi = int(after["midi"])
        string_index = int(after["stringIndex"])
        fret = int(after["fret"])
        if (
            string_index not in OPEN_MIDI_BY_STRING_INDEX
            or not (0 <= fret <= 24)
            or OPEN_MIDI_BY_STRING_INDEX.get(string_index, -999) + fret != midi
        ):
            position_violations.append(
                {
                    "eventIndex": int(after["eventIndex"]),
                    "midi": midi,
                    "stringIndex": string_index,
                    "fret": fret,
                }
            )
        delta = midi - int(before["midi"])
        if delta:
            changed_indices.append(int(after["eventIndex"]))
            if delta not in (-1, 1):
                pitch_delta_violations.append(
                    {"eventIndex": int(after["eventIndex"]), "delta": delta}
                )
            elif delta == -1:
                down_one += 1
            else:
                up_one += 1

    measure_set = sorted({int(event["measure"]) for event in canonical_candidate})
    if len(candidate) != len(accepted):
        raise ValueError("candidate event cardinality changed")

    return {
        "candidate": candidate,
        "canonicalCandidate": canonical_candidate,
        "candidateSha256": candidate_sha,
        "decisions": decisions,
        "metrics": {
            "eventsConsidered": len(accepted),
            "usableEvidenceEvents": len(accepted) - category_counts["insufficient"],
            "insufficientFrameEvents": category_counts["insufficient"],
            "pitchChangesTotal": len(changed_indices),
            "pitchChangesDownOne": down_one,
            "pitchChangesUpOne": up_one,
            "ambiguousFailClosedCount": category_counts["ambiguous"],
            "weakFailClosedCount": category_counts["weak"],
            "malformedFailClosedCount": category_counts["malformed"],
            "originalBestCount": reason_counts["original-best"],
            "onsetGroupFingeringFailClosedCount": int(applied["onsetGroupFailClosedCount"]),
            "positionIdentityViolations": len(position_violations),
            "timingMetadataInvariantViolations": len(timing_violations),
            "inputMutationViolations": len(input_mutations),
            "orderViolations": len(order_violations),
            "pitchDeltaViolations": len(pitch_delta_violations),
            "generatedMeasureCount": len(measure_set),
        },
        "reasonCounts": dict(sorted(reason_counts.items())),
        "violations": {
            "position": position_violations,
            "timingMetadata": timing_violations,
            "inputMutation": input_mutations,
            "order": order_violations,
            "pitchDelta": pitch_delta_violations,
        },
        "changedEventIndices": changed_indices,
        "measureSet": measure_set,
    }


def _construction_proof_payload(
    accepted_meta: Mapping[str, Any],
    construction: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": 14731,
        "phase": "V147-Phase-C-real-audio-construction",
        "acceptedSource": dict(accepted_meta),
        "candidateEventCount": len(construction["canonicalCandidate"]),
        "candidateEventSha256": construction["candidateSha256"],
        "metrics": construction["metrics"],
        "reasonCounts": construction["reasonCounts"],
        "changedEventIndices": construction["changedEventIndices"],
        "measureSet": construction["measureSet"],
        "referenceRead": False,
        "goldRead": False,
        "calibrationScoreRun": False,
        "candidateSearchRun": False,
        "alternateCandidateConstructed": False,
        "modalGpuUsed": False,
        "productionIntegrated": False,
    }


def _sha_json(value: Any) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _decode_exact_audio(audio_path: Path) -> tuple[Any, bytes, dict[str, Any]]:
    import imageio_ffmpeg
    import numpy as np

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    version = subprocess.check_output([ffmpeg, "-version"], text=True).splitlines()[0].strip()
    command = [
        ffmpeg,
        "-v",
        "error",
        "-i",
        str(audio_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        str(SAMPLE_RATE),
        "-f",
        "f32le",
        "-acodec",
        "pcm_f32le",
        "pipe:1",
    ]
    pcm_bytes = subprocess.check_output(command)
    if not pcm_bytes or len(pcm_bytes) % 4:
        raise ValueError("decoder produced invalid float32 PCM byte stream")
    samples = np.frombuffer(pcm_bytes, dtype="<f4").copy()
    if samples.ndim != 1 or samples.size == 0 or not np.all(np.isfinite(samples)):
        raise ValueError("decoded PCM is empty or non-finite")
    return samples, pcm_bytes, {
        "decoder": "imageio-ffmpeg bundled ffmpeg",
        "imageioFfmpegVersion": imageio_ffmpeg.__version__,
        "ffmpegVersion": version,
        "sampleRate": SAMPLE_RATE,
        "channels": 1,
        "sampleFormat": "pcm_f32le",
        "sampleCount": int(samples.size),
        "durationSeconds": float(samples.size) / SAMPLE_RATE,
        "normalizedPcmSha256": hashlib.sha256(pcm_bytes).hexdigest(),
        "normalizedPcmBytes": len(pcm_bytes),
    }


def _prepare_cqt(samples: Any) -> tuple[Any, Any, Any, dict[str, Any]]:
    import librosa
    import numpy as np

    harmonic, _ = librosa.effects.hpss(samples, margin=HPSS_MARGIN)
    fmin = float(librosa.midi_to_hz(FMIN_MIDI))
    cqt = np.abs(
        librosa.cqt(
            harmonic,
            sr=SAMPLE_RATE,
            hop_length=HOP_LENGTH,
            fmin=fmin,
            n_bins=N_BINS,
            bins_per_octave=BINS_PER_OCTAVE,
        )
    )
    if cqt.shape[0] != N_BINS or cqt.shape[1] == 0 or not np.all(np.isfinite(cqt)):
        raise ValueError("prepared CQT has invalid shape or non-finite values")
    midi_bins = FMIN_MIDI + np.arange(N_BINS, dtype=float) * (12.0 / BINS_PER_OCTAVE)
    frame_times = librosa.frames_to_time(
        np.arange(cqt.shape[1]),
        sr=SAMPLE_RATE,
        hop_length=HOP_LENGTH,
    )
    return cqt, midi_bins, frame_times, {
        "hpssMargin": list(HPSS_MARGIN),
        "cqtShape": [int(cqt.shape[0]), int(cqt.shape[1])],
        "hopLength": HOP_LENGTH,
        "binsPerOctave": BINS_PER_OCTAVE,
        "fminMidi": FMIN_MIDI,
        "fminHz": fmin,
        "nBins": N_BINS,
        "midiBinMin": float(midi_bins[0]),
        "midiBinMax": float(midi_bins[-1]),
    }


def _write_pdf_fidelity(
    candidate: Sequence[Mapping[str, Any]],
    candidate_sha: str,
    output_dir: Path,
) -> dict[str, Any]:
    freeze_dir = output_dir / "freeze"
    freeze_dir.mkdir(parents=True, exist_ok=True)
    (freeze_dir / "rhythm-frozen-analysis.json").write_text(
        json.dumps({"renderEvents": candidate}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
        "v143RuntimeSafetyVerified": True,
        "referenceOpenedDuringFreeze": False,
        "eventSha256": candidate_sha,
    }
    (freeze_dir / "rhythm-freeze-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    candidate_input = output_dir / "candidate-input.json"
    candidate_input.write_text(
        json.dumps({"events": candidate}, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    pdf_evidence = output_dir / "pdf-render-evidence.json"
    js = """
import fs from 'node:fs';
import { projectV143RenderEvents } from './lib/v143RenderContract.js';
const input = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
const renderEvents = projectV143RenderEvents(input.events || []);
const out = {runtimeSafetyVerified:true,runtimeLabelsRequired:false,referenceOpened:false,renderEvents};
fs.writeFileSync(process.argv[2], JSON.stringify(out));
"""
    subprocess.check_call(
        [
            "node",
            "--experimental-default-type=module",
            "--input-type=module",
            "-e",
            js,
            str(candidate_input),
            str(pdf_evidence),
        ],
        cwd=ROOT,
    )
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / "validation/rhythm_holdout/verify_pdf_event_fidelity.py"),
            str(freeze_dir),
            str(pdf_evidence),
        ],
        cwd=ROOT,
    )
    return json.loads(
        (freeze_dir / "rhythm-pdf-event-fidelity.json").read_text(encoding="utf-8")
    )


def _runtime_versions() -> dict[str, Any]:
    import imageio_ffmpeg
    import librosa
    import numpy
    import scipy
    import soundfile

    return {
        "python": platform.python_version(),
        "numpy": numpy.__version__,
        "scipy": scipy.__version__,
        "librosa": librosa.__version__,
        "soundfile": soundfile.__version__,
        "imageioFfmpeg": imageio_ffmpeg.__version__,
        "node": subprocess.check_output(["node", "--version"], text=True).strip(),
        "platform": platform.platform(),
    }


def preflight(v5_path: Path) -> dict[str, Any]:
    blobs = _verify_source_blobs()
    _, accepted_meta = _load_accepted(v5_path)
    return {
        "schema": 14730,
        "gate": "GO",
        "phase": "V147-Phase-C-pre-real-audio-execution",
        "acceptedSource": accepted_meta,
        "sourceBlobs": blobs,
        "audioRead": False,
        "referenceRead": False,
        "goldRead": False,
    }


def execute(v5_path: Path, audio_path: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    blobs = _verify_source_blobs()
    accepted, accepted_meta = _load_accepted(v5_path)  # MUST precede audio byte read.

    raw = audio_path.read_bytes()
    if len(raw) != EXPECTED_RAW_AUDIO_BYTES:
        raise ValueError(
            f"raw audio byte count mismatch: {len(raw)} != {EXPECTED_RAW_AUDIO_BYTES}"
        )
    raw_sha = verify_raw_audio_identity(raw)
    if raw_sha != EXPECTED_RAW_AUDIO_SHA256:
        raise ValueError("raw audio identity mismatch")

    samples, _, decoder_info = _decode_exact_audio(audio_path)
    cqt, midi_bins, frame_times, frontend_info = _prepare_cqt(samples)

    first = _construct_from_prepared_cqt(accepted, cqt, midi_bins, frame_times)
    first_payload = _construction_proof_payload(accepted_meta, first)
    first_proof_sha = _sha_json(first_payload)

    # Determinism replay uses the identical prepared evidence and frozen rules.
    second = _construct_from_prepared_cqt(accepted, cqt, midi_bins, frame_times)
    second_payload = _construction_proof_payload(accepted_meta, second)
    second_proof_sha = _sha_json(second_payload)
    deterministic = (
        first["candidateSha256"] == second["candidateSha256"]
        and first_proof_sha == second_proof_sha
    )

    candidate = first["canonicalCandidate"]
    pdf_report = _write_pdf_fidelity(
        candidate,
        first["candidateSha256"],
        output_dir,
    )
    metrics = dict(first["metrics"])
    metrics["pdfEventFidelity"] = float(pdf_report.get("pdfEventFidelity", 0.0))

    invariant_go = (
        len(candidate) == EXPECTED_ACCEPTED_EVENT_COUNT
        and metrics["generatedMeasureCount"] == EXPECTED_MEASURE_COUNT
        and metrics["positionIdentityViolations"] == 0
        and metrics["timingMetadataInvariantViolations"] == 0
        and metrics["inputMutationViolations"] == 0
        and metrics["orderViolations"] == 0
        and metrics["pitchDeltaViolations"] == 0
        and metrics["pdfEventFidelity"] == 1.0
        and deterministic
    )

    report = {
        "schema": 14732,
        "phase": "V147-Phase-C-real-audio-artifact-first",
        "gate": "GO" if invariant_go else "STOP",
        "acceptedManifest": {
            "path": "debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json",
            "blob": "acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68",
        },
        "acceptedSource": accepted_meta,
        "rawAudio": {"sha256": raw_sha, "bytes": len(raw)},
        "decoder": decoder_info,
        "frontEnd": frontend_info,
        "versions": _runtime_versions(),
        "sourceBlobs": blobs,
        "candidate": {
            "eventCount": len(candidate),
            "eventSha256": first["candidateSha256"],
            "generatedMeasureCount": metrics["generatedMeasureCount"],
        },
        "metrics": metrics,
        "reasonCounts": first["reasonCounts"],
        "changedEventIndices": first["changedEventIndices"],
        "violations": first["violations"],
        "constructionProofPayloadSha256": first_proof_sha,
        "determinismReplayProofPayloadSha256": second_proof_sha,
        "deterministic": deterministic,
        "pdfFidelity": pdf_report,
        "exactlyOneCandidateArtifactPersisted": True,
        "referenceRead": False,
        "goldRead": False,
        "calibrationScoreRun": False,
        "candidateSearchRun": False,
        "alternateCandidateConstructed": False,
        "modalGpuUsed": False,
        "productionIntegrated": False,
    }

    (output_dir / "candidate.json").write_text(
        json.dumps(
            {"schema": 14733, "instrument": "rhythm", "renderEvents": candidate},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "decisions.json").write_text(
        json.dumps(first["decisions"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "construction-proof.json").write_text(
        json.dumps(first_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "phase-c-evidence.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if not invariant_go:
        raise SystemExit("V147 Phase C invariant gate STOP")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("preflight", "execute"), required=True)
    parser.add_argument(
        "--v5",
        type=Path,
        default=ROOT / "debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json",
    )
    parser.add_argument("--audio", type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "debug/v147-phase-c-real-audio",
    )
    args = parser.parse_args()
    if args.mode == "preflight":
        result = preflight(args.v5.resolve())
        print(
            "V147_PHASE_C_PREFLIGHT_JSON="
            + json.dumps(result, sort_keys=True, separators=(",", ":"))
        )
        return 0
    if args.audio is None:
        parser.error("--audio is required in execute mode")
    result = execute(
        args.v5.resolve(),
        args.audio.resolve(),
        args.output_dir.resolve(),
    )
    print(
        "V147_PHASE_C_REAL_AUDIO_JSON="
        + json.dumps(result, sort_keys=True, separators=(",", ":"))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
