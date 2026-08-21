from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal

import v143_contextual_prune_surviving_band_provenance_modal as base


app = modal.App("dadrock-v143-surviving-band-provenance-partial-tail")

# Reuse the already-isolated provenance image, adding only the source modules
# this adapter imports directly. Production, frozen scorer/model artifacts, and
# the live endpoint remain untouched.
partial_tail_image = base.provenance_image.add_local_python_source(
    "v143_contextual_prune_surviving_band_provenance_modal",
    "v143_contextual_prune_reference_free_carrier",
    "v143_candidate_timing_adapter",
)


@app.function(image=partial_tail_image, gpu="L4", timeout=2400, memory=12288)
def diagnose_surviving_band_provenance_partial_tail(
    source_audio: bytes,
    suffix: str = ".audio",
) -> dict[str, Any]:
    """Run the existing provenance gate with the sealed 113-half-measure tail.

    The shared research carrier intentionally requires complete 16-step measures.
    The calibration audio historically ends after step 7 of measure 113, so the
    reserve carrier has 264 legitimate grid rows, not 272. This adapter extends
    only the final timing-grid guard to steps 8-15, lets the unchanged carrier
    builder finish, then removes those synthetic guard-only rows before any
    provenance or frozen-score comparison is performed.
    """
    if not source_audio:
        raise ValueError("source_audio is empty")

    import v143_contextual_prune_reference_free_carrier as carrier_module

    original_grid_builder = carrier_module.build_subdivision_grid
    original_carrier_builder = (
        carrier_module.build_contextual_prune_reference_free_carrier
    )

    adapter_state: dict[str, Any] = {
        "extendedFinalGrid": False,
        "trimmedReserveGrid": False,
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
    carrier_module.build_contextual_prune_reference_free_carrier = (
        partial_tail_carrier_builder
    )

    try:
        raw_gate = base.diagnose_surviving_band_provenance.get_raw_f()
        result = raw_gate(source_audio, suffix)
    finally:
        carrier_module.build_subdivision_grid = original_grid_builder
        carrier_module.build_contextual_prune_reference_free_carrier = (
            original_carrier_builder
        )

    if adapter_state["extendedFinalGrid"] is not True:
        raise RuntimeError("Historical partial-tail grid extension was not exercised")
    if adapter_state["trimmedReserveGrid"] is not True:
        raise RuntimeError("Historical reserve grid was not restored to 264 rows")

    result["partialTailAdapter"] = {
        **adapter_state,
        "scope": "measure 113 timing-grid completeness guard only",
        "comparisonGridCount": 264,
        "comparisonMeasure113Steps": list(range(8)),
        "carrierRowsModified": False,
        "frozenScorerModified": False,
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
