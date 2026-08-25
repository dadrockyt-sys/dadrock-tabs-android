#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

EXPECTED_RENDERED_EVENTS = 1209
EXPECTED_BASELINE_RENDERED = 967
EXPECTED_RESCUED_RENDERED = 242
EXPECTED_PRESERVED_METADATA = 933
EXPECTED_NEUTRAL_BASELINE = 34
EXPECTED_NEUTRAL_RESCUED = 242
EXPECTED_NEUTRAL_TOTAL = EXPECTED_NEUTRAL_BASELINE + EXPECTED_NEUTRAL_RESCUED

SEMANTIC_FIELDS = (
    "durationSeconds",
    "sustainTier",
    "bendSemitones",
    "bendTargetFret",
    "bendTargetMidi",
    "bendRelease",
    "legatoTargetEventIndex",
    "legatoTargetFret",
    "legatoTargetMidi",
    "legatoContinuationFromEventIndex",
    "legatoContinuationType",
)


def _identity(event: Mapping[str, Any]) -> tuple[int, int, int]:
    return int(event["measure"]), int(event["step"]), int(event.get("midi", event.get("dominantMidi")))


def _duration_steps(event: Mapping[str, Any]) -> int:
    sustain = event.get("rhythmSustain") if isinstance(event.get("rhythmSustain"), Mapping) else {}
    value = sustain.get("durationSteps", event.get("durationSteps", 1))
    try:
        return max(1, int(round(float(value))))
    except (TypeError, ValueError):
        return 1


def _techniques(event: Mapping[str, Any]) -> tuple[str, ...]:
    found: set[str] = set()
    for field in ("rhythmTechniques", "techniques"):
        for value in event.get(field) or []:
            if isinstance(value, str):
                name = value
            elif isinstance(value, Mapping):
                name = value.get("type")
            else:
                name = ""
            normalized = str(name or "").strip().lower()
            if normalized:
                found.add(normalized)
    return tuple(sorted(found))


def validate(product: Mapping[str, Any], stream: Mapping[str, Any]) -> dict[str, Any]:
    baseline_events = [event for event in product.get("events") or [] if isinstance(event, Mapping)]
    render_events = [event for event in stream.get("events") or [] if isinstance(event, Mapping)]
    baseline_by_identity = {_identity(event): event for event in baseline_events}
    rendered_identities = {_identity(event) for event in render_events}

    preserved = [event for event in render_events if event.get("metadataSource") == "preserved-baseline-note"]
    neutral = [event for event in render_events if event.get("metadataSource") == "v5-shadow-neutral"]
    neutral_indices = {int(event["eventIndex"]) for event in neutral}
    neutral_baseline = [event for event in neutral if event.get("v5AttackClass") == "baseline"]
    neutral_rescued = [event for event in neutral if event.get("v5AttackClass") == "rescued"]

    preserved_identity_exact = True
    preserved_duration_exact = True
    preserved_techniques_exact = True
    for event in preserved:
        source = baseline_by_identity.get(_identity(event))
        if source is None:
            preserved_identity_exact = False
            continue
        if int(event.get("durationSteps", 1)) != _duration_steps(source):
            preserved_duration_exact = False
        if _techniques(event) != _techniques(source):
            preserved_techniques_exact = False

    neutral_identity_absent_from_baseline = all(_identity(event) not in baseline_by_identity for event in neutral)
    neutral_one_step = all(int(event.get("durationSteps", 0)) == 1 for event in neutral)
    neutral_no_techniques = all(not _techniques(event) for event in neutral)
    neutral_no_semantic_fields = all(
        not any(field in event for field in SEMANTIC_FIELDS)
        for event in neutral
    )
    neutral_baseline_is_corrected_primary = all(
        event.get("v5PrimaryCorrected") is True
        and event.get("v5Primary") is True
        and event.get("v5AttackClass") == "baseline"
        for event in neutral_baseline
    )
    neutral_rescued_is_rescued = all(
        event.get("v5AttackClass") == "rescued"
        and event.get("v5PrimaryCorrected") is False
        for event in neutral_rescued
    )

    no_preserved_legato_targets_neutral = True
    for event in preserved:
        target = event.get("legatoTargetEventIndex")
        if target is not None and int(target) in neutral_indices:
            no_preserved_legato_targets_neutral = False
            break

    historical_technique_identities = {
        _identity(event)
        for event in baseline_events
        if _techniques(event)
    }
    lost_technique_identities = historical_technique_identities - rendered_identities
    neutral_corrected_attacks = {
        (int(event["measure"]), int(event["step"]))
        for event in neutral_baseline
        if event.get("v5PrimaryCorrected") is True
    }
    lost_techniques_only_at_corrected_attacks = all(
        (measure, step) in neutral_corrected_attacks
        for measure, step, _midi in lost_technique_identities
    )
    rendered_technique_identities = {
        _identity(event)
        for event in render_events
        if _techniques(event)
    }
    invented_technique_identities = rendered_technique_identities - historical_technique_identities

    summary = stream.get("summary") if isinstance(stream.get("summary"), Mapping) else {}
    checks = {
        "streamValidationPassed": stream.get("validationPassed") is True,
        "streamReferenceFree": stream.get("referenceFree") is True,
        "professionalReferenceUnused": stream.get("professionalReferenceUsed") is False,
        "modalUnused": stream.get("modalInvoked") is False,
        "productionUntouched": stream.get("productionModified") is False,
        "renderedEventCount1209": len(render_events) == EXPECTED_RENDERED_EVENTS,
        "baselineRendered967": int(summary.get("baselineRenderedEventCount") or -1) == EXPECTED_BASELINE_RENDERED,
        "rescuedRendered242": int(summary.get("rescuedRenderedEventCount") or -1) == EXPECTED_RESCUED_RENDERED,
        "preservedMetadata933": len(preserved) == EXPECTED_PRESERVED_METADATA,
        "neutralBaseline34": len(neutral_baseline) == EXPECTED_NEUTRAL_BASELINE,
        "neutralRescued242": len(neutral_rescued) == EXPECTED_NEUTRAL_RESCUED,
        "neutralTotal276": len(neutral) == EXPECTED_NEUTRAL_TOTAL,
        "preservedIdentityExact": preserved_identity_exact,
        "preservedDurationExact": preserved_duration_exact,
        "preservedTechniquesExact": preserved_techniques_exact,
        "neutralIdentityAbsentFromBaseline": neutral_identity_absent_from_baseline,
        "neutralOneStep": neutral_one_step,
        "neutralNoTechniques": neutral_no_techniques,
        "neutralNoSemanticFields": neutral_no_semantic_fields,
        "neutralBaselineIsCorrectedPrimary": neutral_baseline_is_corrected_primary,
        "neutralRescuedIsRescued": neutral_rescued_is_rescued,
        "noPreservedLegatoTargetsNeutral": no_preserved_legato_targets_neutral,
        "lostTechniquesOnlyAtCorrectedAttacks": lost_techniques_only_at_corrected_attacks,
        "noInventedTechniqueIdentity": not invented_technique_identities,
    }
    passed = all(checks.values())
    return {
        "schemaVersion": 1,
        "classification": "v143-v5-conservative-neutral-metadata-policy-validation",
        "policy": "preserve-exact-baseline-metadata-else-one-step-no-technique-no-relational-semantics",
        "validationPassed": passed,
        "metadataPolicyResolved": passed,
        "neutralFallbackConservative": passed,
        "freezeReady": False,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "modalInvoked": False,
        "productionModified": False,
        "counts": {
            "renderedEventCount": len(render_events),
            "preservedMetadataEventCount": len(preserved),
            "neutralEventCount": len(neutral),
            "neutralBaselineEventCount": len(neutral_baseline),
            "neutralRescuedEventCount": len(neutral_rescued),
            "historicalTechniqueIdentityCount": len(historical_technique_identities),
            "lostHistoricalTechniqueIdentityCount": len(lost_technique_identities),
            "inventedTechniqueIdentityCount": len(invented_technique_identities),
        },
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("render_stream", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(json.loads(args.product.read_text()), json.loads(args.render_stream.read_text()))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    return 0 if result["validationPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
