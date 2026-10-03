"""Audit the preserved Go My Way professional timing map against immutable source identity.

This is not candidate generation and does not alter any frozen timebase.
It tests internal consistency of the professional map and its alignment provenance.
"""
from __future__ import annotations
import argparse, json, subprocess, hashlib
from pathlib import Path

def sha256(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def ffprobe_duration(path):
    out=subprocess.check_output([
        "ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(path)
    ],text=True).strip()
    return float(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--audio",required=True)
    ap.add_argument("--timing-map",required=True)
    ap.add_argument("--alignment-diagnosis",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()

    audio=Path(a.audio)
    tm=json.loads(Path(a.timing_map).read_text())
    diag=json.loads(Path(a.alignment_diagnosis).read_text())
    bounds=tm["measureBoundaries"]
    quarter_beats=sum(int(r["meter"]["numerator"]) for r in bounds)
    first=float(bounds[0]["startSeconds"])
    last=float(bounds[-1]["endSeconds"])
    mapped_span=last-first
    base=float(tm["baseTempoBpm"])
    resolved=float(tm["alignment"]["resolvedTempoBpm"])
    base_span=quarter_beats*60.0/base
    resolved_span=quarter_beats*60.0/resolved
    audio_duration=ffprobe_duration(audio)

    result={
      "kind":"gomyway-professional-timing-map-integrity-audit-v1",
      "audio":{"path":str(audio),"sha256":sha256(audio),"durationSeconds":audio_duration},
      "timingMap":{
        "sha256":sha256(a.timing_map),
        "baseTempoBpm":base,
        "resolvedTempoBpm":resolved,
        "firstMeasureOffsetSeconds":first,
        "lastMeasureEndSeconds":last,
        "mappedSpanSeconds":mapped_span,
        "quarterBeatCountFromMeters":quarter_beats,
        "spanIfBaseTempoSeconds":base_span,
        "spanIfResolvedTempoSeconds":resolved_span,
        "baseTempoEndSeconds":first+base_span,
        "resolvedTempoEndSeconds":first+resolved_span,
        "audioTailAfterMappedEndSeconds":audio_duration-last,
        "audioTailAfterBaseTempoEndSeconds":audio_duration-(first+base_span),
      },
      "alignmentDiagnosis":{
        "sha256":sha256(a.alignment_diagnosis),
        "eventCount":diag.get("eventCount"),
        "bestTempoBpm":diag.get("best",{}).get("tempo"),
        "bestOffsetSeconds":diag.get("best",{}).get("offsetSeconds"),
        "bestCorrectCandidateSlots":diag.get("best",{}).get("correctCandidateSlots"),
        "bestTotalMatchingOccurrences":diag.get("best",{}).get("totalMatchingOccurrences"),
        "searchTempoRangeBpm":diag.get("search",{}).get("tempoRangeBpm"),
        "searchTempoStepBpm":diag.get("search",{}).get("tempoStepBpm"),
        "searchToleranceSeconds":diag.get("search",{}).get("toleranceSeconds"),
        "productionPromotionAllowed":diag.get("productionPromotionAllowed"),
      },
      "mapMetadata":{
        "performanceDriftCorrection":tm.get("measureBoundaryGeneration",{}).get("performanceDriftCorrection"),
        "manualAnchorMeasures":tm.get("measureBoundaryGeneration",{}).get("manualAnchorMeasures"),
        "productionPromotionAllowed":tm.get("productionPromotionAllowed"),
        "protectedReference":tm.get("protectedReference"),
      },
      "derived":{
        "resolvedMinusBaseBpm":resolved-base,
        "baseVsResolvedSpanDifferenceSeconds":base_span-resolved_span,
        "mapSpanMatchesResolvedTempoSeconds":mapped_span-resolved_span,
        "mapSpanMatchesBaseTempoSeconds":mapped_span-base_span
      },
      "interpretationBoundary":"Audit only. Does not modify the professional reference or any frozen candidate."
    }
    Path(a.output_json).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
