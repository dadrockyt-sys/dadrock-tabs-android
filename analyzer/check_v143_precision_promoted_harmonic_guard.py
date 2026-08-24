from __future__ import annotations

import json
import subprocess
from pathlib import Path

from v143_contextual_prune_precision_shadow import PrecisionShadowResult
from v143_precision_promoted_harmonic_guard import apply_reference_free_promoted_harmonic_guard


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"
AUDIT_PATH = ROOT / "debug" / "v143-contextual-prune" / "precision-polyphonic-expansion-audit.json"
OUTPUT_PATH = ROOT / "debug" / "v143-contextual-prune" / "precision-promoted-harmonic-guard-proof.json"
MIDI_MIN = 28
MIDI_MAX = 112


def _vector(values: dict[int, float], default: float = -2.0) -> list[float]:
    result = [float(default)] * (MIDI_MAX - MIDI_MIN + 1)
    for midi, value in values.items():
        result[int(midi) - MIDI_MIN] = float(value)
    return result


def _row(measure: int, onset: float, values: dict[int, float], candidates: list[int]) -> dict:
    vector = _vector(values)
    view = {
        "attackMax": vector,
        "earlyMean": vector,
        "sustainMean": vector,
    }
    return {
        "measure": int(measure),
        "onsetTime": float(onset),
        "candidateMidis": list(candidates),
        "stemSupportMax": 2,
        "sweepSupportMax": 4,
        "detectionCountSum": 8,
        "viewA": view,
        "viewB": view,
    }


def main() -> int:
    grid = {
        (1, 0): 0.0,
        (1, 4): 0.5,
        (1, 8): 1.0,
    }
    rows = [
        _row(1, 0.0, {40: 0.78, 52: 0.90}, [40, 52]),
        _row(1, 0.5, {45: 0.78, 52: 0.90}, [45, 52]),
        _row(1, 1.0, {40: 0.82, 52: 0.90}, [40, 52]),
    ]
    precision = PrecisionShadowResult(
        input_events=frozenset(grid),
        retained_events=frozenset(grid),
        pruned_events=frozenset(),
        original_pitch_sets={
            (1, 0): (40, 52),
            (1, 4): (45, 52),
            (1, 8): (40, 52),
        },
        pitch_sets={
            (1, 0): (40, 52),
            (1, 4): (45, 52),
            (1, 8): (40, 52),
        },
        primary_midis={
            (1, 0): 40,
            (1, 4): 45,
            (1, 8): 52,
        },
        fail_safe_events=frozenset(),
        fundamental_promotions=2,
        suppressed_pitch_count=0,
    )

    guarded, diagnostics = apply_reference_free_promoted_harmonic_guard(rows, grid, precision)
    diag = diagnostics.to_dict()

    synthetic_checks = {
        "attackIdentityUnchanged": guarded.retained_events == precision.retained_events,
        "primaryMidiUnchanged": guarded.primary_midis == precision.primary_midis,
        "promotedOctaveStrongestSuppressed": guarded.pitch_sets[(1, 0)] == (40,),
        "nonHarmonicStrongestPreserved": guarded.pitch_sets[(1, 4)] == (45, 52),
        "unpromotedPitchSetPreserved": guarded.pitch_sets[(1, 8)] == (40, 52),
        "exactlyOneSyntheticPitchSuppressed": guarded.suppressed_pitch_count == 1,
        "diagnosticInspectedThree": diag["inspectedAttackCount"] == 3,
        "diagnosticSawTwoPromotions": diag["promotedPrimaryCount"] == 2,
        "diagnosticSawOneHarmonicPromotion": diag["harmonicStrongestAbovePromotedPrimaryCount"] == 1,
        "diagnosticSuppressedOne": diag["suppressedStrongestHarmonicCount"] == 1,
        "noAttackAdded": diag["addsUnobservedAttack"] is False,
        "noPitchAdded": diag["addsUnobservedPitch"] is False,
        "noRelocation": diag["relocatesAttack"] is False,
    }

    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    old_candidate_checks = {
        "auditSchemaV2": int(audit.get("schemaVersion") or 0) >= 2,
        "doubleCountPathProven": audit.get("harmonicPromotionDoubleCountPathProven") is True,
        "oldFundamentalPromotionCount144": int(audit.get("fundamentalPromotionCountMetadata") or -1) == 144,
        "oldAllPromotedStrongestRendered": int(audit.get("promotedPrimaryWithStrongestRenderedCount") or -1) == 144,
        "oldHarmonicPromotedStrongestRendered96": int(audit.get("promotedPrimaryWithHarmonicStrongestRenderedCount") or -1) == 96,
        "oldOctavePromotedStrongest78": int((audit.get("promotedPrimaryStrongestIntervalHistogram") or {}).get("12") or -1) == 78,
        "oldSerializedPerPitchBasicPitchSupportUnavailable": audit.get("perPitchBasicPitchSupportRecoverableFromSerializedHypotheses") is False,
    }

    protected = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        cwd=ROOT,
        text=True,
    ).strip()
    protected_ok = protected == EXPECTED_PROTECTED_BLOB

    source = (ROOT / "analyzer" / "v143_precision_promoted_harmonic_guard.py").read_text(encoding="utf-8").lower()
    forbidden = [
        "professional-rhythm-complete",
        "reference.json",
        "songsterr",
        "are you gonna go my way",
        "lenny kravitz",
        "craig ross",
    ]
    anti_leakage = not any(token in source for token in forbidden)

    passed = all(synthetic_checks.values()) and all(old_candidate_checks.values()) and protected_ok and anti_leakage
    report = {
        "schemaVersion": 1,
        "gate": "v143-precision-promoted-harmonic-guard-proof",
        "syntheticChecks": synthetic_checks,
        "oldCandidateChecks": old_candidate_checks,
        "oldCandidateScoringRelevantSuppressionOpportunityCount": 96,
        "oldCandidateOctaveSuppressionOpportunityCount": 78,
        "correctionChangesPitchIdentity": True,
        "correctionChangesAttackIdentity": False,
        "correctionAddsPitch": False,
        "correctionRelocatesAttack": False,
        "guardDiagnostics": diag,
        "protectedPipelineBlob": protected,
        "expectedProtectedPipelineBlob": EXPECTED_PROTECTED_BLOB,
        "protectedPipelineUnchanged": protected_ok,
        "antiLeakagePassed": anti_leakage,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "modalGpuUsed": False,
        "passed": passed,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit("V143 precision promoted harmonic guard proof failed")

    print("V143 precision promoted harmonic guard checker: PASS")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
