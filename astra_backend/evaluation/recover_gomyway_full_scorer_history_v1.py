from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROLE_WORDS = ("bass", "lead", "rhythm")
SIGNAL_WORDS = ("reference", "score", "scorer", "label", "ground", "professional")


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, errors="replace")


def blob_text(rev: str, path: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "show", f"{rev}:{path}"],
            text=True,
            errors="replace",
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None


def measure_numbers(obj):
    out = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            lk = str(key).lower()
            if lk in {"measurenumber", "measure", "bar", "barnumber"}:
                if isinstance(value, (int, float)):
                    out.add(int(value))
            out |= measure_numbers(value)
    elif isinstance(obj, list):
        for value in obj:
            out |= measure_numbers(value)
    return out


def roles_in(obj, path: str, raw: str):
    hay = (path + "\n" + raw[:10000]).lower()
    return [role for role in ROLE_WORDS if role in hay]


def coverage_hint(obj, raw: str):
    nums = measure_numbers(obj)
    direct = {}
    if isinstance(obj, dict):
        for key in ("measureStart", "measureEnd", "measureCount", "coverage"):
            if key in obj:
                direct[key] = obj[key]
    text_113 = bool(re.search(r"\b113\b", raw))
    return {
        "minMeasure": min(nums) if nums else None,
        "maxMeasure": max(nums) if nums else None,
        "distinctMeasureCount": len(nums),
        "direct": direct,
        "mentions113": text_113,
        "appearsFull1to113": bool(nums and min(nums) <= 1 and max(nums) >= 113),
    }


def main():
    subprocess.run(["git", "fetch", "origin", "main", "--prune"], check=True)
    subprocess.run(["git", "fetch", "origin", "astra-work", "--prune"], check=True)

    commits = []
    for ref in ("origin/main", "origin/astra-work"):
        commits.extend(run("git", "rev-list", ref).splitlines())
    # Preserve order, newest-ish first across refs.
    commits = list(dict.fromkeys(commits))

    seen_blob = set()
    candidates = []

    for rev in commits:
        names = run("git", "ls-tree", "-r", "--name-only", rev).splitlines()
        for path in names:
            low = path.lower()
            if "gomyway" not in low or not low.endswith(".json"):
                continue
            if not any(word in low for word in SIGNAL_WORDS) and not any(role in low for role in ROLE_WORDS):
                continue

            try:
                blob = run("git", "rev-parse", f"{rev}:{path}").strip()
            except subprocess.CalledProcessError:
                continue
            if blob in seen_blob:
                continue
            seen_blob.add(blob)

            raw = blob_text(rev, path)
            if raw is None or len(raw) > 6_000_000:
                continue
            try:
                obj = json.loads(raw)
            except Exception:
                continue

            roles = roles_in(obj, path, raw)
            cov = coverage_hint(obj, raw)
            if not roles and not cov["mentions113"]:
                continue

            candidates.append({
                "commit": rev,
                "path": path,
                "blob": blob,
                "bytes": len(raw.encode("utf-8", errors="replace")),
                "roles": roles,
                "coverage": cov,
                "topLevelKeys": list(obj.keys())[:40] if isinstance(obj, dict) else [],
            })

    fullish = [
        c for c in candidates
        if c["coverage"]["appearsFull1to113"]
        or (
            c["coverage"]["mentions113"]
            and any(role in c["roles"] for role in ROLE_WORDS)
        )
    ]

    result = {
        "schemaVersion": 1,
        "kind": "gomyway-full-scorer-history-recovery-v1",
        "searchedRefs": ["origin/main", "origin/astra-work"],
        "uniqueJsonBlobsInspected": len(seen_blob),
        "candidateCount": len(candidates),
        "fullCoverageCandidateCount": len(fullish),
        "fullCoverageCandidates": fullish,
        "allCandidates": candidates,
    }
    Path("gomyway_full_scorer_history_recovery_v1.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps({
        "candidateCount": len(candidates),
        "fullCoverageCandidateCount": len(fullish),
        "fullCoverageCandidates": fullish[:100],
    }, indent=2))


if __name__ == "__main__":
    main()
