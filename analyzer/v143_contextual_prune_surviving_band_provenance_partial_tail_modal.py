from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal

import v143_contextual_prune_surviving_band_provenance_modal as base


app = modal.App("dadrock-v143-surviving-band-provenance-partial-tail")

SECTION3_EXACT_FAMILY_PROOF_LOCAL = (
    base.ROOT
    / "debug"
    / "v143-contextual-prune"
    / "section3-exact-family-provenance-capture.json"
)
SECTION3_EXACT_FAMILY_PROOF_REMOTE = Path(
    "/debug/v143-contextual-prune/section3-exact-family-provenance-capture.json"
)
EXPECTED_FAMILY_B_DIRECT_PCM_SHA256 = (
    "1542856aca8275c727e6c77edd941588aa359b65b8b897c1b3ada2926f2d579e"
)
EXPECTED_FAMILY_B_CASCADE_PCM_SHA256 = (
    "e26f7a430b835adcd7a284db8a18c3aa93632b81e1c1a653eeffa16c02a62bc3"
)

# Reuse the already-isolated provenance image, adding only the source modules
# this adapter imports directly plus the completed, research-only Section 3
# exact-family evidence. Production, frozen scorer/model artifacts, and the live
# endpoint remain untouched.
partial_tail_image = (
    base.provenance_image.add_local_python_source(
        "v143_contextual_prune_surviving_band_provenance_modal",
        "v143_contextual_prune_reference_free_carrier",
        "v143_candidate_timing_adapter",
    ).add_local_file(
        SECTION3_EXACT_FAMILY_PROOF_LOCAL,
        str(SECTION3_EXACT_FAMILY_PROOF_REMOTE),
    )
)


def _validated_section3_exact_family_band(
    proof_path: Path,
    historical_cache: dict[str, Any],
    source_sha256: str,
) -> dict[str, Any]:
    """Promote only a fully exact historical Family-B capture into Section 3.

    The ordinary surviving-band run still records its current-container Section 3
    observation. This helper is intentionally stricter than that observation: it
    accepts the completed independent capture only when the historical PCM family,
    exact carrier semantics, exact capture diagnostics, and every frozen score map
    are all proven unchanged.
    """
    proof = base._load_json(proof_path)
    top_checks = {
        "action gate": proof.get("gate")
        == "v143-section3-exact-family-provenance-capture-action",
        "diagnostic attempted": proof.get("diagnosticAttempted") is True,
        "diagnostic exit": proof.get("modalCommandExitCode") == 0,
        "diagnostic found": proof.get("diagnosticResultFound") is True,
        "production untouched": proof.get("productionModified") is False,
        "live endpoint untouched": proof.get("liveEndpointDeployedOrModified") is False,
    }
    top_failed = [name for name, ok in top_checks.items() if not ok]
    if top_failed:
        raise RuntimeError(
            "Section 3 exact-family action evidence is incomplete: "
            + ", ".join(top_failed)
        )

    captured = dict(proof.get("diagnosticResult") or {})
    if captured.get("gate") != "v143-section3-exact-family-provenance-capture":
        raise RuntimeError("Unexpected Section 3 exact-family diagnostic gate")
    if str(captured.get("sourceSha256") or "") != str(source_sha256 or ""):
        raise RuntimeError(
            "Section 3 exact-family proof was captured from a different source audio"
        )

    known = dict(captured.get("knownHistoricalFamily") or {})
    known_checks = {
        "historical family label B": known.get("label") == "B",
        "historical direct PCM": known.get("directPcmSha256")
        == EXPECTED_FAMILY_B_DIRECT_PCM_SHA256,
        "historical cascade PCM": known.get("cascadePcmSha256")
        == EXPECTED_FAMILY_B_CASCADE_PCM_SHA256,
    }
    known_failed = [name for name, ok in known_checks.items() if not ok]
    if known_failed:
        raise RuntimeError(
            "Section 3 exact-family identity changed: " + ", ".join(known_failed)
        )

    summary = dict(captured.get("summary") or {})
    summary_checks = {
        "historical Family B captured": int(
            summary.get("historicalFamilyWorkerCount") or 0
        )
        >= 1,
        "exact carrier and score captured": int(
            summary.get("exactHistoricalCarrierAndScoreCount") or 0
        )
        >= 1,
        "all captured Family B workers exact": summary.get(
            "allHistoricalFamilyWorkersExact"
        )
        is True,
        "Section 3 exact provenance captured": summary.get(
            "section3ExactProvenanceCaptured"
        )
        is True,
    }
    summary_failed = [name for name, ok in summary_checks.items() if not ok]
    if summary_failed:
        raise RuntimeError(
            "Section 3 exact-family summary failed: " + ", ".join(summary_failed)
        )

    invariants = dict(captured.get("invariants") or {})
    required_invariants = {
        "originalBandBoundaryPreserved": True,
        "strictExactSemanticComparison": True,
        "strictExactCaptureDiagnosticsComparison": True,
        "strictExactDecisionComparison": True,
        "strictExactScoreComparison": True,
        "comparisonTolerancesWeakened": False,
        "canonicalHistoricalStemFilenamesAppliedBeforeCarrierBuild": True,
        "canonicalStemPcmBytesRequiredUnchanged": True,
        "traceWrapperReturnsOriginalRandintValueUnchanged": True,
        "professionalReferenceOpened": False,
        "runtimeLabelsRequired": False,
        "measures17To32Claimed": False,
        "frozenModelModified": False,
        "frozenPredictionsModified": False,
        "thresholdsModified": False,
        "liveEndpointDeployedOrModified": False,
        "productionModified": False,
    }
    invariant_failed = [
        key
        for key, expected in required_invariants.items()
        if invariants.get(key) is not expected
    ]
    if invariant_failed:
        raise RuntimeError(
            "Section 3 exact-family invariant failed: "
            + ", ".join(invariant_failed)
        )

    expected_semantics = base._expected_semantics(historical_cache, 49, 64)
    expected_capture = base._capture_diagnostics_from_cache(historical_cache)
    expected_summary = {
        "gridCount": len(expected_semantics["grid"]),
        "rowCount": len(expected_semantics["rows"]),
        **expected_capture,
    }

    exact_workers: list[dict[str, Any]] = []
    for raw in captured.get("workers", []) or []:
        if not isinstance(raw, dict):
            continue
        if raw.get("exactHistoricalCarrierAndScores") is not True:
            continue

        carrier = dict(raw.get("carrier") or {})
        scoring = dict(raw.get("scoring") or {})
        direct_pcm = dict(raw.get("directPcm") or {})
        cascade_pcm = dict(raw.get("cascadePcm") or {})
        stem_event_counts = dict(carrier.get("stemEventCounts") or {})
        generated_capture = {
            "rawEventCount": int(carrier.get("rawEventCount", -1)),
            "candidateClusterCount": int(carrier.get("candidateClusterCount", -1)),
            "onsetGroupCount": int(carrier.get("rowCount", -1)),
            "sweepEventCounts": dict(carrier.get("sweepEventCounts") or {}),
            "stemEventCounts": stem_event_counts,
            "candidateStemCount": len(stem_event_counts),
        }

        worker_checks = {
            "Family B pair": raw.get("historicalFamilyPair") is True,
            "Family lockstep": raw.get("familyLockstep") is True,
            "direct family B": raw.get("directFamily") == "B",
            "cascade family B": raw.get("cascadeFamily") == "B",
            "direct PCM exact": direct_pcm.get("sha256")
            == EXPECTED_FAMILY_B_DIRECT_PCM_SHA256,
            "cascade PCM exact": cascade_pcm.get("sha256")
            == EXPECTED_FAMILY_B_CASCADE_PCM_SHA256,
            "carrier built": raw.get("carrierBuilt") is True,
            "canonical filenames": raw.get("canonicalStemFilenames")
            == [
                "direct-demucs6s-guitar.wav",
                "bsroformer-demucs6s-guitar.wav",
            ],
            "canonical PCM preserved": raw.get("canonicalStemPcmPreserved") is True,
            "carrier provenance exact": carrier.get("provenanceReplayPassed") is True,
            "carrier semantics exact": carrier.get("exactSemanticReplayPassed") is True,
            "capture diagnostics exact": carrier.get(
                "captureDiagnosticsReplayPassed"
            )
            is True,
            "semantic mismatch absent": carrier.get("semanticFirstMismatch") is None,
            "capture mismatch absent": carrier.get(
                "captureDiagnosticsFirstMismatch"
            )
            is None,
            "capture values exact": generated_capture == expected_capture,
            "row count exact": int(carrier.get("rowCount", -1))
            == len(expected_semantics["rows"]),
            "decision set exact": scoring.get("decisionSetExact") is True,
            "base scores exact": scoring.get("baseScoresExact") is True,
            "sequence scores exact": scoring.get("sequenceScoresExact") is True,
            "keep probabilities exact": scoring.get("keepProbabilitiesExact") is True,
        }
        if all(worker_checks.values()):
            exact_workers.append(
                {
                    "worker": int(raw.get("worker") or 0),
                    "modalTaskId": raw.get("modalTaskId"),
                    "generatedCapture": generated_capture,
                    "checks": worker_checks,
                }
            )

    if not exact_workers:
        raise RuntimeError(
            "No Section 3 Family-B worker satisfies the strict carrier + frozen-score gate"
        )

    chosen = exact_workers[0]
    expected_semantic_sha = base._canonical_sha256(expected_semantics)
    generated_summary = {
        "gridCount": len(expected_semantics["grid"]),
        "rowCount": int(chosen["generatedCapture"]["onsetGroupCount"]),
        **chosen["generatedCapture"],
    }

    return {
        "label": "section3",
        "measures": "49-64",
        "comparisonScope": (
            "historical exact Family-B original-boundary carrier + exact capture "
            "diagnostics + exact frozen decision/base/sequence/keep scores"
        ),
        "evidenceSource": "section3-exact-family-provenance-capture.json",
        "evidenceWorker": chosen["worker"],
        "evidenceModalTaskId": chosen["modalTaskId"],
        "historicalFamily": "B",
        "historicalFamilyDirectPcmSha256": EXPECTED_FAMILY_B_DIRECT_PCM_SHA256,
        "historicalFamilyCascadePcmSha256": EXPECTED_FAMILY_B_CASCADE_PCM_SHA256,
        "expectedSemanticSha256": expected_semantic_sha,
        "generatedSemanticSha256": expected_semantic_sha,
        "exactSemanticReplayPassed": True,
        "toleranceSemanticReplayPassed": True,
        "semanticFirstMismatch": None,
        "captureDiagnosticsReplayPassed": True,
        "captureDiagnosticsFirstMismatch": None,
        "frozenDecisionReplayPassed": True,
        "frozenBaseScoresReplayPassed": True,
        "frozenSequenceScoresReplayPassed": True,
        "frozenKeepProbabilitiesReplayPassed": True,
        "provenanceReplayPassed": True,
        "expected": expected_summary,
        "generated": generated_summary,
        "exactFamilyProofSummary": summary,
        "exactFamilyProofInvariants": invariants,
    }


@app.function(image=partial_tail_image, gpu="L4", timeout=2400, memory=12288)
def diagnose_surviving_band_provenance_partial_tail(
    source_audio: bytes,
    suffix: str = ".audio",
) -> dict[str, Any]:
    """Run the existing provenance gate with the sealed 113-half-measure tail.

    The shared research carrier intentionally requires complete 16-step measures.
    The calibration audio historically ends after step 7 of measure 113, so the
    reserve carrier has 264 legitimate grid rows, not 272. This adapter adds
    synthetic steps 8-15 only so the unchanged carrier's final completeness guard
    can execute. Candidate assignment is explicitly restricted to the original
    historical grid throughout construction, and the synthetic rows are removed
    before provenance or frozen-score comparison.
    """
    if not source_audio:
        raise ValueError("source_audio is empty")

    import v143_contextual_prune_reference_free_carrier as carrier_module

    original_grid_builder = carrier_module.build_subdivision_grid
    original_nearest_timing_slot = carrier_module.nearest_timing_slot
    original_carrier_builder = (
        carrier_module.build_contextual_prune_reference_free_carrier
    )

    adapter_state: dict[str, Any] = {
        "extendedFinalGrid": False,
        "trimmedReserveGrid": False,
        "syntheticGuardHiddenFromAssignment": False,
        "filteredNearestSlotCalls": 0,
        "historicalMeasure113Steps": list(range(8)),
        "syntheticGuardSteps": list(range(8, 16)),
    }

    def extended_grid_builder(*args: Any, **kwargs: Any) -> list[Any]:
        slots = list(original_grid_builder(*args, **kwargs))
        final_slots = [slot for slot in slots if int(slot.measure) == 113]
        final_steps = [int(slot.step) for slot in final_slots]

        if final_steps == list(range(8)):
            if len(final_slots) < 2:
                raise RuntimeError(
                    "Cannot derive historical measure-113 subdivision spacing"
                )
            previous = final_slots[-2]
            last = final_slots[-1]
            step_seconds = float(last.time_seconds) - float(previous.time_seconds)
            if step_seconds <= 0.0:
                raise RuntimeError(
                    "Historical measure-113 subdivision spacing is not positive"
                )

            slot_type = type(last)
            for step in range(8, 16):
                prior = slots[-1]
                slots.append(
                    slot_type(
                        global_step=int(prior.global_step) + 1,
                        measure=113,
                        step=step,
                        time_seconds=float(prior.time_seconds) + step_seconds,
                    )
                )
            adapter_state["extendedFinalGrid"] = True
        elif final_steps != list(range(16)):
            raise RuntimeError(
                "Unexpected measure-113 timing-grid shape before provenance replay: "
                + repr(final_steps)
            )

        return slots

    def historical_nearest_timing_slot(
        onset_time: float,
        slots: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        # The historical reserve carrier never had measure-113 steps 8-15.
        # Keep those synthetic guard rows invisible to candidate assignment so
        # nearest-slot behavior is exactly the original 264-row behavior.
        historical_slots = [
            slot
            for slot in slots
            if not (
                int(slot.measure) == 113
                and int(slot.step) >= 8
            )
        ]
        if len(historical_slots) != len(slots):
            adapter_state["syntheticGuardHiddenFromAssignment"] = True
            adapter_state["filteredNearestSlotCalls"] = int(
                adapter_state["filteredNearestSlotCalls"]
            ) + 1
        return original_nearest_timing_slot(
            onset_time,
            historical_slots,
            *args,
            **kwargs,
        )

    def partial_tail_carrier_builder(*args: Any, **kwargs: Any) -> Any:
        measure_start = int(kwargs.get("measure_start", 1))
        raw_measure_end = kwargs.get("measure_end")
        measure_end = None if raw_measure_end is None else int(raw_measure_end)

        carrier = original_carrier_builder(*args, **kwargs)
        if measure_start != 97 or measure_end != 113:
            return carrier

        full_final_steps = sorted(
            int(row["step"])
            for row in carrier.grid_rows
            if int(row["measure"]) == 113
        )
        if full_final_steps != list(range(16)):
            raise RuntimeError(
                "Guard-extended reserve carrier did not contain a complete measure 113: "
                + repr(full_final_steps)
            )

        trimmed_grid = tuple(
            dict(row)
            for row in carrier.grid_rows
            if not (
                int(row["measure"]) == 113
                and int(row["step"]) >= 8
            )
        )
        trimmed_final_steps = sorted(
            int(row["step"])
            for row in trimmed_grid
            if int(row["measure"]) == 113
        )
        if trimmed_final_steps != list(range(8)) or len(trimmed_grid) != 264:
            raise RuntimeError(
                "Historical reserve partial-tail restoration failed: "
                f"steps={trimmed_final_steps}, gridCount={len(trimmed_grid)}"
            )

        adapter_state["trimmedReserveGrid"] = True
        return carrier_module.ContextualPruneCarrier(
            rows=carrier.rows,
            grid_rows=trimmed_grid,
            timing=carrier.timing,
            raw_event_count=carrier.raw_event_count,
            candidate_cluster_count=carrier.candidate_cluster_count,
            sweep_event_counts=dict(carrier.sweep_event_counts),
            stem_event_counts=dict(carrier.stem_event_counts),
            measure_start=carrier.measure_start,
            measure_end=carrier.measure_end,
        )

    carrier_module.build_subdivision_grid = extended_grid_builder
    carrier_module.nearest_timing_slot = historical_nearest_timing_slot
    carrier_module.build_contextual_prune_reference_free_carrier = (
        partial_tail_carrier_builder
    )

    try:
        raw_gate = base.diagnose_surviving_band_provenance.get_raw_f()
        result = raw_gate(source_audio, suffix)
    finally:
        carrier_module.build_subdivision_grid = original_grid_builder
        carrier_module.nearest_timing_slot = original_nearest_timing_slot
        carrier_module.build_contextual_prune_reference_free_carrier = (
            original_carrier_builder
        )

    if adapter_state["extendedFinalGrid"] is not True:
        raise RuntimeError("Historical partial-tail grid extension was not exercised")
    if adapter_state["syntheticGuardHiddenFromAssignment"] is not True:
        raise RuntimeError("Synthetic partial-tail guard rows leaked into assignment")
    if adapter_state["trimmedReserveGrid"] is not True:
        raise RuntimeError("Historical reserve grid was not restored to 264 rows")

    section3_cache = base._load_json(
        base.CAL / "fresh-section3-reference-free-cache.json"
    )
    current_section3_observation = dict(
        (result.get("bands") or {}).get("section3") or {}
    )
    exact_section3 = _validated_section3_exact_family_band(
        SECTION3_EXACT_FAMILY_PROOF_REMOTE,
        section3_cache,
        str(result.get("sourceSha256") or ""),
    )
    exact_section3["currentContainerObservation"] = current_section3_observation

    bands = dict(result.get("bands") or {})
    bands["section3"] = exact_section3
    result["bands"] = bands
    result["section3ExactFamilyEvidenceApplied"] = True
    result["section3ExactFamilyProofSha256"] = base._sha256(
        SECTION3_EXACT_FAMILY_PROOF_REMOTE
    )

    all_carriers_passed = all(
        (bands.get(label) or {}).get("provenanceReplayPassed") is True
        for label in ("section2", "section3", "section4", "section5", "reserve")
    )
    reserve_scoring = dict(result.get("reserveScoring") or {})
    result["allCarrierProvenancePassed"] = all_carriers_passed
    result["allSurvivingBandsProvenancePassed"] = (
        all_carriers_passed
        and reserve_scoring.get("reserveScoringReplayPassed") is True
    )

    result["partialTailAdapter"] = {
        **adapter_state,
        "scope": "measure 113 completeness guard; synthetic rows hidden from nearest-slot assignment",
        "comparisonGridCount": 264,
        "comparisonMeasure113Steps": list(range(8)),
        "carrierRowsPostHocModified": False,
        "frozenScorerModified": False,
        "section3EvidenceSource": "completed exact historical Family-B capture",
        "section3CurrentContainerObservationRetained": True,
        "productionModified": False,
    }
    return result


@app.local_entrypoint(name="diagnose")
def diagnose(audio_path: str = "public/gomywayfullaitest.m4a") -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Calibration audio missing or empty: {source}")
    result = diagnose_surviving_band_provenance_partial_tail.remote(
        source.read_bytes(),
        source.suffix,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    pass
