from __future__ import annotations

import numpy as np

from guitartechs_training_v4.objective_decoder import (
    NUM_CLASSES, NUM_FRETS, NUM_STRINGS, SILENCE_CLASS,
    decode_with_hysteresis,
)
from guitartechs_training_v7.objective_decoder import local_event_maxima

BACKSHIFT_RADIUS_FRAMES = 2

def _runs(states):
    out=[];i=0
    while i<len(states):
        v=int(states[i]);j=i+1
        while j<len(states) and int(states[j])==v:j+=1
        out.append((i,j,v));i=j
    return out

def decode_v8_hybrid(state_probabilities, event_scores):
    """
    Conservative V8 decoder.

    1. Frozen V4 hysteresis is the sole admission/continuation scaffold.
    2. V7 event rank may only move an already-admitted active run start earlier
       by <=2 frames.
    3. A backshift frame is eligible only when:
       - it is the deterministic local event maximum;
       - the same fret as the admitted run is the relative state argmax;
       - that fret outranks silence.
    4. No new active run can be created and no V4-admitted run can be deleted.
    5. Raw event scores are used only by rank, so positive affine transforms
       cannot change the output.
    """
    state=np.asarray(state_probabilities,dtype=np.float64)
    event=np.asarray(event_scores,dtype=np.float64)
    if state.ndim!=3 or state.shape[1:]!=(NUM_STRINGS,NUM_CLASSES):
        raise ValueError("state probabilities must be T x 6 x 21")
    if event.shape!=state.shape[:2]:
        raise ValueError("event scores must be T x 6")
    base=decode_with_hysteresis(state)
    maxima=local_event_maxima(event)
    out=base.copy()

    for s in range(NUM_STRINGS):
        # Compute runs from the frozen base only; adjustments never create a new run.
        for start,end,fret in _runs(base[:,s]):
            if fret < 0 or start <= 0:
                continue
            lo=max(0,start-BACKSHIFT_RADIUS_FRAMES)
            chosen=start
            for t in range(lo,start):
                if not maxima[t,s]:
                    continue
                row=state[t,s]
                best_fret=int(np.argmax(row[:NUM_FRETS]))
                if best_fret != fret:
                    continue
                if float(row[fret]) <= float(row[SILENCE_CLASS]):
                    continue
                chosen=t
                break
            if chosen < start:
                out[chosen:start,s]=fret
    return out
