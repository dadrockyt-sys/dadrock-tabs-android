from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/v143-repaired-timing-precision-candidate-product.yml"
PRODUCER = ROOT / "analyzer/v143_repaired_timing_precision_candidate_product_modal.py"
REPLAY = ROOT / "analyzer/v143_precision_replay_policy_compare.py"
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
    workflow = WORKFLOW.read_text(encoding="utf-8")
    producer = PRODUCER.read_text(encoding="utf-8")
    replay = REPLAY.read_text(encoding="utf-8")

    require(TARGET_BRANCH in workflow, "target branch missing from workflow")
    require(f"refs/heads/{TARGET_BRANCH}" in workflow, "workflow dispatch ref is not pinned to target branch")
    require("GITHUB_SHA" in workflow and "origin/$TARGET_BRANCH" in workflow, "dispatch SHA is not bound to remote target head")
    require(PROTECTED_BLOB in workflow, "protected pipeline blob guard missing")
    require(APPROVED_AUDIO_SHA256 in workflow, "approved fixture SHA guard missing")
    require(LOCK_PATH in workflow, "one-shot lock path missing")
    require("automaticRetryAllowed" in workflow, "reservation does not explicitly prohibit automatic retry")
    require("reserved_before_modal" in workflow, "pre-Modal reservation state missing")
    require("singlePaidCaptureConsumed" in workflow, "capture-consumption state missing")

    modal_command = "python -m modal run analyzer/v143_repaired_timing_precision_candidate_product_modal.py::approved_audio"
    require(workflow.count(modal_command) == 1, "workflow must contain exactly one paid Modal command")
    require(producer.count(".remote(") == 1, "producer must contain exactly one Modal .remote call")
    require("precisionReplayEvidence" in producer and "build_replay_evidence(" in producer, "producer replay evidence persistence missing")
    require("import modal" not in replay and ".remote(" not in replay and "modal run" not in replay, "CPU replay path contains Modal usage")

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
            "Build CPU replay policy comparison",
            "Finalize one-shot capture lock",
        ),
        "required pre-reservation/capture/finalization ordering is broken",
    )

    reserve_pos = workflow.find("Reserve the one-shot capture before Modal")
    modal_pos = workflow.find(modal_command)
    finalize_pos = workflow.find("Finalize one-shot capture lock")
    require(0 <= reserve_pos < modal_pos < finalize_pos, "lock is not reserved before the paid call")
    require(
        workflow.find('test "$GITHUB_REF" = "refs/heads/$TARGET_BRANCH"') < reserve_pos,
        "branch identity gate must run before reservation",
    )
    require(
        workflow.find('test "$(git rev-parse "origin/$TARGET_BRANCH")" = "$GITHUB_SHA"') < reserve_pos,
        "remote-head binding gate must run before reservation",
    )
    require(
        workflow.find('if test -f "$lock"; then') < reserve_pos,
        "preexisting-lock refusal must run before reservation",
    )

    protected_bytes = PROTECTED.read_bytes()
    require(len(protected_bytes) > 0, "protected pipeline unexpectedly empty")

    print("v143 precision capture readiness checks passed")
    print("paid_modal_commands=1")
    print("producer_remote_calls=1")
    print("reservation_precedes_modal=true")
    print("automatic_retry_allowed=false")
    print("cpu_replay_modal_free=true")


if __name__ == "__main__":
    main()
