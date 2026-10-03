"""Score cached Go My Way full-song predictions against all three professional roles.

This is a scoring-only follow-up. It MUST consume predictions frozen by
Astra Go My Way Full Song Professional Benchmark V1. It never runs a separator
or transcriber and never changes predictions.

References:
- rhythm: 1..16 professional intro fixture + 17..113 human-approved reference
- bass: frozen visual machine-readable 1..113 + frozen source-local attack timing
- lead: frozen visual machine-readable 1..113 + frozen source-local attack timing

Exact-MIDI/onset is primary. Pitch-class/onset and onset-only are descriptive
upper-bound diagnostics. Fixed onset tolerance: 50 ms. No alignment search.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from score_note_onsets import score_note_onsets

ONSET_TOLERANCE_SECONDS = 0.05
GUITAR_OPEN_MIDI = [64, 59, 55, 50, 45, 40]


def expand_intro_reference(intro: dict) -> list[dict]:
    base = intro["notes"]
    source_measures = intro.get("repeat", {}).get("sourceMeasures", [1, 2])
    target_starts = [1] + list(intro.get("repeat", {}).get("targetMeasureStarts", []))
    if source_measures != [1, 2] or target_starts != [1, 3, 5, 7, 9, 11, 13, 15]:
        raise RuntimeError("unexpected intro repeat contract")
    out = []
    for start in target_starts:
        for note in base:
            source_measure = int(note["measure"])
            measure = start + (source_measure - 1)
            string_index = int(note["stringIndex"])
            fret = int(note["fret"])
            out.append({
                "measure": measure,
                "step": float(note["step"]),
                "midi": GUITAR_OPEN_MIDI[string_index] + fret,
                "stringIndex": string_index,
                "fret": fret,
                "source": "intro-fixture-expanded",
            })
    return out


def build_rhythm_reference(intro: dict, later: dict, timing: dict):
    boundaries = {int(x["measureNumber"]): x for x in timing["measureBoundaries"]}
    raw_notes = expand_intro_reference(intro)
    unpitched = []

    if int(later.get("measureStart", -1)) != 17 or int(later.get("measureEnd", -1)) != 113:
        raise RuntimeError("17-113 rhythm reference range mismatch")
    if int(later.get("humanApprovedMeasureCount", -1)) != 97:
        raise RuntimeError("17-113 rhythm reference is not fully human-approved")
    if later.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("professional reference scoring-only boundary missing")

    for measure in later["measures"]:
        m = int(measure["measureNumber"])
        for event_index, event in enumerate(measure.get("events", [])):
            step = float(event["quantizedStep"])
            for note_index, note in enumerate(event.get("notes", [])):
                string_one_based = int(note["string"])
                fret = int(note["fret"])
                common = {
                    "measure": m,
                    "step": step,
                    "stringIndex": string_one_based - 1,
                    "fret": fret,
                    "eventIndex": event_index,
                    "noteIndex": note_index,
                    "source": "human-approved-17-113",
                }
                if fret < 0:
                    unpitched.append(common)
                    continue
                common["midi"] = GUITAR_OPEN_MIDI[string_one_based - 1] + fret
                raw_notes.append(common)

    targets = []
    for index, row in enumerate(raw_notes):
        m = int(row["measure"])
        b = boundaries[m]
        onset = float(b["startSeconds"]) + (float(row["step"]) / 16.0) * float(b["durationSeconds"])
        targets.append({
            "id": f"rhythm:{index}:m{m}:s{row['step']}",
            "midi": int(row["midi"]),
            "start": onset,
            "measure": m,
            "step": row["step"],
            "stringIndex": row["stringIndex"],
            "fret": row["fret"],
            "source": row["source"],
        })
    targets.sort(key=lambda x: (x["start"], x["midi"], x["id"]))
    return targets, unpitched


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def source_measure_length_16ths(time_signature: str) -> int:
    if time_signature == "4/4":
        return 16
    if time_signature == "2/4":
        return 8
    raise RuntimeError(f"unsupported source time signature: {time_signature}")


def build_role_targets(machine: dict, timing_ref: dict, timing_map: dict, role: str):
    measures={int(m["measure"]):m for m in machine["measures"]}
    if set(measures)!=set(range(1,114)):
        raise RuntimeError(f"{role}: machine reference must contain measures 1..113")

    steps_by={int(k):v for k,v in timing_ref["stepsByMeasure"].items()}
    if set(steps_by)!=set(range(1,114)):
        raise RuntimeError(f"{role}: timing reference must contain measures 1..113")

    boundaries={int(x["measureNumber"]):x for x in timing_map["measureBoundaries"]}
    if set(boundaries)!=set(range(1,114)):
        raise RuntimeError("timing map must contain measures 1..113")

    excluded={int(k) for k in (timing_ref.get("policy",{}).get("excludedMeasures",{}) or {})}
    rows=[]
    skipped={
        "excludedMeasurePitchedEvents":0,
        "nullTimingPitchedEvents":0,
        "deadOrUnpitchedEvents":0,
        "continuationOnlyEvents":0,
    }

    for measure_number in range(1,114):
        measure=measures[measure_number]
        events=measure.get("events",[])
        steps=steps_by[measure_number]
        if len(events)!=len(steps):
            raise RuntimeError(
                f"{role} m{measure_number}: event/timing length mismatch "
                f"{len(events)} != {len(steps)}"
            )

        ts=str(measure.get("timeSignature") or (
            "2/4" if measure_number==104 else "4/4"
        ))
        length16=source_measure_length_16ths(ts)
        boundary=boundaries[measure_number]
        start=float(boundary["startSeconds"])
        duration=float(boundary["durationSeconds"])

        for index,(event,step) in enumerate(zip(events,steps)):
            midi=event.get("midi")
            continuation=event.get("continuationOnly") is True
            if continuation:
                skipped["continuationOnlyEvents"]+=1
                if step is not None:
                    raise RuntimeError(
                        f"{role} m{measure_number} event {index}: continuation has attack step"
                    )
                continue
            if not isinstance(midi,int):
                skipped["deadOrUnpitchedEvents"]+=1
                continue
            if measure_number in excluded:
                skipped["excludedMeasurePitchedEvents"]+=1
                continue
            if step is None:
                skipped["nullTimingPitchedEvents"]+=1
                continue
            step=float(step)
            if not 0 <= step < length16:
                raise RuntimeError(
                    f"{role} m{measure_number}: source-local step {step} outside {length16}"
                )

            onset=start+(step/length16)*duration
            rows.append({
                "id":f"{role}:m{measure_number}:e{index}",
                "midi":midi,
                "start":onset,
                "measure":measure_number,
                "sourceLocalStep":step,
                "timeSignature":ts,
                "stringIndex":event.get("stringIndex"),
                "fret":event.get("fret"),
            })

    expected=int(timing_ref["audit"]["expectedPitchedScorerRows"])
    if len(rows)!=expected:
        raise RuntimeError(f"{role}: expected {expected} scorer rows, built {len(rows)}")
    rows.sort(key=lambda x:(x["start"],x["midi"],x["id"]))
    return rows,skipped


def transform_midi(rows,mode):
    out=[]
    for row in rows:
        r={"id":str(row["id"]),"start":float(row["start"])}
        midi=int(row["midi"])
        if mode=="exact":
            r["midi"]=midi
        elif mode=="pitch_class":
            r["midi"]=60+(midi%12)
        elif mode=="onset_only":
            r["midi"]=60
        else:
            raise ValueError(mode)
        out.append(r)
    return out


def compact(score):
    return {k:score[k] for k in (
        "predictions","targets","tp","fp","fn",
        "precision","recall","f1","meanAbsoluteOnsetErrorSeconds",
    )}


def score_modes(predictions,targets,start,end):
    result={}
    for name,mode in (
        ("exactMidiOnset","exact"),
        ("pitchClassOnset","pitch_class"),
        ("onsetOnly","onset_only"),
    ):
        result[name]=compact(score_note_onsets(
            transform_midi(predictions,mode),
            transform_midi(targets,mode),
            start=start,end=end,tolerance=ONSET_TOLERANCE_SECONDS,
        ))
    return result


def per_measure_exact(predictions,targets,timing_map):
    rows=[]
    for b in timing_map["measureBoundaries"]:
        m=int(b["measureNumber"])
        start=float(b["startSeconds"])
        end=float(b["endSeconds"])
        p=[x for x in predictions if start-ONSET_TOLERANCE_SECONDS <= float(x["start"]) < end+ONSET_TOLERANCE_SECONDS]
        t=[x for x in targets if int(x["measure"])==m]
        score=score_note_onsets(
            transform_midi(p,"exact"),
            transform_midi(t,"exact"),
            start=max(0.0,start-ONSET_TOLERANCE_SECONDS),
            end=end+ONSET_TOLERANCE_SECONDS,
            tolerance=ONSET_TOLERANCE_SECONDS,
        )
        rows.append({"measure":m,"referenceCount":len(t),"score":compact(score)})
    return rows


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

    pred_path=Path(args.prediction_benchmark)
    prediction_bundle=json.loads(pred_path.read_text())
    if prediction_bundle.get("kind")!="gomyway-full-song-current-pipeline-professional-benchmark-v1":
        raise RuntimeError("prediction benchmark identity mismatch")
    if prediction_bundle.get("referenceBlindInference") is not True:
        raise RuntimeError("prediction benchmark was not reference-blind inference")
    if prediction_bundle.get("thresholdSearch") is not False:
        raise RuntimeError("prediction benchmark performed threshold search")

    intro=json.loads(Path(args.intro_reference).read_text())
    rhythm=json.loads(Path(args.rhythm_reference).read_text())
    timing=json.loads(Path(args.timing_map).read_text())
    bass=json.loads(Path(args.bass_reference).read_text())
    bass_timing=json.loads(Path(args.bass_timing).read_text())
    lead=json.loads(Path(args.lead_reference).read_text())
    lead_timing=json.loads(Path(args.lead_timing).read_text())

    rhythm_targets,rhythm_unpitched=build_rhythm_reference(intro,rhythm,timing)
    bass_targets,bass_skipped=build_role_targets(bass,bass_timing,timing,"bass")
    lead_targets,lead_skipped=build_role_targets(lead,lead_timing,timing,"lead")

    if len(rhythm_targets)!=971:
        raise RuntimeError(f"expected 971 rhythm pitched targets, got {len(rhythm_targets)}")
    if len(bass_targets)!=547:
        raise RuntimeError(f"expected 547 bass targets, got {len(bass_targets)}")
    if len(lead_targets)!=447:
        raise RuntimeError(f"expected 447 lead targets, got {len(lead_targets)}")

    cache=prediction_bundle["predictionCache"]
    whole=cache["wholeMix"]
    guitar=cache["rawGuitarStem"]
    bass_pred=cache["rawBassStem"]

    start=max(0.0,float(timing["measureBoundaries"][0]["startSeconds"])-0.10)
    end=float(timing["measureBoundaries"][-1]["endSeconds"])+0.10

    roles={
        "rhythm":{
            "predictionStream":"rawGuitarStem",
            "targetCount":len(rhythm_targets),
            "rawRoleStem":score_modes(guitar,rhythm_targets,start,end),
            "wholeMixControl":score_modes(whole,rhythm_targets,start,end),
            "perMeasureExact":per_measure_exact(guitar,rhythm_targets,timing),
        },
        "lead":{
            "predictionStream":"rawGuitarStem",
            "targetCount":len(lead_targets),
            "rawRoleStem":score_modes(guitar,lead_targets,start,end),
            "wholeMixControl":score_modes(whole,lead_targets,start,end),
            "perMeasureExact":per_measure_exact(guitar,lead_targets,timing),
        },
        "bass":{
            "predictionStream":"rawBassStem",
            "targetCount":len(bass_targets),
            "rawRoleStem":score_modes(bass_pred,bass_targets,start,end),
            "wholeMixControl":score_modes(whole,bass_targets,start,end),
            "perMeasureExact":per_measure_exact(bass_pred,bass_targets,timing),
        },
    }

    for role,data in roles.items():
        role_f=data["rawRoleStem"]["exactMidiOnset"]["f1"]
        whole_f=data["wholeMixControl"]["exactMidiOnset"]["f1"]
        data["exactF1DeltaRoleStemVsWholeMix"]=(
            None if role_f is None or whole_f is None else role_f-whole_f
        )

    exact_f1s=[roles[r]["rawRoleStem"]["exactMidiOnset"]["f1"] for r in ("rhythm","lead","bass")]
    macro=sum(float(x) for x in exact_f1s if x is not None)/sum(x is not None for x in exact_f1s)

    result={
        "schemaVersion":1,
        "kind":"gomyway-full-song-three-role-professional-score-v1",
        "benchmarkClass":"existing-reference-development-not-holdout",
        "scoringOnly":True,
        "modelExecution":False,
        "predictionBenchmark":{
            "path":str(pred_path),
            "sha256":sha256_file(pred_path),
            "sourceRunId":37094392537,
            "referenceBlindInference":True,
        },
        "professionalReferenceCoverage":{
            "rhythm":{"measures":[1,113],"pitchedScorerRows":971,"unpitchedRowsExcluded":len(rhythm_unpitched)},
            "bass":{"measures":[1,113],"pitchedScorerRows":547,"skipped":bass_skipped},
            "lead":{"measures":[1,113],"pitchedScorerRows":447,"skipped":lead_skipped},
            "totalPitchedScorerRows":1965,
        },
        "referenceIdentities":{
            "introRhythm":{"path":args.intro_reference,"sha256":sha256_file(Path(args.intro_reference))},
            "rhythm17to113":{"path":args.rhythm_reference,"sha256":sha256_file(Path(args.rhythm_reference))},
            "timingMap":{"path":args.timing_map,"sha256":sha256_file(Path(args.timing_map))},
            "bassMachine":{"path":args.bass_reference,"sha256":sha256_file(Path(args.bass_reference))},
            "bassTiming":{"path":args.bass_timing,"sha256":sha256_file(Path(args.bass_timing))},
            "leadMachine":{"path":args.lead_reference,"sha256":sha256_file(Path(args.lead_reference))},
            "leadTiming":{"path":args.lead_timing,"sha256":sha256_file(Path(args.lead_timing))},
        },
        "scoringContract":{
            "onsetToleranceSeconds":ONSET_TOLERANCE_SECONDS,
            "primaryMetric":"one-to-one exact MIDI + onset",
            "diagnosticMetrics":["pitch-class + onset","onset-only"],
            "alignmentSearch":False,
            "thresholdSearch":False,
            "referenceReadDuringInference":False,
            "sourceMeterTiming":"actual measure boundaries; 4/4=16 source sixteenths, 2/4=8 source sixteenths",
        },
        "roles":roles,
        "threeRoleMacroExactMidiOnsetF1":macro,
        "interpretationBoundary":(
            "Rhythm and lead share the generic raw guitar separator stream; this score does not prove "
            "rhythm-vs-lead role separation. Bass uses the raw bass stream. Professional references are "
            "scoring-only and this remains development evidence, not a sealed holdout or production gate."
        ),
    }

    Path(args.output_json).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({
        "coverage":result["professionalReferenceCoverage"],
        "threeRoleMacroExactMidiOnsetF1":macro,
        "roleSummary":{
            role:{
                "targets":data["targetCount"],
                "rawExact":data["rawRoleStem"]["exactMidiOnset"],
                "rawPitchClass":data["rawRoleStem"]["pitchClassOnset"],
                "rawOnsetOnly":data["rawRoleStem"]["onsetOnly"],
                "wholeExact":data["wholeMixControl"]["exactMidiOnset"],
                "deltaExact":data["exactF1DeltaRoleStemVsWholeMix"],
            }
            for role,data in roles.items()
        },
    },indent=2))


if __name__=="__main__":
    main()
