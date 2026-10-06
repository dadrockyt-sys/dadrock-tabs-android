#!/usr/bin/env python3
from __future__ import annotations
import numpy as np
from guitartechs_training_v4.objective_decoder import NUM_CLASSES,NUM_STRINGS,decode_with_hysteresis,count_active_runs
from guitartechs_training_v8.decoder import decode_v8_hybrid

def synthetic():
    T=12
    state=np.zeros((T,NUM_STRINGS,NUM_CLASSES),float)
    state[...,20]=1.0

    def set_normalized_row(t,string,fret,active_p,silence_p):
        row=np.zeros(NUM_CLASSES,float)
        remainder=1.0-active_p-silence_p
        assert remainder >= 0.0
        others=[i for i in range(NUM_CLASSES) if i not in (fret,20)]
        if others:
            row[others]=remainder/len(others)
        row[fret]=active_p
        row[20]=silence_p
        assert np.isclose(row.sum(),1.0)
        state[t,string]=row

    # An admitted fret-4 run begins at frame 4 by V4 confidence.
    # Frame 3 already has fret 4 > silence, but not enough absolute confidence
    # for V4 start. Event ranking marks frame 3 as local maximum.
    set_normalized_row(3,0,4,0.38,0.36)
    for t in range(4,8):
        set_normalized_row(t,0,4,0.60,0.20)
    ev=np.zeros((T,NUM_STRINGS),float)
    ev[3,0]=2.0;ev[4,0]=1.0

    base=decode_with_hysteresis(state)
    hybrid=decode_v8_hybrid(state,ev)
    assert base[3,0] == -1 and base[4,0] == 4
    assert hybrid[3,0] == 4 and hybrid[4,0] == 4
    assert count_active_runs(hybrid)==count_active_runs(base)
    print("V8_BACKSHIFT_ONLY_PASS")

    # Event score calibration cannot change ranks/output.
    hybrid2=decode_v8_hybrid(state,ev*17.0+101.0)
    assert np.array_equal(hybrid,hybrid2)
    print("V8_CALIBRATION_INVARIANCE_PASS")

    # An event peak with a different relative fret cannot invent/change a note.
    bad=ev.copy();bad[2,0]=100
    set_normalized_row(2,0,7,0.60,0.20)
    h3=decode_v8_hybrid(state,bad)
    assert h3[2,0] == -1
    assert count_active_runs(h3)==count_active_runs(decode_with_hysteresis(state))
    print("V8_NO_NEW_RUNS_PASS")
    print("V8_SYNTHETIC_VERIFICATION_PASS")

if __name__=="__main__": synthetic()
