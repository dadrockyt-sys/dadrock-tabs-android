import json, hashlib, os
from pathlib import Path

OUTDIR=Path('research/v154-professional-references'); OUTDIR.mkdir(parents=True,exist_ok=True)

strings=['e','B','G','D','A','E']
open_midi={'e':64,'B':59,'G':55,'D':50,'A':45,'E':40}
idx={s:i for i,s in enumerate(strings)}

def note(s,f,**kw):
    d={'string':s,'stringIndex':idx[s],'kind':'note','fret':int(f),'midi':open_midi[s]+int(f)}
    d.update(kw); return d

def dead(s,**kw):
    d={'string':s,'stringIndex':idx[s],'kind':'deadNote','fret':None,'midi':None,'notation':'x'}
    d.update(kw); return d

def add_voicing(events, frets, group, label=None, **kw):
    # frets dict in high-to-low string order. simultaneous group is preserved without timing inference.
    for s in strings:
        if s in frets:
            e=note(s,frets[s],chordGroup=group, simultaneous=True, **kw)
            if label: e['chordLabel']=label
            events.append(e)

def annotate_orders(events):
    for i,e in enumerate(events): e['visualOrder']=i
    return events

# page mapping
page_for={}
for m in range(1,8): page_for[m]=1
for m in range(8,12): page_for[m]=2
for m in range(12,16): page_for[m]=3
for m in range(16,24): page_for[m]=4
for m in range(24,29): page_for[m]=5
for m in range(29,35): page_for[m]=6
for m in range(35,39): page_for[m]=7
for m in range(39,44): page_for[m]=8
for m in range(44,49): page_for[m]=9
for m in range(49,56): page_for[m]=10
for m in range(56,61): page_for[m]=11
for m in range(61,66): page_for[m]=12
for m in range(66,78): page_for[m]=13
for m in range(78,82): page_for[m]=14
for m in range(82,86): page_for[m]=15
for m in range(86,90): page_for[m]=16
page_for[89]=[16,17]
page_for[90]=17
page_for[91]=[17,18]
for m in range(92,96): page_for[m]=18
for m in range(96,100): page_for[m]=19
for m in range(100,107): page_for[m]=20
for m in range(107,113): page_for[m]=21
page_for[113]=22

def section(m):
    if m<=16:return 'Intro'
    if m<=32:return 'Verse 1'
    if m<=38:return 'Chorus'
    if m<=46:return 'Riff'
    if m<=62:return 'Verse 2'
    if m<=69:return 'Chorus'
    if m<=77:return 'Bridge'
    if m<=94:return 'Solo'
    if m<=102:return 'Post-solo Riff'
    return 'Out-Chorus'

def ts(m):
    if m==104:return '2/4'
    return '4/4'

measures={m:{'measure':m,'timeSignature':ts(m),'events':[],'section':section(m),
             ('sourcePages' if isinstance(page_for[m],list) else 'sourcePage'):page_for[m],
             'timingNormalizationStatus':'not-yet-normalized-for-v154-step-scorer'} for m in range(1,114)}

def setev(m, evs, annotations=None, **extra):
    measures[m]['events']=annotate_orders(evs)
    if annotations: measures[m]['annotations']=annotations
    measures[m].update(extra)

def blank(m, annotations=None, **extra):
    if annotations: measures[m]['annotations']=annotations
    measures[m].update(extra)

# opening metadata/blanks
blank(1,['opening tempo quarter-note = 129','opening 4/4 time signature visible'])
for m in [2,3,4]: blank(m,['intentional blank/rest measure'])

# Main Em riff template m5-m11

def em_riff(full_end=True, final_rest=False, slide_final=False):
    evs=[note('G',14,bendLabel='full',slurToNext=True),note('G',12,slurFromPrevious=True),
         note('D',14),note('A',14),note('D',12),note('D',14,vibrato=True)]
    if full_end: evs.append(note('D',12))
    return evs
for m in range(5,12):
    setev(m,em_riff(),['Em riff','P.M. marking visible over later notes','vibrato marking visible near right side'])
# m10 overlay
measures[10]['annotations'].append('green selection highlight is interface UI and is excluded from notation')
setev(12,em_riff(full_end=False),['Em riff variant','P.M. marking visible','visible rest at measure end','vibrato marking visible'])
setev(13,em_riff(),['Em riff','P.M. marking visible','vibrato marking visible'])
setev(14,em_riff(full_end=False),['Em riff variant','P.M. marking visible','visible rest at measure end','vibrato marking visible'])
setev(15,em_riff(full_end=False),['Em riff variant','P.M. marking visible','visible rest at measure end','vibrato marking visible'])
ev16=em_riff(full_end=False); ev16[-1]['slideOut']=True
setev(16,ev16,['Em riff section ending','P.M. marking visible','vibrato marking visible','final D14 has visible slide/release mark','double barline/section boundary follows'])

for m in range(17,25): blank(m,['intentional blank/rest measure; lyric alignment visible'])

# transposed riff 25-27

def tr_riff():
    return [note('G',13,bendLabel='full',slurToNext=True),note('G',11,slurFromPrevious=True),note('D',12),note('A',12),note('D',10),note('D',12,vibrato=True)]
setev(25,tr_riff(),['full bend on G13','P.M. marking visible','vibrato marking visible','visible rest at end'])
setev(26,tr_riff(),['full bend on G13','P.M. marking visible','vibrato marking visible','visible rest at end'])
setev(27,tr_riff(),['full bend on G13','P.M. marking visible','vibrato marking visible'])
setev(28,[dead('D'),note('G',12),dead('D'),note('G',10),note('G',9,slurToNext=True),dead('D'),note('G',10),dead('D'),note('G',12),dead('D')],
      ['dead-note riff; a visible rest occurs before G9','curved articulation/slur visible at G9','exact rhythmic placement deferred'])
for m in range(29,33): blank(m,['intentional blank/rest measure; lyric alignment visible'])
blank(33,['rest/sustain glyph visible; no pitch inferred'],chordSymbols=['G6'])
blank(34,['rest/sustain glyph visible; no pitch inferred'],chordSymbols=['A(tp2)'])

# chord measures 35/36 and repeats

def chord35():
    ev=[]
    for n in range(4): add_voicing(ev,{'e':9,'B':9,'G':9},f'E-{n+1}','E')
    add_voicing(ev,{'e':7,'B':7,'G':7},'D-1','D')
    add_voicing(ev,{'e':9,'B':9,'G':9},'E-final','E',slideOut=True)
    return ev

def chord36():
    ev=[]
    for n in range(4): add_voicing(ev,{'e':9,'B':9,'G':9},f'E-{n+1}','E')
    add_voicing(ev,{'e':12,'B':12,'G':12},'G-1','G')
    add_voicing(ev,{'e':9,'B':9,'G':9},'E-final','E',slideOut=True)
    return ev
for m in [35,65,107]: setev(m,chord35(),['stacked notes in each chordGroup are simultaneous','final E voicing has visible release/slide arcs','visible rest follows'],chordSymbols=['E','D','E'])
for m in [36,66,108]: setev(m,chord36(),['stacked notes in each chordGroup are simultaneous','final E voicing has visible release/slide arcs','visible rest follows'],chordSymbols=['E','G','E'])
blank(37,['rests only; chord symbols visible'],chordSymbols=['G6','A(tp2)'])
blank(38,['intentional blank/rest measure','double barline follows'])
