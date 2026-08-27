setev(88,[note('B',17,bendLabel='2',slurToNext=True),note('B',15,slurFromPrevious=True),note('G',16),note('B',15,slurToNext=True),note('B',17),note('G',16,slideToNext=True),note('G',14,slideFromPrevious=True,slideToNext=True),note('G',12,slideFromPrevious=True),note('D',14)],
      ['descending G16–G14–G12 is under a visible curved/slide-like phrase mark','raw bend label “2” preserved'])
# m89 split across pages
setev(89,[note('G',12,slurToNext=True),note('G',14,slurFromPrevious=True,slurToNext=True),note('G',12,slurFromPrevious=True),note('D',14),note('G',12),note('G',14),note('G',14,parenthesized=True,continuationOnly=True,bendLabel='full'),note('e',12),note('B',12),note('B',15),note('B',15,parenthesized=True,continuationOnly=True,bendLabel='full'),note('e',12),note('B',15),note('B',12),note('G',14,slideOut=True)],
      ['measure wraps from source page 16 onto source page 17','parenthesized notes are preserved as visible bend/release continuations','exact wrapped-system timing intentionally deferred'])
# m90 two systems on page17
setev(90,[note('G',14,parenthesized=True,continuationOnly=True,bendLabel='full'),note('B',12),note('e',12),note('B',12),note('B',15,slurToNext=True),note('B',15,parenthesized=True,continuationOnly=True,bendLabel='full'),note('e',12),note('B',15),note('B',12),note('G',14,slurToNext=True),note('G',14,parenthesized=True,continuationOnly=True,bendLabel='full'),note('B',12),note('e',12),note('B',12),note('B',15,slurToNext=True),note('B',15,parenthesized=True,continuationOnly=True,bendLabel='full')],
      ['measure spans two printed systems on source page 17','visual order is preserved across the wrap; exact onset timing deferred'])
# m91 spans pages17/18; continuing repeating high-register figure
setev(91,[note('e',12),note('B',15),note('e',12),note('B',15,slurToNext=True),note('B',15,parenthesized=True,continuationOnly=True,bendLabel='full'),note('e',12),note('B',15,tieToNext=True),note('B',15,parenthesized=True,continuationOnly=True,bendLabel='full'),note('e',12),note('B',15),note('B',15,parenthesized=True,continuationOnly=True,bendLabel='full'),note('e',12),note('B',15),note('B',15,parenthesized=True,continuationOnly=True,bendLabel='full'),note('e',12)],
      ['measure wraps from source page 17 to source page 18','downstroke/upstroke symbols are visible on portions of the figure and are preserved at measure level','exact picking-to-note alignment is not forced where the wrapped screenshot is ambiguous'],
      pickingMarksVisible=['downstroke','upstroke'])
# m92 first system + wrapped second system. Exact strings from staff positions.
setev(92,[
    note('e',15,slurToNext=True,picking='downstroke'),note('e',12,slurFromPrevious=True),note('B',15,picking='downstroke'),note('e',12,picking='upstroke'),
    note('B',15,slurToNext=True,picking='downstroke'),note('B',12,slurFromPrevious=True),note('G',14),note('B',15,slurToNext=True,picking='upstroke'),
    note('B',12,picking='upstroke'),note('G',14),note('B',12,picking='downstroke'),note('G',14,bendLabel='full',picking='upstroke'),note('D',14),
    note('G',12,tripletGroup='m92-triplet-1',slurToNext=True),note('G',14,tripletGroup='m92-triplet-1',slurFromPrevious=True,slurToNext=True),note('G',12,tripletGroup='m92-triplet-1',slurFromPrevious=True,tieToNext=True)
],['measure spans two printed systems','visible downstroke/upstroke marks preserved where alignment is clear','last three G-string notes are under a visible triplet bracket marked 3','final G12 ties into measure 93'])
setev(93,[note('G',12,parenthesized=True,continuationOnly=True,tieFromPrevious=True,tieToNext=True,vibrato=True)],
      ['parenthesized G12 is continuation only from measure 92','vibrato marking extends over measures 93–94'])
setev(94,[note('G',12,parenthesized=True,continuationOnly=True,tieFromPrevious=True,vibrato=True)],
      ['parenthesized G12 is continuation only from measure 93','vibrato marking extends over measures 93–94'])

# post-solo riff 95-102
for m in range(95,102): setev(m,em_riff(full_end=False),['Em riff','P.M. marking visible','vibrato marking visible','visible rest at end'])
ev102=em_riff(full_end=False); ev102[-1]['slideOut']=True
setev(102,ev102,['Em riff section ending','P.M. marking visible','final D14 has visible curved slide/release','double barline into Out-Chorus'])
blank(103,['Out-Chorus begins; intentional blank/rest measure'])
blank(104,['explicit 2/4 time signature visible','intentional blank/rest measure'])
blank(105,['explicit return to 4/4 time signature visible','intentional blank/rest measure'])
blank(106,['intentional blank/rest measure'])
# 107/108 already set
for m in range(109,114): blank(m,['intentional blank/rest measure; lyric alignment visible' if m<113 else 'final blank measure with final barline'])

# chord symbol metadata on relevant measures
measures[5]['chordSymbols']=['Em']; measures[41]['chordSymbols']=['Em']; measures[95]['chordSymbols']=['Em']
# sections labels are above specific boundaries, retained automatically via section field

# finalize counts
all_events=[]
for m in range(1,114):
    obj=measures[m]
    obj['eventCount']=len(obj['events'])
    obj['attackLikeEventCount']=sum(1 for e in obj['events'] if not e.get('continuationOnly'))
    all_events.extend(obj['events'])

pitched=sum(1 for e in all_events if e['kind']=='note')
deadn=sum(1 for e in all_events if e['kind']=='deadNote')
cont=sum(1 for e in all_events if e.get('continuationOnly'))
midis=[e['midi'] for e in all_events if e['kind']=='note']

# Current screenshot receipt metadata for transformed chat copies (hashes measured in active ChatGPT sandbox before commit; screenshot bytes are NOT committed)
current = [
    {'page': 1, 'currentFilename': '84.jpg', 'previousReceiptFilename': '1000120332.jpg', 'bytes': 132772, 'width': 1314, 'height': 2048, 'sha256': 'c12ee1f9e7499c5f8a85551295dd657f4e6736730670ac8d1132841903de31a1'},
    {'page': 2, 'currentFilename': '85.jpg', 'previousReceiptFilename': '1000120334.jpg', 'bytes': 136397, 'width': 1269, 'height': 2048, 'sha256': '7187a049373bc7f2ffad8aaf0a2ba44e4e9d61933df108106c7669d7b6ec71b1'},
    {'page': 3, 'currentFilename': '86.jpg', 'previousReceiptFilename': '1000120336.jpg', 'bytes': 126641, 'width': 1263, 'height': 2048, 'sha256': '87cb8ad414d3f57430ac79bb4558c68e79b92299a9665e9f8d654aae5a483f64'},
