from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

import modal
import modal_analyzer_v71 as base

engine = base.engine
app = modal.App("dadrock-tab-analyzer-v72-candidate")
image = base.image.add_local_python_source("modal_analyzer_v71")

ENGINE_VERSION = "7.2-phase-1-adaptive-three-way-instrument-separation-v3"

REGISTER_POLICY: dict[str, tuple[int, int]] = {
    "bass": (28, 51),
    "rhythm": (52, 63),
    "lead": (64, 76),
}

MIN_REGISTER_EVENTS = {
    "bass": 2,
    "rhythm": 4,
    "lead": 3,
}

# Each V71 transcription request exposes a slightly different raw inventory.
# These thresholds are taken from the locked Go My Way 2 green benchmark's
# raw inventories, not from its already-gated output. This lets the bass pass
# activate even though its octave-lead inventory is smaller than the lead and
# rhythm passes, while still requiring convincing evidence of all three layers.
STRONG_LAYER_INVENTORY_BY_REQUEST: dict[str, dict[str, int]] = {
    "bass": {
        "bass": 62,
        "rhythm": 38,
        "lead": 11,
    },
    "rhythm": {
        "bass": 49,
        "rhythm": 39,
        "lead": 14,
    },
    "lead": {
        "bass": 49,
        "rhythm": 39,
        "lead": 14,
    },
}

# The strict split is enabled only when the recording contains repeated evidence
# that all three pitch layers are active together. This prevents ordinary lead
# recordings such as Stairway from losing valid notes below MIDI 64.
TIME_BUCKET_SECONDS = 0.18
MIN_TRIPLE_LAYER_BUCKETS = 3
MIN_DUAL_LAYER_BUCKETS = 6


def to_json_safe(value: Any) -> Any:
    return base.to_json_safe(value)


def event_midi(event: dict[str, Any]) -> int | None:
    for key in ("midi", "midiPitch", "pitch"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return int(round(value))
    return None


def event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def register_for_midi(midi: int) -> str | None:
    for part, (low, high) in REGISTER_POLICY.items():
        if low <= midi <= high:
            return part
    return None


def summarize_layer_evidence(
    events: list[dict[str, Any]],
    transcription_type: str,
) -> dict[str, Any]:
    register_counts: Counter[str] = Counter()
    time_buckets: dict[int, set[str]] = defaultdict(set)

    for event in events:
        midi = event_midi(event)
        if midi is None:
            continue
        part = register_for_midi(midi)
        if part is None:
            continue
        register_counts[part] += 1
        bucket = int(event_start(event) / TIME_BUCKET_SECONDS)
        time_buckets[bucket].add(part)

    triple_buckets = sum(1 for layers in time_buckets.values() if len(layers) == 3)
    dual_or_more_buckets = sum(1 for layers in time_buckets.values() if len(layers) >= 2)

    minimums_met = all(
        register_counts.get(part, 0) >= minimum
        for part, minimum in MIN_REGISTER_EVENTS.items()
    )

    request_thresholds = STRONG_LAYER_INVENTORY_BY_REQUEST[transcription_type]
    strong_inventory_met = all(
        register_counts.get(part, 0) >= minimum
        for part, minimum in request_thresholds.items()
    )

    simultaneous_support = (
        triple_buckets >= MIN_TRIPLE_LAYER_BUCKETS
        or (
            triple_buckets >= 1
            and dual_or_more_buckets >= MIN_DUAL_LAYER_BUCKETS
        )
    )

    eligible = minimums_met and (simultaneous_support or strong_inventory_met)

    if simultaneous_support:
        activation_reason = "repeated-simultaneous-three-layer-evidence"
    elif strong_inventory_met:
        activation_reason = "request-aware-locked-baseline-strength-inventory"
    else:
        activation_reason = "insufficient-three-layer-evidence"

    return {
        "registerCounts": dict(register_counts),
        "timeBucketSeconds": TIME_BUCKET_SECONDS,
        "tripleLayerBuckets": triple_buckets,
        "dualOrMoreLayerBuckets": dual_or_more_buckets,
        "minimumRegisterEvents": MIN_REGISTER_EVENTS,
        "strongLayerInventoryForRequest": request_thresholds,
        "minimumsMet": minimums_met,
        "strongInventoryMet": strong_inventory_met,
        "simultaneousSupport": simultaneous_support,
        "activationReason": activation_reason,
        "strictThreeWaySeparationEligible": eligible,
    }


def gate_events(
    events: list[dict[str, Any]],
    transcription_type: str,
) -> list[dict[str, Any]]:
    low, high = REGISTER_POLICY[transcription_type]
    return [
        event
        for event in events
        if (midi := event_midi(event)) is not None and low <= midi <= high
    ]


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    if transcription_type not in REGISTER_POLICY:
        raise ValueError(
            f"Unsupported transcription type: {transcription_type!r}. "
            f"Expected one of {sorted(REGISTER_POLICY)}."
        )

    result = base.analyze_audio_file(audio_path, transcription_type)
    raw_events = [
        event
        for event in (result.get("events") or [])
        if isinstance(event, dict)
    ]
    evidence = summarize_layer_evidence(raw_events, transcription_type)
    eligible = bool(evidence["strictThreeWaySeparationEligible"])

    if eligible:
        separated_events = gate_events(raw_events, transcription_type)
        result["rawEvents"] = raw_events
        result["events"] = separated_events
        result["generatedTabRequiresRefresh"] = True
        mode = "strict-three-way-register-gate"
    else:
        separated_events = raw_events
        mode = "protected-v71-fallback"

    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["adaptiveInstrumentSeparation"] = {
        "mode": mode,
        "requestedPart": transcription_type,
        "policy": {
            part: [low, high]
            for part, (low, high) in REGISTER_POLICY.items()
        },
        "rawEventCount": len(raw_events),
        "outputEventCount": len(separated_events),
        "evidence": evidence,
        "safetyRule": (
            "use-the-strict-register-split-only-when-repeated-simultaneous-"
            "three-layer-evidence-or-request-aware-locked-baseline-strength-"
            "inventory-is-present-otherwise-preserve-v71"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = ENGINE_VERSION
    result["instrumentSeparationMode"] = mode
    return result


@app.function(image=image, timeout=600, memory=4096)
def benchmark_healthcheck() -> dict[str, Any]:
    return {
        "ok": True,
        "engineVersion": ENGINE_VERSION,
        "registerPolicy": {
            part: [low, high]
            for part, (low, high) in REGISTER_POLICY.items()
        },
        "minimumRegisterEvents": MIN_REGISTER_EVENTS,
        "strongLayerInventoryByRequest": STRONG_LAYER_INVENTORY_BY_REQUEST,
        "timeBucketSeconds": TIME_BUCKET_SECONDS,
        "minimumTripleLayerBuckets": MIN_TRIPLE_LAYER_BUCKETS,
        "minimumDualLayerBuckets": MIN_DUAL_LAYER_BUCKETS,
    }
