from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCER = ROOT / "analyzer/v143_repaired_timing_precision_candidate_product_modal.py"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"precision replay capture-order failure: {message}")


def check() -> None:
    text = PRODUCER.read_text(encoding="utf-8")
    needles = (
        "precision = apply_reference_free_precision_shadow_v2(",
        "precision, promoted_harmonic_guard = apply_reference_free_promoted_harmonic_guard(",
        "replay_evidence = build_precision_replay_evidence(",
        "candidate = build_precision_candidate_assembly(",
        "with_bends = enrich_rhythm_assembly_with_consensus_bends(",
        "sustained_events, sustain_diagnostics = annotate_sustain_shadow(",
    )
    positions = [text.find(needle) for needle in needles]
    _require(all(position >= 0 for position in positions), "required candidate-stage call missing")
    _require(positions == sorted(positions), "candidate-stage order changed")

    replay_start = positions[2]
    replay_end = text.find(")", replay_start)
    replay_call = text[replay_start : replay_end + 1]
    _require("carrier.rows" in replay_call, "replay is not sourced from physical carrier rows")
    _require("carrier.grid" in replay_call, "replay is not bound to the candidate grid")
    _require("precision" in replay_call, "replay is not bound to post-guard precision identity")

    # Scope is deliberate: replay is captured after the common promoted-harmonic
    # correction and before guitar voicing/semantic/sustain rendering. Therefore
    # it can exactly replay the precision-stage attack/pitch decisions without
    # confusing downstream guitar-position drops with source-pitch suppression.
    _require(
        positions[1] < positions[2] < positions[3],
        "replay must be post-harmonic-guard and pre-voicing",
    )

    print("PASS v143 precision replay capture order")
    print("post_promoted_harmonic_guard=true")
    print("pre_candidate_voicing=true")
    print("pre_semantic_sustain_rendering=true")
    print("source_carrier_rows=true")
    print("source_candidate_grid=true")


if __name__ == "__main__":
    check()
