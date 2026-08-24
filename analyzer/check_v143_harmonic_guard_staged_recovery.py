from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECOVERY = ROOT / "analyzer" / "v143_harmonic_guard_staged_recovery_modal.py"
PRODUCT = ROOT / "analyzer" / "v143_repaired_timing_precision_candidate_product_modal.py"
OUTPUT = ROOT / "debug" / "v143-contextual-prune" / "harmonic-guard-staged-recovery-preflight.json"
PROTECTED = ROOT / "analyzer" / "v143_reference_free_rhythm_pipeline.py"

EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"
EXPECTED_FIXTURE_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_NORMALIZED_SHA256 = "ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f"
EXPECTED_DIRECT_SHA256 = "0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c"
EXPECTED_CASCADE_SHA256 = "546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41"
EXPECTED_SIMULATED_RENDER_SHA256 = "50aa17f6855a816ce73f8b427062e8c24c5ce0a5751c7b6425e79c6cea89ecca"

FORBIDDEN = (
    "Professionalexample",
    "professional-rhythm-complete",
    "rhythm-professional-holdout-score",
    "Songsterr",
    "Are You Gonna Go My Way",
    "Lenny Kravitz",
    "Craig Ross",
)

REQUIRED_PIPELINE_CALLS = (
    "estimate_reference_free_timing",
    "repair_reference_free_beat_grid_from_samples",
    "build_contextual_prune_reference_free_carrier",
    "run_contextual_prune",
    "apply_reference_free_shadow_correction",
    "apply_reference_free_precision_shadow",
    "apply_reference_free_promoted_harmonic_guard",
    "build_precision_candidate_assembly",
    "enrich_rhythm_assembly_with_consensus_bends",
    "enrich_rhythm_assembly_with_legato",
    "guard_semantic_events",
    "build_pitch_energy_view",
    "annotate_sustain_shadow",
    "promote_candidate_sustain",
    "render_rhythm_tab",
)


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path.relative_to(ROOT))], cwd=ROOT, text=True).strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decorator_resources(tree: ast.AST) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for deco in node.decorator_list:
            if not isinstance(deco, ast.Call) or not isinstance(deco.func, ast.Attribute):
                continue
            if deco.func.attr != "function":
                continue
            values: dict[str, object] = {}
            for keyword in deco.keywords:
                if isinstance(keyword.value, ast.Constant):
                    values[keyword.arg or ""] = keyword.value.value
            result[node.name] = values
    return result


def main() -> None:
    source = RECOVERY.read_text(encoding="utf-8")
    product_source = PRODUCT.read_text(encoding="utf-8")
    tree = ast.parse(source)
    resources = decorator_resources(tree)

    fixture = ROOT / "public" / "gomywayfullaitest.m4a"
    checks = {
        "protectedPipelineExact": git_blob(PROTECTED) == EXPECTED_PROTECTED_BLOB,
        "approvedFixtureExact": fixture.exists() and sha256_file(fixture) == EXPECTED_FIXTURE_SHA256,
        "recoveryPythonParses": tree is not None,
        "onlyRoformerHasGpuKeyword": all(
            ((name == "roformer_gpu") == ("gpu" in values))
            for name, values in resources.items()
            if name in {"direct_demucs_cpu", "roformer_gpu", "cascade_demucs_cpu", "assemble_candidate_cpu"}
        ),
        "roformerIsL4": resources.get("roformer_gpu", {}).get("gpu") == "L4",
        "roformerGpuTimeoutAtMost600": int(resources.get("roformer_gpu", {}).get("timeout") or 999999) <= 600,
        "directIsCpuOnly": "gpu" not in resources.get("direct_demucs_cpu", {}) and resources.get("direct_demucs_cpu", {}).get("cpu") == 1.0,
        "cascadeIsCpuOnly": "gpu" not in resources.get("cascade_demucs_cpu", {}) and resources.get("cascade_demucs_cpu", {}).get("cpu") == 1.0,
        "assemblyIsCpuOnly": "gpu" not in resources.get("assemble_candidate_cpu", {}) and float(resources.get("assemble_candidate_cpu", {}).get("cpu") or 0) > 0,
        "allFourStagesPresent": all(name in resources for name in ("direct_demucs_cpu", "roformer_gpu", "cascade_demucs_cpu", "assemble_candidate_cpu")),
        "exactFixtureBound": EXPECTED_FIXTURE_SHA256 in source,
        "exactNormalizedBound": EXPECTED_NORMALIZED_SHA256 in source,
        "exactDirectStemBound": EXPECTED_DIRECT_SHA256 in source,
        "exactCascadeStemBound": EXPECTED_CASCADE_SHA256 in source,
        "deterministicDemucsControlsReused": "DEMUCS_SINGLE_THREAD_ENV" in source and "seeded_audio_separator_cli" in source,
        "roformerFrozenHelperReused": "separate_roformer_instrumental" in source,
        "productOuterNormalizationPreserved": '"-ar", "44100", "-ac", "2"' in source and '"pcm_s16le"' in source,
        "allProductPipelineCallsPreserved": all(name in source for name in REQUIRED_PIPELINE_CALLS),
        "guardBeforeCandidateAssembly": source.find("apply_reference_free_promoted_harmonic_guard") < source.find("build_precision_candidate_assembly(carrier.rows"),
        "approvedAudioOrchestrationOrder": (
            source.find("direct_demucs_cpu.remote")
            < source.find("roformer_gpu.remote")
            < source.find("cascade_demucs_cpu.remote")
            < source.find("assemble_candidate_cpu.remote")
        ),
        "noWholeProductRemoteCall": "analyze_repaired_precision_candidate.remote" not in source,
        "forbiddenReferenceTokensAbsent": not any(token in source for token in FORBIDDEN),
        "professionalReferenceHardFalse": '"professionalReferenceUsed": False' in source,
        "productionHardFalse": '"productionModified": False' in source,
        "productModePreserved": "v143-repaired-timing-contextual-prune-precision-promoted-harmonic-guard-candidate" in source,
        "productSourceStillContainsSamePipelineCalls": all(name in product_source for name in REQUIRED_PIPELINE_CALLS if name != "promote_candidate_sustain"),
    }

    failed = [key for key, value in checks.items() if not value]
    proof = {
        "schemaVersion": 1,
        "gate": "v143-harmonic-guard-staged-recovery-preflight",
        "recoverySourceBlob": git_blob(RECOVERY),
        "productSourceBlob": git_blob(PRODUCT),
        "protectedPipelineBlob": git_blob(PROTECTED),
        "expectedProtectedPipelineBlob": EXPECTED_PROTECTED_BLOB,
        "approvedFixtureSha256": sha256_file(fixture) if fixture.exists() else None,
        "expectedApprovedFixtureSha256": EXPECTED_FIXTURE_SHA256,
        "exactTwoPassStageBindings": {
            "normalizedWavSha256": EXPECTED_NORMALIZED_SHA256,
            "directGuitarStemSha256": EXPECTED_DIRECT_SHA256,
            "cascadeGuitarStemSha256": EXPECTED_CASCADE_SHA256,
        },
        "offlineExpectedGuardProjectionSha256": EXPECTED_SIMULATED_RENDER_SHA256,
        "modalResourcePlan": {
            "directDemucs": "cpu",
            "roformer": "L4",
            "roformerTimeoutSeconds": resources.get("roformer_gpu", {}).get("timeout"),
            "cascadeDemucs": "cpu",
            "candidateAssembly": "cpu",
            "fullPipelineL4Reservation": False,
        },
        "historicalExactProofEvidence": {
            "runId": 32697939613,
            "directDemucsObservedSecondsApprox": 462,
            "roformerObservedSecondsApprox": 47,
            "cascadeDemucsObservedSecondsApprox": 437,
            "note": "Observed in successful exact pass logs; recovery binds resulting exact direct/cascade stem hashes rather than trusting timing.",
        },
        "checks": checks,
        "failedChecks": failed,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "modalInvokedByPreflight": False,
        "modalGpuUsedByPreflight": False,
        "passed": not failed,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(proof, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(proof, indent=2))
    if failed:
        raise SystemExit("staged recovery preflight failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
