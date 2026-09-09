#!/usr/bin/env python3

import argparse
import json
from collections import Counter
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from activation_valley_release_evidence import (
    evaluate_activation_spectral_valley,
    fixed_rule_manifest,
)
from basic_pitch_activation_evidence import decode_and_verify_activation_sidecar
from estimate_selected_pitch_releases import (
    CONTRACT as V2_CONTRACT,
    DROP_FROM_ONSET_DB,
    HOP_LENGTH,
    MAX_SEARCH_SECONDS,
    MIN_DURATION_SECONDS,
    MIN_FLOOR_MARGIN_DB,
    MIN_ONSET_ABOVE_FLOOR_DB,
    SUSTAINED_LOW_FRAMES,
    load_evidence,
    next_same_pitch_reattack_frame,
    sustained_release,
    unresolved_duration,
)

CONTRACT = "songsterr-fresh-spectral-activation-release-evidence-v3"
FALLBACK_METHOD = "selected-pitch-activation-valley-with-spectral-corroboration"
PRIMARY_METHOD = "selected-pitch-sustained-spectral-decay"
FALLBACK_ELIGIBLE_REASON = "NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="isolated guitar stem")
    parser.add_argument("--evidence", required=True, help="duration-free note evidence")
    parser.add_argument("--activation-evidence", required=True, help="same-inference activation sidecar")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--allow-model-upstream",
        action="store_true",
        help="Explicitly authorize fresh model-derived duration-free pitch/activation evidence.",
    )
    return parser.parse_args()


def increment(counter, key):
    counter[key] += 1


def next_same_pitch_seconds(onsets, index, midi):
    for later in onsets[index + 1:]:
        if later.get("classification") != "unambiguous":
            continue
        if later.get("selectedMidi") is None or int(later["selectedMidi"]) != midi:
            continue
        return float(later["sourceStart"])
    return None


def load_activation(path, evidence):
    with open(path, "r", encoding="utf-8") as handle:
        sidecar = json.load(handle)
    decoded = decode_and_verify_activation_sidecar(sidecar, evidence=evidence)
    provenance = sidecar.get("provenance", {})
    if provenance.get("modelInvoked") is not True:
        raise RuntimeError("V3_ACTIVATION_EVIDENCE_REQUIRES_MODEL_PROVENANCE")
    guards = sidecar.get("hardGuards", {})
    if guards.get("sameInferenceAsDecodedNotes") is not True:
        raise RuntimeError("V3_ACTIVATION_SAME_INFERENCE_GUARD_MISSING")
    for key in (
        "decodedModelNoteEndsIncluded",
        "decodedModelNoteEndsUsedAsDuration",
        "writesSourceEnd",
        "writesDurationSeconds",
        "activeDurationAuthority",
        "changesPitchIdentity",
    ):
        if guards.get(key) is not False:
            raise RuntimeError(f"V3_ACTIVATION_GUARD_CHANGED:{key}")
    return sidecar, decoded


def build_audio_features(audio_path, evidence):
    y, sr = sf.read(audio_path, always_2d=False)
    if y.ndim != 1:
        y = np.mean(y, axis=1)
    y = np.asarray(y, dtype=np.float32)
    if sr <= 0 or len(y) == 0:
        raise RuntimeError("RELEASE_EVIDENCE_AUDIO_EMPTY")

    diagnostics = evidence.get("diagnostics") or {}
    analysis_range = diagnostics.get("analysisMidiRange")
    if not isinstance(analysis_range, list) or len(analysis_range) != 2:
        raise RuntimeError("RELEASE_EVIDENCE_ANALYSIS_RANGE_MISSING")
    analysis_midi_min = int(analysis_range[0])
    analysis_midi_max = int(analysis_range[1])
    n_bins = analysis_midi_max - analysis_midi_min + 1
    if n_bins <= 0:
        raise RuntimeError("RELEASE_EVIDENCE_ANALYSIS_RANGE_INVALID")

    harmonic = librosa.effects.harmonic(y, margin=2.0)
    cqt = np.abs(librosa.cqt(
        harmonic,
        sr=sr,
        hop_length=HOP_LENGTH,
        fmin=librosa.midi_to_hz(analysis_midi_min),
        n_bins=n_bins,
        bins_per_octave=12,
    ))
    cqt_db = librosa.amplitude_to_db(cqt, ref=np.max, top_db=80.0)
    pitch_floors = np.percentile(cqt_db, 20, axis=1)
    return sr, analysis_midi_min, analysis_midi_max, cqt_db, pitch_floors


def run_primary_v2_spectral(
    evidence,
    *,
    sr,
    analysis_midi_min,
    cqt_db,
    pitch_floors,
):
    attempted = 0
    resolved = 0
    durations = []
    confidences = []
    reason_counts = Counter()
    same_pitch_reattack_censor_count = 0
    onsets = evidence.get("onsets", [])

    for index, onset in enumerate(onsets):
        if onset.get("classification") != "unambiguous" or onset.get("selectedMidi") is None:
            continue
        attempted += 1
        midi = int(onset["selectedMidi"])
        bin_index = midi - analysis_midi_min
        if bin_index < 0 or bin_index >= cqt_db.shape[0]:
            reason = "SELECTED_MIDI_OUTSIDE_ANALYSIS_RANGE"
            unresolved_duration(onset, reason)
            increment(reason_counts, reason)
            continue

        onset_frame = int(librosa.time_to_frames(
            float(onset["sourceStart"]), sr=sr, hop_length=HOP_LENGTH
        ))
        onset_frame = max(0, min(cqt_db.shape[1] - 1, onset_frame))
        onset_stop = min(cqt_db.shape[1], onset_frame + 5)
        onset_level_db = float(np.max(cqt_db[bin_index, onset_frame:onset_stop]))
        pitch_floor_db = float(pitch_floors[bin_index])
        if onset_level_db - pitch_floor_db < MIN_ONSET_ABOVE_FLOOR_DB:
            reason = "INSUFFICIENT_ONSET_TO_FLOOR_CONTRAST"
            unresolved_duration(onset, reason)
            increment(reason_counts, reason)
            continue

        reattack_frame = next_same_pitch_reattack_frame(onsets, index, midi, sr)
        max_search_frame = onset_frame + max(
            1, int(np.ceil(MAX_SEARCH_SECONDS * sr / HOP_LENGTH))
        )
        censored_by_reattack = (
            reattack_frame is not None and reattack_frame < max_search_frame
        )
        if censored_by_reattack:
            same_pitch_reattack_censor_count += 1

        release = sustained_release(
            cqt_db[bin_index],
            onset_frame,
            onset_level_db,
            pitch_floor_db,
            sr,
            censor_frame=reattack_frame if censored_by_reattack else None,
        )
        if release is None:
            reason = (
                FALLBACK_ELIGIBLE_REASON
                if censored_by_reattack
                else "NO_CLEAR_SUSTAINED_SPECTRAL_RELEASE"
            )
            unresolved_duration(
                onset,
                reason,
                censored_by_same_pitch_reattack=censored_by_reattack,
            )
            increment(reason_counts, reason)
            continue

        source_start = float(onset["sourceStart"])
        source_end = float(release["sourceEnd"])
        duration_seconds = source_end - source_start
        if duration_seconds < MIN_DURATION_SECONDS:
            reason = "RELEASE_TOO_CLOSE_TO_ONSET"
            unresolved_duration(
                onset,
                reason,
                censored_by_same_pitch_reattack=censored_by_reattack,
            )
            increment(reason_counts, reason)
            continue

        if censored_by_reattack:
            reattack_seconds = float(
                librosa.frames_to_time(reattack_frame, sr=sr, hop_length=HOP_LENGTH)
            )
            if source_end >= reattack_seconds:
                reason = "RELEASE_NOT_BEFORE_SAME_PITCH_REATTACK"
                unresolved_duration(
                    onset,
                    reason,
                    censored_by_same_pitch_reattack=True,
                )
                increment(reason_counts, reason)
                continue

        onset["sourceEnd"] = source_end
        onset["durationSeconds"] = duration_seconds
        onset["durationConfidence"] = release["durationConfidence"]
        onset.setdefault("provenance", {})["durationEvidence"] = {
            "source": V2_CONTRACT,
            "resolved": True,
            "method": PRIMARY_METHOD,
            "nextOnsetUsedAsDuration": False,
            "samePitchReattackCensored": censored_by_reattack,
            "onsetLevelDb": release["onsetLevelDb"],
            "releaseLevelDb": release["releaseLevelDb"],
            "pitchFloorDb": release["pitchFloorDb"],
            "observedDropDb": release["observedDropDb"],
            "thresholdDb": release["thresholdDb"],
        }
        resolved += 1
        durations.append(duration_seconds)
        confidences.append(release["durationConfidence"])

    return {
        "attempted": attempted,
        "resolved": resolved,
        "unresolved": attempted - resolved,
        "reasonCounts": dict(sorted(reason_counts.items())),
        "samePitchReattackCensorCount": same_pitch_reattack_censor_count,
        "meanResolvedDurationSeconds": float(np.mean(durations)) if durations else 0.0,
        "medianResolvedDurationSeconds": float(np.median(durations)) if durations else 0.0,
        "maxResolvedDurationSeconds": float(np.max(durations)) if durations else 0.0,
        "meanDurationConfidence": float(np.mean(confidences)) if confidences else 0.0,
    }


def apply_activation_fallback(
    evidence,
    *,
    decoded,
    sr,
    analysis_midi_min,
    analysis_midi_max,
    cqt_db,
):
    activations = np.asarray(decoded["activations"], dtype=np.float32)
    frame_times = np.asarray(decoded["frameTimesSeconds"], dtype=np.float64)
    activation_min_midi = int(decoded["minimumMidi"])
    activation_max_midi = int(decoded["maximumMidi"])
    bundle = decoded["inferenceBundleIdentity"]
    note_identity = decoded["noteInferenceIdentity"]

    attempted = 0
    resolved = 0
    rejection_counts = Counter()
    resolved_midis = Counter()
    spans = []
    onsets = evidence.get("onsets", [])

    for index, onset in enumerate(onsets):
        duration_evidence = onset.get("provenance", {}).get("durationEvidence", {})
        if duration_evidence.get("resolved") is True:
            continue
        if duration_evidence.get("reason") != FALLBACK_ELIGIBLE_REASON:
            continue

        attempted += 1
        midi = int(onset["selectedMidi"])
        reattack = next_same_pitch_seconds(onsets, index, midi)
        if reattack is None:
            reason = "MISSING_SAME_PITCH_REATTACK"
            increment(rejection_counts, reason)
            duration_evidence["activationFallback"] = {
                "source": CONTRACT,
                "attempted": True,
                "resolved": False,
                "reason": reason,
            }
            continue

        if (
            midi < activation_min_midi
            or midi > activation_max_midi
            or midi < analysis_midi_min
            or midi > analysis_midi_max
        ):
            reason = "MIDI_OUTSIDE_ACTIVATION_OR_SPECTRAL_RANGE"
            increment(rejection_counts, reason)
            duration_evidence["activationFallback"] = {
                "source": CONTRACT,
                "attempted": True,
                "resolved": False,
                "reason": reason,
            }
            continue

        candidate, reason = evaluate_activation_spectral_valley(
            trace=activations[:, midi - activation_min_midi],
            frame_times=frame_times,
            source_start=float(onset["sourceStart"]),
            reattack=reattack,
            cqt_db=cqt_db,
            bin_index=midi - analysis_midi_min,
            sr=sr,
            hop_length=HOP_LENGTH,
        )
        if candidate is None:
            increment(rejection_counts, reason)
            duration_evidence["activationFallback"] = {
                "source": CONTRACT,
                "attempted": True,
                "resolved": False,
                "reason": reason,
                "nextOnsetUsedAsDuration": False,
                "samePitchReattackUsedAsDuration": False,
                "decodedModelNoteEndUsedAsDuration": False,
            }
            continue

        source_start = float(onset["sourceStart"])
        source_end = float(candidate["observedValleySeconds"])
        duration_seconds = source_end - source_start
        if source_end >= reattack or duration_seconds < MIN_DURATION_SECONDS:
            raise RuntimeError(
                f"V3_ACTIVATION_RELEASE_WINDOW_GUARD_FAILED:{onset.get('onsetId')}"
            )

        onset["sourceEnd"] = source_end
        onset["durationSeconds"] = duration_seconds
        onset["durationConfidence"] = None
        onset.setdefault("provenance", {})["durationEvidence"] = {
            "source": CONTRACT,
            "resolved": True,
            "method": FALLBACK_METHOD,
            "primarySpectralContract": V2_CONTRACT,
            "primarySpectralMethod": PRIMARY_METHOD,
            "primarySpectralReason": FALLBACK_ELIGIBLE_REASON,
            "fixedActivationRule": fixed_rule_manifest(),
            "activationEvidenceContract": decoded.get("inferenceBundleIdentity", {}).get("contract"),
            "activationNoteIdentitySha256": note_identity["sha256"],
            "activationInferenceBundleSha256": bundle["sha256"],
            "samePitchReattackCensored": True,
            "samePitchReattackSeconds": reattack,
            "samePitchReattackUsedAsDuration": False,
            "nextOnsetUsedAsDuration": False,
            "decodedModelNoteEndUsedAsDuration": False,
            "observedValleySeconds": source_end,
            "observedSpanFromOnsetSeconds": duration_seconds,
            "onsetActivationPeak": candidate["onsetActivationPeak"],
            "valleyActivationMean": candidate["valleyActivationMean"],
            "activationDrop": candidate["activationDrop"],
            "onsetSpectralDb": candidate["onsetSpectralDb"],
            "valleySpectralDb": candidate["valleySpectralDb"],
            "spectralDropDb": candidate["spectralDropDb"],
        }
        resolved += 1
        spans.append(duration_seconds)
        increment(resolved_midis, midi)

    return {
        "attempted": attempted,
        "resolved": resolved,
        "unresolved": attempted - resolved,
        "rejectionReasonCounts": dict(sorted(rejection_counts.items())),
        "resolvedMidiHistogram": {str(k): v for k, v in sorted(resolved_midis.items())},
        "meanResolvedSpanSeconds": float(np.mean(spans)) if spans else 0.0,
        "medianResolvedSpanSeconds": float(np.median(spans)) if spans else 0.0,
        "maxResolvedSpanSeconds": float(np.max(spans)) if spans else 0.0,
    }


def final_unresolved_reasons(evidence):
    reasons = Counter()
    for onset in evidence.get("onsets", []):
        if onset.get("classification") != "unambiguous" or onset.get("selectedMidi") is None:
            continue
        if onset.get("durationSeconds") is not None:
            continue
        duration_evidence = onset.get("provenance", {}).get("durationEvidence", {})
        increment(reasons, duration_evidence.get("reason", "UNDECLARED"))
    return dict(sorted(reasons.items()))


def main():
    args = parse_args()
    evidence = load_evidence(
        args.evidence,
        allow_model_upstream=args.allow_model_upstream,
    )
    if evidence.get("provenance", {}).get("modelInvoked") is True and not args.allow_model_upstream:
        raise RuntimeError("V3_MODEL_UPSTREAM_REQUIRES_EXPLICIT_AUTHORIZATION")

    sidecar, decoded = load_activation(args.activation_evidence, evidence)
    sr, analysis_midi_min, analysis_midi_max, cqt_db, pitch_floors = build_audio_features(
        args.input, evidence
    )

    v2_baseline = run_primary_v2_spectral(
        evidence,
        sr=sr,
        analysis_midi_min=analysis_midi_min,
        cqt_db=cqt_db,
        pitch_floors=pitch_floors,
    )
    fallback = apply_activation_fallback(
        evidence,
        decoded=decoded,
        sr=sr,
        analysis_midi_min=analysis_midi_min,
        analysis_midi_max=analysis_midi_max,
        cqt_db=cqt_db,
    )

    attempted = v2_baseline["attempted"]
    final_resolved = sum(
        1
        for onset in evidence.get("onsets", [])
        if onset.get("classification") == "unambiguous"
        and onset.get("selectedMidi") is not None
        and onset.get("durationSeconds") is not None
    )
    if final_resolved != v2_baseline["resolved"] + fallback["resolved"]:
        raise RuntimeError("V3_RESOLVED_COUNT_ACCOUNTING_MISMATCH")

    unresolved = attempted - final_resolved
    if attempted > 0 and final_resolved == attempted:
        duration_resolution = "complete"
    elif final_resolved > 0:
        duration_resolution = "partial"
    else:
        duration_resolution = "none"

    capabilities = evidence.setdefault("capabilities", {})
    capabilities["durationResolution"] = duration_resolution
    capabilities["durationMethod"] = (
        "selected-pitch-sustained-spectral-decay"
        "+activation-valley-spectral-fallback"
    )

    upstream = evidence.get("provenance", {})
    release_diagnostics = {
        "contract": CONTRACT,
        "version": 3,
        "soleDurationAuthority": True,
        "requiresDurationFreeInput": True,
        "explicitModelUpstreamAuthorizationRequired": True,
        "modelUpstreamAllowedThisRun": bool(args.allow_model_upstream),
        "upstreamModelInvoked": upstream.get("modelInvoked") is True,
        "upstreamGpuInvoked": upstream.get("gpuInvoked") is True,
        "primarySpectralContract": V2_CONTRACT,
        "primarySpectralRunsFirst": True,
        "primarySpectralResolvedCount": v2_baseline["resolved"],
        "primarySpectralUnresolvedCount": v2_baseline["unresolved"],
        "primarySpectralUnresolvedReasonCounts": v2_baseline["reasonCounts"],
        "samePitchReattackCensorCount": v2_baseline["samePitchReattackCensorCount"],
        "activationFallbackEligibleReason": FALLBACK_ELIGIBLE_REASON,
        "activationFallbackAttemptedCount": fallback["attempted"],
        "activationFallbackResolvedCount": fallback["resolved"],
        "activationFallbackUnresolvedCount": fallback["unresolved"],
        "activationFallbackRejectionReasonCounts": fallback["rejectionReasonCounts"],
        "activationFallbackResolvedMidiHistogram": fallback["resolvedMidiHistogram"],
        "activationFallbackMeanResolvedSpanSeconds": fallback["meanResolvedSpanSeconds"],
        "activationFallbackMedianResolvedSpanSeconds": fallback["medianResolvedSpanSeconds"],
        "activationFallbackMaxResolvedSpanSeconds": fallback["maxResolvedSpanSeconds"],
        "activationFixedRule": fixed_rule_manifest(),
        "activationEvidenceContract": sidecar.get("contract"),
        "activationNoteIdentitySha256": decoded["noteInferenceIdentity"]["sha256"],
        "activationInferenceBundleSha256": decoded["inferenceBundleIdentity"]["sha256"],
        "activationEvidenceSameInferenceVerified": True,
        "activationStageInvokedModel": False,
        "attemptedPromotedOnsetCount": attempted,
        "resolvedPromotedOnsetCount": final_resolved,
        "unresolvedPromotedOnsetCount": unresolved,
        "resolutionRate": final_resolved / attempted if attempted else 0.0,
        "unresolvedReasonCounts": final_unresolved_reasons(evidence),
        "minimumDurationSeconds": MIN_DURATION_SECONDS,
        "maximumSearchSeconds": MAX_SEARCH_SECONDS,
        "sustainedLowFrames": SUSTAINED_LOW_FRAMES,
        "minimumOnsetAboveFloorDb": MIN_ONSET_ABOVE_FLOOR_DB,
        "dropFromOnsetDb": DROP_FROM_ONSET_DB,
        "minimumFloorMarginDb": MIN_FLOOR_MARGIN_DB,
        "samePitchReattackIsCensorOnly": True,
        "samePitchReattackUsedAsDuration": False,
        "nextOnsetUsedAsDuration": False,
        "decodedModelNoteEndUsedAsDuration": False,
        "activationDurationConfidence": None,
        "activationDurationConfidenceInvented": False,
    }
    evidence.setdefault("diagnostics", {})["releaseEvidence"] = release_diagnostics
    evidence.setdefault("provenance", {})["durationEvidenceSource"] = CONTRACT
    evidence["provenance"]["durationEvidenceReferenceBlind"] = True
    evidence["provenance"]["durationEvidenceModelInvoked"] = False
    evidence["provenance"]["durationEvidenceGpuInvoked"] = False
    evidence["provenance"]["durationEvidenceRequiresDurationFreeInput"] = True
    evidence["provenance"]["durationEvidenceAcceptedAuthorizedModelUpstream"] = bool(
        args.allow_model_upstream and upstream.get("modelInvoked") is True
    )
    evidence["provenance"]["activationEvidenceConsumed"] = True
    evidence["provenance"]["activationEvidenceIdentityVerified"] = True
    evidence["provenance"]["decodedModelNoteEndUsedAsDuration"] = False
    evidence["provenance"]["nextOnsetUsedAsDuration"] = False
    evidence["provenance"]["samePitchReattackUsedAsDuration"] = False

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(evidence, handle, indent=2)
        handle.write("\n")

    print(json.dumps({
        "contract": CONTRACT,
        "capabilities": capabilities,
        "releaseEvidence": release_diagnostics,
    }))


if __name__ == "__main__":
    main()
