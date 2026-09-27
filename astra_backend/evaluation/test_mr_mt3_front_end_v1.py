import tempfile, unittest
from pathlib import Path
import mido

from evaluation.mr_mt3_front_end_v1 import *
from evaluation.pretrained_note_front_end_v1 import PitchEvent

def write_midi(path, events):
    mid=mido.MidiFile(ticks_per_beat=480)
    tr=mido.MidiTrack(); mid.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo",tempo=500000,time=0))
    current_program={}
    last_tick=0
    serial=[]
    for row in events:
        start,end,ch,program,note=row
        serial.append((int(round(start*960)),0,ch,program,note))
        serial.append((int(round(end*960)),1,ch,program,note))
    serial.sort()
    for tick,kind,ch,program,note in serial:
        delta=tick-last_tick; last_tick=tick
        if current_program.get(ch)!=program:
            tr.append(mido.Message("program_change",channel=ch,program=program,time=delta))
            delta=0; current_program[ch]=program
        if kind==0:
            tr.append(mido.Message("note_on",channel=ch,note=note,velocity=80,time=delta))
        else:
            tr.append(mido.Message("note_off",channel=ch,note=note,velocity=0,time=delta))
    mid.save(path)

class MRMT3ProjectionTests(unittest.TestCase):
    def temp_midi(self,events):
        td=tempfile.TemporaryDirectory(); p=Path(td.name)/"x.mid"; write_midi(p,events)
        self.addCleanup(td.cleanup); return p

    def test_guitar_program_bounds_are_inclusive(self):
        p=self.temp_midi([(0.1,.2,0,24,40),(.3,.4,1,31,83)])
        ev,st=project_midi_to_guitar_events(p,0,1)
        self.assertEqual([(e.pitch,round(e.start,2)) for e in ev],[(40,.1),(83,.3)])
        self.assertEqual(st["accepted"],2)

    def test_non_guitar_program_rejected(self):
        p=self.temp_midi([(0.1,.2,0,23,60),(0.3,.4,1,32,60)])
        ev,st=project_midi_to_guitar_events(p,0,1)
        self.assertEqual(ev,[])
        self.assertEqual(st["rejectedProgram"],2)

    def test_percussion_rejected_even_with_guitar_program(self):
        p=self.temp_midi([(0.1,.2,9,24,60)])
        ev,st=project_midi_to_guitar_events(p,0,1)
        self.assertEqual(ev,[])
        self.assertEqual(st["rejectedPercussion"],1)

    def test_pitch_range_rejected(self):
        p=self.temp_midi([(0.1,.2,0,24,39),(.3,.4,0,24,84)])
        ev,st=project_midi_to_guitar_events(p,0,1)
        self.assertEqual(ev,[])
        self.assertEqual(st["rejectedPitchRange"],2)

    def test_crop_clipping_without_favorable_shift(self):
        p=self.temp_midi([(0.0,.3,0,24,40),(.9,1.2,0,24,45),(1.2,1.4,0,24,50)])
        ev,_=project_midi_to_guitar_events(p,.1,1.1)
        got=[(e.pitch,round(e.start,3),round(e.end,3)) for e in ev]
        self.assertEqual(got,[(40,0.0,.2),(45,.8,1.0)])

    def test_deterministic_multitrack_projection(self):
        p=self.temp_midi([(0.1,.2,0,24,40),(.3,.5,1,25,45)])
        a,_=project_midi_to_guitar_events(p,0,1)
        b,_=project_midi_to_guitar_events(p,0,1)
        self.assertEqual(a,b)

    def test_reuses_corrected_duplicate_pitch_scorer(self):
        p=self.temp_midi([(0.1,.4,0,24,45)])
        refs=[PitchEvent("a",45,.1,.4),PitchEvent("b",45,.1,.4)]
        x=score_projected_midi(p,refs,0,1)
        self.assertEqual(x["scores"]["rawReferenceCount"],2)
        self.assertEqual(x["scores"]["ambiguityCollapsedReferenceCount"],1)
        self.assertEqual(x["scores"]["pitchOnset"]["f1"],1.0)

    def test_zero_optimizer_no_threshold_search_frozen(self):
        x=frozen_identity()
        self.assertEqual(x["optimizerSteps"],0)
        self.assertIs(x["thresholdSearch"],False)
        self.assertEqual(x["checkpointBytes"],183672643)

if __name__=="__main__": unittest.main()
