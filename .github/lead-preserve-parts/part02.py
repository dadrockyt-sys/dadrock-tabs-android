# source uncertainty riff 39-46
setev(39,[note('D',12,parenthesized=True,ghostLike=True)],
      ['mostly rests','parenthesized D12 is preserved exactly as visible','source annotation above measures 39–40 says “Probably a mistake they left in”','do not silently correct source'],
      excludeFromScoringUntilTimingNormalizationResolved=True)
blank(40,['intentional blank/rest measure','source annotation above measures 39–40 says “Probably a mistake they left in”','do not silently correct source'],excludeFromScoringUntilTimingNormalizationResolved=True)
for m in [41,43,44,45]:
    setev(m,em_riff(full_end=False),['Em riff','P.M. marking visible','vibrato marking visible','visible rest at end'])
for m in [42,46]:
    ev=em_riff(full_end=False); ev[-1]['slideOut']=True
    setev(m,ev,['Em riff','P.M. marking visible','vibrato marking visible','final D14 has visible slide/release mark'])
measures[46]['annotations'].append('double barline/section boundary follows')

for m in range(47,55): blank(m,['intentional blank/rest measure; lyric alignment visible'])
for m in [55,56]: setev(m,tr_riff(),['full bend on G13','P.M. marking visible','vibrato marking visible','visible rest at end'])
ev57=tr_riff()+[dead('D'),dead('D')]
setev(57,ev57,['full bend on G13','P.M. marking visible','vibrato marking visible','two D-string dead notes at end'])
setev(58,[note('G',12),note('G',12),note('G',10),note('G',10),dead('D'),note('G',9,slurToNext=True),dead('D'),note('G',10),dead('D'),note('G',12),note('G',12),note('G',12,slideOut=True)],
      ['mixed fretted/dead-note riff','visible curved articulation at G9','final G12 has visible slide/release mark'])
for m in range(59,63): blank(m,['intentional blank/rest measure; lyric alignment visible'])
blank(63,['rest/sustain glyph visible; no pitch inferred'],chordSymbols=['G6'])
blank(64,['rest/sustain glyph visible; no pitch inferred'],chordSymbols=['A(tp2)'])
# 65/66 already set
blank(62,['intentional blank/rest measure before Chorus','double barline into Chorus'])

# m67-69 sustained A voicing, then bridge
# m67 chord printed after rests: B2 G2 D2 A0
v=[]; add_voicing(v,{'B':2,'G':2,'D':2,'A':0},'A-sustain-start','A(tp2)',tieToNext=True)
setev(67,v,['rests precede the final A voicing','stacked chord tones are simultaneous','ties continue into measure 68'],chordSymbols=['G6','A(tp2)'])
v=[]
for s,f in [('B',2),('G',2),('D',2),('A',0)]: v.append(note(s,f,parenthesized=True,continuationOnly=True,tieFromPrevious=True,tieToNext=True))
setev(68,v,['parenthesized A-voicing continuation; no new attack inferred','long ties visible across measure'])
v=[]
for s,f in [('B',2),('G',2),('D',2)]: v.append(note(s,f,parenthesized=True,continuationOnly=True,tieFromPrevious=True))
setev(69,v,['only three parenthesized upper chord tones remain visibly printed at left','continuation only; no new attack inferred','double barline into Bridge'])
for m in range(70,78): blank(m,['intentional blank/rest Bridge measure'])

# Solo 78-94
setev(78,[note('D',12,slurToNext=True),note('D',14,slurFromPrevious=True),note('G',12,slurToNext=True),note('G',14,slurFromPrevious=True,slurToNext=True),note('G',12,slurFromPrevious=True,tieToNext=True)],
      ['Solo begins','vibrato marking visible above passage','curved slur/legato arcs preserved; exact onset timing deferred'])
setev(79,[note('G',12,parenthesized=True,continuationOnly=True,tieFromPrevious=True,bendLabel='full'),note('D',14,slurToNext=True),note('D',12,slurFromPrevious=True),note('A',14),note('D',12)],
      ['opening parenthesized G12 continues from measure 78 and carries a visible full-bend arrow','rests separate the continuation from later fast-note group','tiny mark near bend label is not interpreted beyond raw full-bend label'])
setev(80,[note('D',14,slideOut=True),note('A',12,bendLabel='1/4'),note('A',12),note('A',10,bendLabel='1/4'),note('A',10),note('E',12,bendLabel='1/4'),note('E',12)],
      ['vibrato marking visible at left','three visible quarter-bend labels preserved as raw “1/4”'])
setev(81,[note('E',10,slurToNext=True),note('E',12,slurFromPrevious=True),note('E',10,slurToNext=True),note('E',12,slurFromPrevious=True,slideOut=True),note('A',11,slideIn=True),note('D',9)],
      ['vibrato marking visible above middle/right','detached small gray dot above far right is not assigned to a note because its notation/UI meaning is ambiguous'],
      visualUncertainty=True)
setev(82,[dead('D'),note('D',11,slurToNext=True),note('D',9,slurFromPrevious=True),note('A',11),note('D',9),note('D',11),note('G',9),note('G',11),note('G',11,bendLabel='full'),note('G',11,parenthesized=True,continuationOnly=True,bendReleaseContext=True),note('G',9),note('D',11)],
      ['visible rests are omitted from attack-event list','full-bend/release context on G11 preserved without inventing exact bend timing'])
setev(83,[note('G',9,slurToNext=True),note('G',11,slurFromPrevious=True,slurToNext=True),note('G',9,slurFromPrevious=True),note('D',11),note('G',9),note('G',11),note('G',13,slideIn=True),note('B',12),note('e',12),note('B',12),note('B',17,slideIn=True),note('B',17,vibrato=True)],
      ['vibrato marking visible over final high-register notes','curved articulation under final B17 preserved generically as vibrato/slur context'])
setev(84,[note('B',17,vibrato=True),note('B',17),note('e',15),note('B',17,vibrato=True),note('B',17),note('G',16),note('e',15),note('B',17,tieToNext=True)],
      ['multiple vibrato markings visible','final B17 carries curved continuation into measure 85'])
setev(85,[note('B',17,parenthesized=True,continuationOnly=True,tieFromPrevious=True,bendLabel='full'),note('B',17,bendLabel='full'),note('B',17,bendLabel='full'),note('B',17,bendLabel='full')],
      ['four visible full-bend indications; first is a parenthesized continuation from measure 84'])
setev(86,[note('B',17,bendLabel='full',slurToNext=True),note('B',15,slurFromPrevious=True),note('G',17),note('G',17,vibrato=True,tieToNext=True),note('G',17,parenthesized=True,continuationOnly=True,tieFromPrevious=True,bendLabel='2')],
      ['vibrato marking visible across middle','parenthesized final G17 has raw bend label “2”','visible rest follows'])
setev(87,[note('G',17,bendLabel='2',slurToNext=True),note('G',17,bendLabel='2'),note('G',17,bendLabel='1 3/4'),note('G',17,bendLabel='2',slurToNext=True),note('G',17,bendLabel='2')],
      ['raw bend labels are preserved exactly as visible; no semitone normalization yet','visible initial rest'])
