"""Go My Way rhythm timing-map sensitivity diagnostic V1.

Scoring-only, no model execution and no alignment search.

Compare the same frozen raw-guitar Basic Pitch predictions and the same professional
rhythm measures 17..113 under two already-existing timing contracts:
1. professional timing map V2: 133.8 BPM / measure-1 offset 7.1 s, measure boundaries
2. legacy separator-grade grid: 129 BPM / measure-1 start -0.013937331 s

Both are evaluated at the current fixed 50 ms tolerance. A secondary 85 ms result
is reported only because 85 ms was the historical legacy scorer tolerance; it is
not selected as a new threshold.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from score_note_onsets import score_note_onsets

GUITAR_OPEN_MIDI=[64,59,55,50,45,40]
LEGACY_TEMPO=129.0
LEGACY_MEASURE1_START=-0.013937331
CURRENT_TOL=0.05
HISTORICAL_TOL=0.085


def targets_from_reference(reference, timing_kind, timing_map=None):
    out=[]
    beat=60.0/LEGACY_TEMPO
    legacy_measure=beat*4.0
    legacy_step=beat/4.0
    for measure in reference["measures"]:
        m=int(measure["measureNumber"])
        if not 17<=m<=113:
            continue
        if timing_kind=="v2":
            b=timing_map[m]
            mstart=float(b["startSeconds"])
            mdur=float(b["durationSeconds"])
        elif timing_kind=="legacy129":
            mstart=LEGACY_MEASURE1_START+(m-1)*legacy_measure
            mdur=legacy_measure
        else:
            raise ValueError(timing_kind)
        for ei,event in enumerate(measure.get("events",[])):
            step=float(event["quantizedStep"])
            onset=mstart+(step/16.0)*mdur
            for ni,note in enumerate(event.get("notes",[])):
                fret=int(note["fret"])
                if fret<0:
                    continue
                s=int(note["string"])-1
                midi=GUITAR_OPEN_MIDI[s]+fret
                out.append({
                    "id":f"{timing_kind}:m{m}:e{ei}:n{ni}",
                    "midi":midi,
                    "start":onset,
                    "measure":m,
                })
    return out


def transform(rows,mode):
    out=[]
    for r in rows:
        midi=int(r["midi"])
        out.append({
            "id":str(r["id"]),
            "start":float(r["start"]),
            "midi": midi if mode=="exact" else 60,
        })
    return out


def score(pred,targets,tolerance,mode):
    start=max(0.0,min(x["start"] for x in targets)-0.2)
    end=max(x["start"] for x in targets)+2.0
    return {
        k:v for k,v in score_note_onsets(
            transform(pred,mode),transform(targets,mode),
            start=start,end=end,tolerance=tolerance,
        ).items()
        if k!="matches"
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prediction-benchmark",required=True)
    ap.add_argument("--reference",required=True)
    ap.add_argument("--timing-map",required=True)
    ap.add_argument("--output-json",required=True)
    args=ap.parse_args()

    bundle=json.loads(Path(args.prediction_benchmark).read_text())
    reference=json.loads(Path(args.reference).read_text())
    timing=json.loads(Path(args.timing_map).read_text())
    boundaries={int(x["measureNumber"]):x for x in timing["measureBoundaries"]}
    pred=bundle["predictionCache"]["rawGuitarStem"]

    target_sets={
        "professionalTimingV2":targets_from_reference(reference,"v2",boundaries),
        "legacy129ZeroOrigin":targets_from_reference(reference,"legacy129"),
    }
    if len(target_sets["professionalTimingV2"])!=867 or len(target_sets["legacy129ZeroOrigin"])!=867:
        raise RuntimeError("expected 867 pitched targets for measures 17..113")

    results={}
    for name,targets in target_sets.items():
        results[name]={
            "50ms":{
                "exactMidiOnset":score(pred,targets,CURRENT_TOL,"exact"),
                "onsetOnly":score(pred,targets,CURRENT_TOL,"onset"),
            },
            "85msHistoricalContext":{
                "exactMidiOnset":score(pred,targets,HISTORICAL_TOL,"exact"),
                "onsetOnly":score(pred,targets,HISTORICAL_TOL,"onset"),
            },
            "firstTargetSeconds":min(x["start"] for x in targets),
            "lastTargetSeconds":max(x["start"] for x in targets),
        }

    result={
        "schemaVersion":1,
        "kind":"gomyway-rhythm-timing-map-sensitivity-v1",
        "scoringOnly":True,
        "alignmentSearch":False,
        "thresholdSearch":False,
        "professionalTargetCount":867,
        "timingContracts":{
            "professionalTimingV2":{
                "source":"public/gomyway-professional-timing-map-v2.json",
                "resolvedTempoBpm":timing["alignment"]["resolvedTempoBpm"],
                "measure1OffsetSeconds":timing["alignment"]["resolvedFirstMeasureOffsetSeconds"],
            },
            "legacy129ZeroOrigin":{
                "source":"public/gomyway-separator-benchmark-stem-grade-v2.json",
                "tempoBpm":LEGACY_TEMPO,
                "measure1StartSeconds":LEGACY_MEASURE1_START,
                "note":"legacy grid derives from candidate measure labels generated on a 129 BPM zero-origin grid; not independent alignment ground truth",
            },
        },
        "results":results,
        "interpretationBoundary":(
            "This diagnostic compares two pre-existing timing contracts only. It does not choose or optimize "
            "tempo, offset, or tolerance and does not authorize replacing the frozen professional timing map."
        ),
    }
    Path(args.output_json).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
