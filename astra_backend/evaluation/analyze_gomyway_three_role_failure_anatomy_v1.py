"""Go My Way professional three-role failure anatomy V1.

Reference-centered descriptive analysis over frozen cached predictions.
No inference, no threshold search, no prediction mutation.

For each professional target, inspect predictions within the fixed 50 ms onset
window and classify candidate availability:
- exact MIDI available
- same pitch class but wrong octave
- near pitch (+/-1 or 2 semitones)
- fourth/fifth-class harmonic relation
- other wrong pitch only
- no prediction near the onset

This is NOT a replacement for the one-to-one F1 scorer because one prediction may
be locally available to multiple simultaneous chord targets. It is an error-anatomy
diagnostic only.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

from score_gomyway_full_song_three_role_v1 import (
    ONSET_TOLERANCE_SECONDS,
    build_rhythm_reference,
    build_role_targets,
)

SECTIONS=[
    ("Intro",1,16),
    ("Verse 1",17,32),
    ("Chorus 1",33,38),
    ("Riff 1",39,46),
    ("Verse 2",47,62),
    ("Chorus 2",63,69),
    ("Bridge",70,77),
    ("Solo / transition",78,94),
    ("Riff 2",95,102),
    ("Out-chorus / ending",103,113),
]


def section_for(measure):
    for name,a,b in SECTIONS:
        if a<=measure<=b:
            return name
    raise RuntimeError(measure)


def percentile(values,q):
    if not values:
        return None
    x=sorted(values)
    if len(x)==1:
        return float(x[0])
    pos=(len(x)-1)*q
    lo=int(pos); hi=min(len(x)-1,lo+1); f=pos-lo
    return float(x[lo]*(1-f)+x[hi]*f)


def register_summary(rows):
    midis=[int(x["midi"]) for x in rows]
    return {
        "count":len(midis),
        "min":min(midis) if midis else None,
        "p10":percentile(midis,0.10),
        "median":percentile(midis,0.50),
        "p90":percentile(midis,0.90),
        "max":max(midis) if midis else None,
    }


def category_for(target,candidates):
    if not candidates:
        return "no_prediction_within_50ms",None,None
    tm=int(target["midi"])
    deltas=[int(p["midi"])-tm for p in candidates]
    if 0 in deltas:
        return "exact_midi_available",0,0
    octave=[d for d in deltas if d!=0 and abs(d)%12==0]
    if octave:
        d=min(octave,key=lambda x:(abs(x),x))
        return "same_pitch_class_wrong_octave",d,abs(d)
    near=[d for d in deltas if 0<abs(d)<=2]
    if near:
        d=min(near,key=lambda x:(abs(x),x))
        return "near_pitch_1_2_semitones",d,abs(d)
    harmonic=[d for d in deltas if abs(d)%12 in (5,7)]
    if harmonic:
        d=min(harmonic,key=lambda x:(abs(x),x))
        return "fourth_fifth_class_relation",d,abs(d)
    d=min(deltas,key=lambda x:(abs(x),x))
    return "other_wrong_pitch_only",d,abs(d)


def analyze_role(predictions,targets):
    counts=collections.Counter()
    delta_hist=collections.Counter()
    examples={k:[] for k in (
        "same_pitch_class_wrong_octave",
        "near_pitch_1_2_semitones",
        "fourth_fifth_class_relation",
        "other_wrong_pitch_only",
        "no_prediction_within_50ms",
    )}
    section_counts={name:collections.Counter() for name,_,_ in SECTIONS}

    for target in targets:
        candidates=[
            p for p in predictions
            if abs(float(p["start"])-float(target["start"]))<=ONSET_TOLERANCE_SECONDS
        ]
        category,delta,_=category_for(target,candidates)
        counts[category]+=1
        section_counts[section_for(int(target["measure"]))][category]+=1
        if delta is not None:
            delta_hist[delta]+=1
        if category in examples and len(examples[category])<10:
            examples[category].append({
                "measure":int(target["measure"]),
                "targetMidi":int(target["midi"]),
                "targetStart":float(target["start"]),
                "candidateMidis":sorted({int(p["midi"]) for p in candidates}),
                "nearestDelta":delta,
            })

    total=len(targets)
    section_rows=[]
    for name,a,b in SECTIONS:
        c=section_counts[name]
        n=sum(c.values())
        section_rows.append({
            "section":name,"measureRange":[a,b],"targetCount":n,
            "categories":dict(c),
            "exactAvailabilityRate":c["exact_midi_available"]/n if n else None,
            "anyOnsetCandidateRate":1-(c["no_prediction_within_50ms"]/n) if n else None,
        })

    return {
        "targetCount":total,
        "categories":dict(counts),
        "rates":{k:v/total for k,v in counts.items()},
        "nearestPitchDeltaHistogram":{
            str(k):v for k,v in sorted(delta_hist.items(),key=lambda x:(-x[1],abs(x[0]),x[0]))
        },
        "topNearestPitchDeltas":[
            {"semitones":k,"count":v,"fractionOfTargets":v/total}
            for k,v in delta_hist.most_common(20)
        ],
        "sectionBreakdown":section_rows,
        "examples":examples,
        "referenceRegister":register_summary(targets),
        "predictionRegister":register_summary(predictions),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prediction-benchmark",required=True)
    ap.add_argument("--intro-reference",required=True)
    ap.add_argument("--rhythm-reference",required=True)
    ap.add_argument("--timing-map",required=True)
    ap.add_argument("--bass-reference",required=True)
    ap.add_argument("--bass-timing",required=True)
    ap.add_argument("--lead-reference",required=True)
    ap.add_argument("--lead-timing",required=True)
    ap.add_argument("--output-json",required=True)
    args=ap.parse_args()

    bundle=json.loads(Path(args.prediction_benchmark).read_text())
    if bundle.get("kind")!="gomyway-full-song-current-pipeline-professional-benchmark-v1":
        raise RuntimeError("frozen prediction bundle identity mismatch")

    intro=json.loads(Path(args.intro_reference).read_text())
    rhythm=json.loads(Path(args.rhythm_reference).read_text())
    timing=json.loads(Path(args.timing_map).read_text())
    bass=json.loads(Path(args.bass_reference).read_text())
    bass_timing=json.loads(Path(args.bass_timing).read_text())
    lead=json.loads(Path(args.lead_reference).read_text())
    lead_timing=json.loads(Path(args.lead_timing).read_text())

    rhythm_targets,_=build_rhythm_reference(intro,rhythm,timing)
    bass_targets,_=build_role_targets(bass,bass_timing,timing,"bass")
    lead_targets,_=build_role_targets(lead,lead_timing,timing,"lead")
    if (len(rhythm_targets),len(bass_targets),len(lead_targets))!=(971,547,447):
        raise RuntimeError("professional target identity/count mismatch")

    cache=bundle["predictionCache"]
    roles={
        "rhythm":analyze_role(cache["rawGuitarStem"],rhythm_targets),
        "lead":analyze_role(cache["rawGuitarStem"],lead_targets),
        "bass":analyze_role(cache["rawBassStem"],bass_targets),
    }

    total_targets=sum(x["targetCount"] for x in roles.values())
    aggregate=collections.Counter()
    for x in roles.values():
        aggregate.update(x["categories"])

    result={
        "schemaVersion":1,
        "kind":"gomyway-three-role-professional-failure-anatomy-v1",
        "benchmarkClass":"existing-reference-development-not-holdout",
        "scoringOnly":True,
        "modelExecution":False,
        "predictionMutation":False,
        "onsetWindowSeconds":ONSET_TOLERANCE_SECONDS,
        "targetCount":total_targets,
        "aggregateCategories":dict(aggregate),
        "aggregateRates":{k:v/total_targets for k,v in aggregate.items()},
        "roles":roles,
        "interpretationBoundary":(
            "Reference-centered candidate availability is diagnostic, not one-to-one scoring. "
            "One prediction may be available to multiple simultaneous chord targets. "
            "Use the separate frozen three-role F1 result for accuracy claims."
        ),
    }
    Path(args.output_json).write_text(json.dumps(result,indent=2)+"\n")

    print(json.dumps({
        "targetCount":total_targets,
        "aggregateCategories":result["aggregateCategories"],
        "aggregateRates":result["aggregateRates"],
        "roles":{
            role:{
                "targetCount":x["targetCount"],
                "categories":x["categories"],
                "rates":x["rates"],
                "referenceRegister":x["referenceRegister"],
                "predictionRegister":x["predictionRegister"],
                "topNearestPitchDeltas":x["topNearestPitchDeltas"][:10],
            }
            for role,x in roles.items()
        },
    },indent=2))


if __name__=="__main__":
    main()
