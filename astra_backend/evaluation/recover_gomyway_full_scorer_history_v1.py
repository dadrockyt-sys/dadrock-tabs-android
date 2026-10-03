from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROLE_WORDS = ("bass", "lead", "rhythm")
SIGNAL_WORDS = ("reference", "score", "scorer", "label", "ground", "professional")


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, errors="replace")


def cat_blob(blob: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "cat-file", "-p", blob],
            text=True,
            errors="replace",
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None


def measure_numbers(obj):
    out=set()
    if isinstance(obj,dict):
        for key,value in obj.items():
            lk=str(key).lower()
            if lk in {"measurenumber","measure","bar","barnumber"} and isinstance(value,(int,float)):
                out.add(int(value))
            out |= measure_numbers(value)
    elif isinstance(obj,list):
        for value in obj:
            out |= measure_numbers(value)
    return out


def coverage_hint(obj,raw):
    nums=measure_numbers(obj)
    direct={}
    if isinstance(obj,dict):
        for key in (
            "measureStart","measureEnd","measureCount","coverage",
            "measures","measureRange","humanApprovedMeasureCount"
        ):
            if key in obj and key!="measures":
                direct[key]=obj[key]
    return {
        "minMeasure": min(nums) if nums else None,
        "maxMeasure": max(nums) if nums else None,
        "distinctMeasureCount": len(nums),
        "direct": direct,
        "mentions113": bool(re.search(r"\b113\b",raw)),
        "appearsFull1to113": bool(nums and min(nums)<=1 and max(nums)>=113),
    }


def roles_in(path,raw):
    hay=(path+"\n"+raw[:20000]).lower()
    return [role for role in ROLE_WORDS if role in hay]


def main():
    subprocess.run(["git","fetch","origin","main","astra-work","--prune"],check=True)

    # One pass over reachable object identities. A blob may have multiple historical paths;
    # preserve each relevant path but inspect blob content only once.
    objects=run("git","rev-list","--objects","--all").splitlines()
    relevant=[]
    for line in objects:
        parts=line.split(" ",1)
        if len(parts)!=2:
            continue
        blob,path=parts
        low=path.lower()
        if "gomyway" not in low or not low.endswith(".json"):
            continue
        if not any(w in low for w in SIGNAL_WORDS) and not any(r in low for r in ROLE_WORDS):
            continue
        relevant.append((blob,path))

    cache={}
    candidates=[]
    seen_pairs=set()
    for blob,path in relevant:
        key=(blob,path)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)

        if blob not in cache:
            raw=cat_blob(blob)
            if raw is None or len(raw)>6_000_000:
                cache[blob]=None
            else:
                try:
                    cache[blob]=(raw,json.loads(raw))
                except Exception:
                    cache[blob]=None
        item=cache[blob]
        if item is None:
            continue
        raw,obj=item
        roles=roles_in(path,raw)
        cov=coverage_hint(obj,raw)
        if not roles and not cov["mentions113"]:
            continue
        candidates.append({
            "path":path,
            "blob":blob,
            "bytes":len(raw.encode("utf-8",errors="replace")),
            "roles":roles,
            "coverage":cov,
            "topLevelKeys":list(obj.keys())[:50] if isinstance(obj,dict) else [],
        })

    fullish=[
        c for c in candidates
        if c["coverage"]["appearsFull1to113"]
        or (
            c["coverage"]["mentions113"]
            and any(role in c["roles"] for role in ROLE_WORDS)
            and (
                c["coverage"]["direct"].get("measureEnd")==113
                or c["coverage"]["direct"].get("measureCount")==113
                or c["coverage"]["direct"].get("coverage")==[1,113]
                or c["coverage"]["direct"].get("measureRange")==[1,113]
            )
        )
    ]

    # Deduplicate identical blob/path summaries and favor concise output.
    fullish.sort(key=lambda c:(c["path"],c["blob"]))
    candidates.sort(key=lambda c:(c["path"],c["blob"]))

    result={
        "schemaVersion":1,
        "kind":"gomyway-full-scorer-history-recovery-v1",
        "searchedRefs":["origin/main","origin/astra-work","all-reachable-git-objects"],
        "reachableObjects":len(objects),
        "relevantHistoricalJsonPaths":len(relevant),
        "uniqueJsonBlobsInspected":sum(v is not None for v in cache.values()),
        "candidateCount":len(candidates),
        "fullCoverageCandidateCount":len(fullish),
        "fullCoverageCandidates":fullish,
        "allCandidates":candidates,
    }
    Path("gomyway_full_scorer_history_recovery_v1.json").write_text(
        json.dumps(result,indent=2)+"\n"
    )
    print(json.dumps({
        "reachableObjects":len(objects),
        "relevantHistoricalJsonPaths":len(relevant),
        "candidateCount":len(candidates),
        "fullCoverageCandidateCount":len(fullish),
        "fullCoverageCandidates":fullish[:100],
    },indent=2))


if __name__=="__main__":
    main()
