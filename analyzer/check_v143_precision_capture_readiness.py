from __future__ import annotations

from pathlib import Path

from check_v143_precision_replay_capture_order import check as check_replay_capture_order
from check_v143_precision_replay_corruption_rejection import check as check_replay_corruption_rejection

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/v143-repaired-timing-precision-candidate-product.yml"
PRODUCER = ROOT / "analyzer/v143_repaired_timing_precision_candidate_product_modal.py"
POLICY = ROOT / "analyzer/v143_contextual_prune_precision_shadow_v2.py"
REPLAY = ROOT / "analyzer/v143_precision_replay_policy_compare.py"
VALIDATOR = ROOT / "analyzer/v143_precision_replay_artifact_validator.py"
CORRUPTION_CHECK = ROOT / "analyzer/check_v143_precision_replay_corruption_rejection.py"
CAPTURE_ORDER_CHECK = ROOT / "analyzer/check_v143_precision_replay_capture_order.py"
PROTECTED = ROOT / "analyzer/v143_reference_free_rhythm_pipeline.py"

TARGET_BRANCH = "v143-contextual-prune-lobo"
LOCK_PATH = "debug/v143-contextual-prune/precision-v2-capture-lock.json"
PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"
APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"precision capture readiness failure: {message}")


def ordered(text: str, *needles: str) -> bool:
    cursor = -1
    for needle in needles:
        cursor = text.find(needle, cursor + 1)
        if cursor < 0:
            return False
    return True


def main() -> None:
    # These are CPU-only source-integrity checks and run before any reservation.
    check_replay_corruption_rejection()
    check_replay_capture_order()

    workflow = WORKFLOW.read_text(encoding="utf-8")
    producer = PRODUCER.read_text(encoding="utf-8")
    policy = POLICY.read_text(encoding="utf-8")
    replay = REPLAY.read_text(encoding="utf-8")
    validator = VALIDATOR.read_text(encoding="utf-8")
    corruption_check = CORRUPTION_CHECK.read_text(encoding="utf-8")
    capture_order_check = CAPTURE_ORDER_CHECK.read_text(encoding="utf-8")

    require(TARGET_BRANCH in workflow, "target branch missing from workflow")
    require('refs/heads/$TARGET_BRANCH' in workflow, "workflow dispatch ref is not pinned to target branch variable")
    require("GITHUB_SHA" in workflow and "origin/$TARGET_BRANCH" in workflow, "dispatch SHA is not bound to remote target head")
    require(PROTECTED_BLOB in workflow, "protected pipeline blob guard missing")
    require(APPROVED_AUDIO_SHA256 in workflow, "approved fixture SHA guard missing")
    require(LOCK_PATH in workflow, "one-shot lock path missing")
    require("automaticRetryAllowed" in workflow, "reservation does not explicitly prohibit automatic retry")
    require("reserved_before_modal" in workflow, "pre-Modal reservation state missing")
    require("singlePaidCaptureConsumed" in workflow, "capture-consumption state missing")
    require("actions/upload-artifact@v4" in workflow and "if: always()" in workflow, "failure-path artifact salvage missing")
    require("python analyzer/v143_precision_replay_artifact_validator.py --self-test" in workflow, "replay validator self-test missing from pre-Modal gate")
    require("replayArtifactValidationSha256" in workflow, "final lock does not bind replay validation artifact")
    require("replayEligibleAttackCount" in workflow, "final lock does not bind eligible attack universe")
    require("replayEligiblePitchHypothesisCount" in workflow, "final lock does not bind eligible pitch universe")
    require("baselineAttackReplayMatches" in workflow, "final lock does not require exact baseline attack replay")
    require("attackPolicyReplayReady" in workflow, "final lock does not require attack-policy replay readiness")

    modal_command = "python -m modal run analyzer/v143_repaired_timing_precision_candidate_product_modal.py::approved_audio"
    require(workflow.count(modal_command) == 1, "workflow must contain exactly one paid Modal command")
    require(producer.count(".remote(") == 1, "producer must contain exactly one Modal .remote call")
    require("precisionReplayEvidence" in producer and "build_precision_replay_evidence(" in producer, "producer replay evidence persistence missing")

    for token in (
        '"schemaVersion": 2',
        '"replayCompleteness": "retained-pitch-plus-eligible-attack-source-universe"',
        '"inputAttackKeys"',
        '"carrierMissingInputAttackKeys"',
        '"eligibleAttacks"',
        '"precisionStrength"',
        '"sourceViewEvidenceReady": True',
        '"precisionStrengthRecomputeReady": True',
        '"zeroValuePreservationReady": True',
        '"fixedRetainedAttackPitchReplayReady": True',
        '"attackPolicyReplayReady": True',
    ):
        require(token in policy, f"full replay serializer token missing: {token}")

    require("import modal" not in replay and ".remote(" not in replay and "modal run" not in replay, "CPU replay path contains Modal usage")
    require("import modal" not in validator and ".remote(" not in validator and "modal run" not in validator, "replay validator contains Modal usage")
    require("validate_product(" in validator and "_self_test()" in validator, "replay validator API/self-test missing")
    require('replay.get("schemaVersion") == 2' in validator, "replay validator does not require schemaVersion 2")
    for token in (
        "baselineAttackReplayMatches",
        "sourceViewEvidenceMatches",
        "precisionStrengthRecomputeMatches",
        "zeroValuePreservationMatches",
        "_legacy_strength(",
        "_recompute_attack_policy(",
        "eligibleAttackCount",
        "eligiblePitchHypothesisCount",
    ):
        require(token in validator, f"replay validator token missing: {token}")

    for token in (
        "_recomputed_primary_midi(",
        "_verified_primary_midi(",
        "primaryRecomputeMatches",
        "primaryRecomputeMismatchAttackCount",
        "storedV2ReplayMatches",
        "v2ReplayMismatchAttackCount",
        "stored v2 selection disagrees with independent CPU replay",
    ):
        require(token in replay, f"strict pitch replay token missing: {token}")

    require("two-view aggregate mismatch" in corruption_check, "corruption guard lacks two-view mismatch test")
    require("precision strength mismatch" in corruption_check, "corruption guard lacks strength mismatch test")
    require("grid/onset error mismatch" in corruption_check, "corruption guard lacks grid/onset mismatch test")
    require("-= 0.20" in corruption_check, "two-view corruption must force aggregate minimum to change")

    require("post-harmonic-guard and pre-voicing" in capture_order_check, "capture-order scope assertion missing")
    require("carrier.rows" in capture_order_check and "carrier.grid" in capture_order_check, "capture-order source binding missing")

    require(
        ordered(
            workflow,
            "Explicit paid-capture authorization and one-shot lock gate",
            "Safety and anti-leakage gate",
            "Reserve the one-shot capture before Modal",
            "reserved_before_modal",
            'git push origin "HEAD:$TARGET_BRANCH"',
            "Run exactly one approved-audio candidate capture",
            modal_command,
            "Validate candidate invariants and replay evidence",
            "Validate replay artifact exact binding",
            "Build CPU replay policy comparison",
            "Finalize one-shot capture lock",
            "Preserve one-shot capture outputs",
        ),
        "required reservation/capture/validation/finalization ordering is broken",
    )

    reserve_pos = workflow.find("Reserve the one-shot capture before Modal")
    modal_pos = workflow.find(modal_command)
    finalize_pos = workflow.find("Finalize one-shot capture lock")
    require(0 <= reserve_pos < modal_pos < finalize_pos, "lock is not reserved before the paid call")
    require(workflow.find('test "$GITHUB_REF" = "refs/heads/$TARGET_BRANCH"') < reserve_pos, "branch identity gate must run before reservation")
    require(workflow.find('test "$(git rev-parse "origin/$TARGET_BRANCH")" = "$GITHUB_SHA"') < reserve_pos, "remote-head binding gate must run before reservation")
    require(workflow.find('if test -f "$lock"; then') < reserve_pos, "preexisting-lock refusal must run before reservation")

    require(len(PROTECTED.read_bytes()) > 0, "protected pipeline unexpectedly empty")

    print("v143 precision capture readiness checks passed")
    print("paid_modal_commands=1")
    print("producer_remote_calls=1")
    print("reservation_precedes_modal=true")
    print("automatic_retry_allowed=false")
    print("cpu_replay_modal_free=true")
    print("failure_path_artifact_salvage=true")
    print("replay_artifact_exact_binding=true")
    print("source_view_evidence_binding=true")
    print("precision_strength_recompute_binding=true")
    print("zero_value_preservation=true")
    print("primary_recompute_binding=true")
    print("stored_v2_replay_strict=true")
    print("negative_corruption_rejection=true")
    print("replay_capture_order_guarded=true")
    print("fixed_best_row_attack_replay_universe=true")


if __name__ == "__main__":
    main()
