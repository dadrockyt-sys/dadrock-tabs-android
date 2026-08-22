from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "analyzer" / "training_profiles" / "rhythm-guitar-reference.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def composite(result: dict[str, Any], profile: dict[str, Any]) -> float:
    scores = result.get("categoryScoresPercent", {})
    return round(sum(float(scores.get(key, 0.0)) * float(weight) for key, weight in profile["weights"].items()), 6)


def categories_pass(result: dict[str, Any], profile: dict[str, Any]) -> bool:
    scores = result.get("categoryScoresPercent", {})
    return all(float(scores.get(key, 0.0)) >= float(minimum) for key, minimum in profile["minimumCategoryPercent"].items())


def heartbeat(stop: threading.Event, status_path: Path, seconds: int) -> None:
    while not stop.wait(max(10, seconds)):
        status = load(status_path) if status_path.exists() else {}
        status["lastHeartbeatAt"] = now()
        write(status_path, status)
        print(f"HEARTBEAT {status['lastHeartbeatAt']} attempt={status.get('currentAttempt')} best={status.get('bestCompositePercent')}", flush=True)


def git_checkpoint(attempt: int, profile: dict[str, Any]) -> None:
    if not (ROOT / ".git").exists() or os.environ.get("GOMYWAY_PUSH_CHECKPOINTS", "0") != "1":
        return
    checkpoint_root = str(Path(profile["checkpointDirectory"]).parent)
    subprocess.run(["git", "add", checkpoint_root], cwd=ROOT, check=True)
    changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode != 0
    if not changed:
        return
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], cwd=ROOT, check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", f"Checkpoint Gomyway adaptive rhythm attempt {attempt}"], cwd=ROOT, check=True)
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "jimmy-paige-v8-section-detection"], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", "HEAD:jimmy-paige-v8-section-detection"], cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-attempts", type=int, default=192, help="Additional attempts in this runner generation")
    parser.add_argument("--max-hours", type=float, default=5.5)
    parser.add_argument("--stall-generations", type=int, default=3)
    parser.add_argument("--minimum-generation-improvement", type=float, default=0.05)
    args = parser.parse_args()

    profile = load(PROFILE)
    checkpoint_dir = ROOT / profile["checkpointDirectory"]
    current_path = ROOT / profile["attemptResultPath"]
    best_path = ROOT / profile["bestCheckpointPath"]
    status_path = ROOT / profile["statusPath"]
    summary_path = ROOT / profile["summaryPath"]
    state_path = checkpoint_dir.parent / "generation-state.json"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    state = load(state_path) if state_path.exists() else {
        "generation": 1,
        "consecutiveStalledGenerations": 0,
        "lastBestCompositePercent": 0.0,
        "targetReached": False,
        "stalled": False,
    }
    generation = int(state.get("generation", 1))
    existing = sorted(checkpoint_dir.glob("attempt-*.json"))
    completed = len(existing)
    stop_after = completed + max(1, args.max_attempts)
    best = load(best_path) if best_path.exists() else None
    best_score = float(best.get("compositePercent", -1.0)) if best else -1.0
    generation_start_best = max(float(state.get("lastBestCompositePercent", 0.0)), best_score)
    target = float(profile["targetCompositePercent"])
    started = time.monotonic()

    status = {
        "status": "running",
        "generation": generation,
        "startedAt": now(),
        "lastHeartbeatAt": now(),
        "resumeFromCompletedAttempts": completed,
        "generationStopAfterAttempt": stop_after,
        "currentAttempt": completed,
        "bestCompositePercent": max(0.0, best_score),
        "targetCompositePercent": target,
        "protectedRules": profile["protectedRules"],
    }
    write(status_path, status)
    stop = threading.Event()
    thread = threading.Thread(target=heartbeat, args=(stop, status_path, int(profile.get("heartbeatSeconds", 60))), daemon=True)
    thread.start()

    command = str(profile.get("attemptCommand", "python analyzer/run_gomyway_rhythm_training_attempt_v3.py")).split()
    try:
        while completed < stop_after and (time.monotonic() - started) < args.max_hours * 3600:
            attempt = completed + 1
            status.update({"currentAttempt": attempt, "attemptStartedAt": now(), "lastHeartbeatAt": now()})
            write(status_path, status)
            print(f"GENERATION {generation} ATTEMPT {attempt} START {status['attemptStartedAt']}", flush=True)
            subprocess.run(command, cwd=ROOT, check=True)
            result = load(current_path)
            result["compositePercent"] = composite(result, profile)
            result["minimumCategoriesPassed"] = categories_pass(result, profile)
            result["targetReached"] = result["compositePercent"] >= target and result["minimumCategoriesPassed"]
            result["completedAt"] = now()
            result["generation"] = generation
            checkpoint = checkpoint_dir / f"attempt-{attempt:06d}.json"
            write(checkpoint, result)
            completed = attempt

            if result["compositePercent"] > best_score:
                best_score = result["compositePercent"]
                best = result
                write(best_path, best)
                if result.get("candidateEvents"):
                    write(checkpoint_dir.parent / "best-renderer-events.json", {
                        "sourceAttempt": attempt,
                        "generation": generation,
                        "compositePercent": best_score,
                        "candidateEvents": result["candidateEvents"],
                        "promotionAllowed": False,
                    })
                print(f"NEW BEST {best_score:.3f}% at attempt {attempt}", flush=True)

            status.update({
                "completedAttempts": completed,
                "bestCompositePercent": max(0.0, best_score),
                "lastAttemptCompositePercent": result["compositePercent"],
                "lastAttemptCompletedAt": result["completedAt"],
                "lastHeartbeatAt": now(),
            })
            write(status_path, status)
            git_checkpoint(attempt, profile)
            print(f"ATTEMPT {attempt} SAVED composite={result['compositePercent']:.3f}% target={result['targetReached']}", flush=True)
            if result["targetReached"]:
                status["status"] = "target-reached"
                break
        else:
            status["status"] = "generation-limit-reached"
    finally:
        stop.set()
        thread.join(timeout=2)

    improvement = max(0.0, best_score - generation_start_best)
    stalled_count = int(state.get("consecutiveStalledGenerations", 0))
    stalled_count = stalled_count + 1 if improvement < args.minimum_generation_improvement else 0
    target_reached = bool(best and best.get("targetReached"))
    stalled = not target_reached and stalled_count >= args.stall_generations
    state.update({
        "generation": generation + 1,
        "completedAttempts": completed,
        "lastGenerationImprovement": round(improvement, 6),
        "lastBestCompositePercent": max(0.0, best_score),
        "consecutiveStalledGenerations": stalled_count,
        "targetCompositePercent": target,
        "targetReached": target_reached,
        "stalled": stalled,
        "continueRequested": not target_reached and not stalled,
        "updatedAt": now(),
    })
    write(state_path, state)

    status["finishedAt"] = now()
    status["lastHeartbeatAt"] = now()
    status["stalled"] = stalled
    write(status_path, status)
    summary = {
        "status": "target-reached" if target_reached else ("stalled" if stalled else status["status"]),
        "generation": generation,
        "startedAt": status["startedAt"],
        "finishedAt": status["finishedAt"],
        "completedAttempts": completed,
        "generationImprovementPercent": round(improvement, 6),
        "consecutiveStalledGenerations": stalled_count,
        "bestCompositePercent": max(0.0, best_score),
        "targetCompositePercent": target,
        "targetReached": target_reached,
        "continueRequested": not target_reached and not stalled,
        "bestAttempt": best.get("attempt") if best else None,
        "bestParameters": best.get("parameters") if best else None,
        "bestCategoryScoresPercent": best.get("categoryScoresPercent") if best else None,
        "protectedRules": profile["protectedRules"],
    }
    write(summary_path, summary)
    print("AUTONOMOUS GENERATION COMPLETE", flush=True)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
