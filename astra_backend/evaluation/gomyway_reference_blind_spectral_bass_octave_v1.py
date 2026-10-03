"""Reference-blind spectral bass octave discriminator V1.

Uses:
- immutable source audio
- frozen BS-Roformer bass stem
- frozen Basic Pitch bass event times/MIDI
No professional note reference is read during candidate construction.

Only allows a -12 semitone correction when spectral evidence around the event
supports a lower fundamental strongly enough to outweigh the current-octave
hypothesis.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import soundfile as sf

WINDOW_SECONDS=0.12
FFT_SIZE=8192
BASS_RANGE=(28,67)
MIN_MIDI_FOR_SHIFT=40
LOW_TO_CURRENT_MIN=0.28
LOW_HYPOTHESIS_MARGIN=1.20
MIN_ABSOLUTE_LOW_SHARE=0.08

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()

def hz(midi):
    return 440.0*(2.0**((float(midi)-69.0)/12.0))

def band_power(freqs,power,f,frac=0.025,min_hz=3.0):
    width=max(min_hz,f*frac)
    mask=(freqs>=f-width)&(freqs<=f+width)
    if not np.any(mask): return 0.0
    return float(np.sum(power[mask]))

def event_spectrum(stereo,sr,t):
    center=int(round(t*sr))
    half=int(round(WINDOW_SECONDS*sr/2.0))
    a=max(0,center-half); b=min(len(stereo),center+half)
    x=np.mean(stereo[a:b],axis=1) if stereo.ndim==2 else stereo[a:b]
    if len(x)<64: return None,None
    x=x.astype(np.float64)
    x=x-np.mean(x)
    w=np.hanning(len(x))
    z=np.fft.rfft(x*w,n=FFT_SIZE)
    p=(z.real*z.real+z.imag*z.imag)
    f=np.fft.rfftfreq(FFT_SIZE,1.0/sr)
    return f,p

def hypothesis_scores(freqs,power,current_midi):
    fh=hz(current_midi); fl=fh/2.0
    # Lower-note hypothesis: fl fundamental + fh second harmonic + higher partials.
    low_parts=[
      band_power(freqs,power,fl),
      band_power(freqs,power,2*fl),
      band_power(freqs,power,3*fl),
      band_power(freqs,power,4*fl),
    ]
    high_parts=[
      band_power(freqs,power,fh),
      band_power(freqs,power,2*fh),
      band_power(freqs,power,3*fh),
      band_power(freqs,power,4*fh),
    ]
    low_score=low_parts[0]+0.70*low_parts[1]+0.45*low_parts[2]+0.30*low_parts[3]
    high_score=high_parts[0]+0.70*high_parts[1]+0.45*high_parts[2]+0.30*high_parts[3]
    total=float(np.sum(power))+1e-18
    return {
      "lowerFundamentalPower":low_parts[0],
      "currentFundamentalPower":high_parts[0],
      "lowerHypothesisScore":low_score,
      "currentHypothesisScore":high_score,
      "lowerFundamentalShare":low_parts[0]/total,
      "lowToCurrentFundamentalRatio":low_parts[0]/(high_parts[0]+1e-18),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--bass-wav",required=True)
    ap.add_argument("--note-evidence",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()

    ev=json.loads(Path(a.note_evidence).read_text())
    audio,sr=sf.read(a.bass_wav,dtype="float32",always_2d=True)
    bass=ev["predictions"]["bass"]
    out=[];changes=[];diagnostics=[]
    lo,hi=BASS_RANGE
    for p in bass:
        q=dict(p); midi=int(p["midi"]); t=float(p["start"])
        q["originalMidi"]=midi; q["spectralOctaveResolverApplied"]=False
        reason="not-eligible"
        diag={"id":p.get("id"),"start":t,"midi":midi}
        if lo<=midi<=hi and midi>=MIN_MIDI_FOR_SHIFT and midi-12>=lo:
            freqs,power=event_spectrum(audio,sr,t)
            if freqs is not None:
                s=hypothesis_scores(freqs,power,midi); diag.update(s)
                lower_wins=(
                  s["lowToCurrentFundamentalRatio"]>=LOW_TO_CURRENT_MIN and
                  s["lowerHypothesisScore"]>=LOW_HYPOTHESIS_MARGIN*s["currentHypothesisScore"] and
                  s["lowerFundamentalShare"]>=MIN_ABSOLUTE_LOW_SHARE
                )
                if lower_wins:
                    q["midi"]=midi-12
                    q["spectralOctaveResolverApplied"]=True
                    changes.append({
                      "id":p.get("id"),"start":t,"fromMidi":midi,"toMidi":midi-12,**s
                    })
                    reason="lower-spectral-hypothesis-wins"
                else:
                    reason="insufficient-lower-spectral-evidence"
            else:
                reason="insufficient-audio-window"
        diag["reason"]=reason
        q["spectralOctaveEvidence"]=diag
        diagnostics.append(diag); out.append(q)

    result={
      "schemaVersion":1,
      "kind":"gomyway-reference-blind-spectral-bass-octave-discriminator-v1",
      "referenceBlind":True,
      "professionalReferenceRead":False,
      "bassStemSha256":sha(a.bass_wav),
      "noteEvidenceSha256":sha(a.note_evidence),
      "parameters":{
        "windowSeconds":WINDOW_SECONDS,"fftSize":FFT_SIZE,
        "bassMidiRange":BASS_RANGE,"minimumMidiForShift":MIN_MIDI_FOR_SHIFT,
        "allowedShiftSemitones":[-12],
        "lowToCurrentFundamentalRatioMin":LOW_TO_CURRENT_MIN,
        "lowerHypothesisMargin":LOW_HYPOTHESIS_MARGIN,
        "minimumAbsoluteLowerFundamentalShare":MIN_ABSOLUTE_LOW_SHARE
      },
      "predictionCount":len(out),"changeCount":len(changes),
      "changes":changes,"diagnostics":diagnostics,
      "predictions":{"bass":out},
      "interpretationBoundary":"Reference-blind spectral candidate; thresholds fixed before professional scoring."
    }
    Path(a.output_json).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"changeCount":len(changes),"parameters":result["parameters"]},indent=2))

if __name__=="__main__":main()
