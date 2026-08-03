from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "public" / "training" / "gomyway-rhythm-17-113-v2"
V3 = ROOT / "public" / "training" / "gomyway-rhythm-17-113-v3"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    V3.mkdir(parents=True, exist_ok=True)
    seed = None
    if (V3 / "best.json").exists():
        seed = load(V3 / "best.json")
    elif (V2 / "best.json").exists():
        seed = load(V2 / "best.json")
        write(V3 / "seed-from-v2.json", seed)
        if seed.get("candidateEvents"):
            write(V3 / "best-renderer-events.json", {
                "source": "generation-2-best-seed",
                "candidateEvents": seed["candidateEvents"],
                "promotionAllowed": False,
            })
    state_path = V3 / "generation-state.json"
    state = load(state_path) if state_path.exists() else {
        "generation": 1,
        "consecutiveStalledGenerations": 0,
        "lastBestCompositePercent": float(seed.get("compositePercent", 0.0)) if seed else 0.0,
        "targetCompositePercent": 90.0,
        "targetReached": False,
        "stalled": False,
    }
    write(state_path, state)
    print("Generation 3 state prepared")
    print("Seed available:", bool(seed))
    print("Starting best:", state["lastBestCompositePercent"])
    print("Target:", state["targetCompositePercent"])


if __name__ == "__main__":
    main()
