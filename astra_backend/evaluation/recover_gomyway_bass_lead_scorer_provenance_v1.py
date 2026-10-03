from __future__ import annotations

import json
import subprocess
from pathlib import Path

NEEDLES = {
    "bass_pdf_sha256": "18e6822394980d22a960a1bd4d923aaddf677f3341b8cc1a2dbb29ea1e8771d0",
    "lead_pdf_sha256": "a11a2c04fdda73e667df16df99aedf9ae0a3ed7af85f62f3c1773b7784a97f56",
    "bass_old_set_sha256": "abd1748066966ceb93fe40bf8c8df3168f6c871ba006e44d28f8840184e3cde3",
    "lead_old_set_sha256": "de2f20c330e52aca6125e29ca2cf5c4b719406fc267a98d43d98f3ab1453ff3c",
    "bass_first_filename": "1000120296.jpg",
    "bass_last_filename": "1000120330.jpg",
    "lead_first_filename": "1000120332.jpg",
    "lead_last_filename": "1000120374.jpg",
}


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, errors="replace")


def main():
    subprocess.run(["git","fetch","origin","--prune"],check=True)
    results={}
    for name,needle in NEEDLES.items():
        cmd=["git","log","--all","--full-history","-S",needle,"--pretty=format:COMMIT %H","--name-only"]
        try:
            raw=run(*cmd)
        except subprocess.CalledProcessError:
            raw=""
        entries=[]
        current=None
        for line in raw.splitlines():
            if line.startswith("COMMIT "):
                current={"commit":line.split(" ",1)[1],"paths":[]}
                entries.append(current)
            elif line.strip() and current is not None:
                current["paths"].append(line.strip())
        results[name]={"needle":needle,"historyHits":entries}

    # Also scan all reachable text JSON blobs for literals even if Git's -S history
    # does not expose a convenient path transition.
    objects=run("git","rev-list","--objects","--all").splitlines()
    blob_paths={}
    for line in objects:
        parts=line.split(" ",1)
        if len(parts)==2 and parts[1].lower().endswith((".json",".md",".txt",".py",".js",".mjs")):
            blob_paths.setdefault(parts[0],set()).add(parts[1])

    content_hits={name:[] for name in NEEDLES}
    for blob,paths in blob_paths.items():
        try:
            size=int(run("git","cat-file","-s",blob).strip())
        except Exception:
            continue
        if size>5_000_000:
            continue
        try:
            raw=subprocess.check_output(["git","cat-file","-p",blob],text=True,errors="replace")
        except Exception:
            continue
        for name,needle in NEEDLES.items():
            if needle in raw:
                content_hits[name].append({
                    "blob":blob,
                    "paths":sorted(paths)[:50],
                    "bytes":size,
                })

    result={
        "schemaVersion":1,
        "kind":"gomyway-bass-lead-scorer-provenance-history-recovery-v1",
        "needleResults":results,
        "reachableContentHits":content_hits,
    }
    Path("gomyway_bass_lead_scorer_provenance_recovery_v1.json").write_text(
        json.dumps(result,indent=2)+"\n"
    )
    print(json.dumps({
        name:{
            "gitLogHits":len(results[name]["historyHits"]),
            "contentHits":len(content_hits[name]),
            "paths":sorted({p for hit in content_hits[name] for p in hit["paths"]})[:100],
        }
        for name in NEEDLES
    },indent=2))


if __name__=="__main__":
    main()
