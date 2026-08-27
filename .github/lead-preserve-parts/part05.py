 'instrument':{'stringsHighToLow':strings,'openMidiHighToLow':[64,59,55,50,45,40],
               'stringIndexConvention':{str(i):s for i,s in enumerate(strings)},'midiRule':'midi = openMidi[stringIndex] + fret'},
 'source':{'receiptPath':'research/v154-professional-references/lead-source-set-receipt.json',
           'previousReceiptPath':'debug/v154-cpu-autonomous/reference-receipts/lead-user-upload-20260827.json',
           'pageCount':22,'previousFrozenSetSha256':prev_set,'currentRenderedSetSha256':current_set_sha,
           'currentCopiesByteIdentityMatchedPreviousFrozenReceipt':False,
           'visualLandmarksConsistentWithFrozenReceipt':True},
 'representation':{'eventOrder':'left-to-right visual order within each measure, including printed-system wraps',
                   'timing':'visual order only; exact V154 16-step onset values are intentionally not present',
                   'scoringReady':False,'requiresTimingNormalizationBeforeScoring':True,
                   'whyNoStepValues':'avoid inventing exact onset timing from horizontal screenshot spacing before a dedicated timing-normalization pass',
                   'deadNotesHaveNullMidi':True,
                   'continuationOnlyMeans':'parenthesized tie/sustain/bend continuation visible with no new attack inferred',
                   'simultaneousChordGroups':'shared chordGroup identifiers preserve stacked chord voicings without inferring exact step onset',
                   'techniques':'visible bends, slides/slurs, vibrato, palm-mute markings and selected picking marks are preserved as flags/raw labels; bend labels are not semitone-normalized here'},
 'measureRange':{'first':1,'last':113,'measureCount':113},
 'audit':{'storedMeasureObjects':113,'eventObjects':len(all_events),'pitchedEventObjects':pitched,'deadNoteObjects':deadn,
          'continuationOnlyObjects':cont,'observedMidiMin':min(midis),'observedMidiMax':max(midis),
          'midiMappingErrors':0,'measureSequenceContinuous':True,'scoringStepFieldsPresent':False},
 'knownUncertainties':[{'measure':10,'type':'ui-overlay','action':'green selection highlight ignored as interface overlay'},
                       {'measures':[39,40],'type':'source-annotation','text':'Probably a mistake they left in','action':'preserve source uncertainty; do not silently correct','excludeFromScoringUntilTimingNormalizationResolved':True},
                       {'measure':81,'type':'detached-gray-dot','action':'not assigned to a note; meaning ambiguous between notation and UI'}],
 'measures':[measures[m] for m in range(1,114)]
}

# validation recursively no step fields and MIDI mapping
assert [m['measure'] for m in ref['measures']]==list(range(1,114))
assert ref['measures'][103]['measure']==104 and ref['measures'][103]['timeSignature']=='2/4'
assert ref['measures'][104]['measure']==105 and ref['measures'][104]['timeSignature']=='4/4'

def walk(x):
    if isinstance(x,dict):
        assert 'step' not in x
        for v in x.values(): walk(v)
    elif isinstance(x,list):
        for v in x: walk(v)
walk(ref)
errors=[]
for mo in ref['measures']:
    assert mo['eventCount']==len(mo['events'])
    assert mo['attackLikeEventCount']==sum(1 for e in mo['events'] if not e.get('continuationOnly'))
    for e in mo['events']:
        if e['kind']=='deadNote':
            if e['midi'] is not None or e['fret'] is not None: errors.append((mo['measure'],e))
        else:
            exp=open_midi[e['string']]+e['fret']
            if e['midi']!=exp: errors.append((mo['measure'],e,exp))
assert not errors,errors
assert ref['audit']['eventObjects']==sum(m['eventCount'] for m in ref['measures'])
assert ref['audit']['pitchedEventObjects']+ref['audit']['deadNoteObjects']==ref['audit']['eventObjects']
assert any(u.get('measures')==[39,40] for u in ref['knownUncertainties'])
assert receipt['byteIdentityMatchPreviousFrozenReceipt'] is False

ref_path=OUTDIR/'lead-professional-reference-machine-readable.json'
receipt_path=OUTDIR/'lead-source-set-receipt.json'
ref_path.write_text(json.dumps(ref,indent=2,ensure_ascii=False,sort_keys=False)+'\n',encoding='utf-8')
receipt_path.write_text(json.dumps(receipt,indent=2,ensure_ascii=False,sort_keys=False)+'\n',encoding='utf-8')
sha=hashlib.sha256(ref_path.read_bytes()).hexdigest()
# Git blob SHA is deterministic and can be computed before commit.
import subprocess
from datetime import datetime, timezone
blob=subprocess.check_output(['git','hash-object',str(ref_path)],text=True).strip()
receipt_blob=subprocess.check_output(['git','hash-object',str(receipt_path)],text=True).strip()
provenance={
 'schema':'dadrock.tabs.v154.professional-reference-provenance.v1',
 'part':'lead',
 'song':ref['song'],
 'researchBranch':'v143-contextual-prune-lobo',
 'preservedAtUtc':datetime.now(timezone.utc).isoformat(),
 'sourceSet':{
   'receiptPath':str(receipt_path),
   'previousFrozenPageCount':22,
   'previousFrozenSetSha256':prev_set,
   'currentRenderedSetSha256':current_set_sha,
   'currentCopiesByteIdentityMatchedPreviousFrozenReceipt':False,
   'visualLandmarksConsistentWithFrozenReceipt':True
 },
 'machineReadableReference':{
   'repositoryPath':str(ref_path),
   'sha256':sha,
   'gitBlobSha':blob,
   'measureCount':113,
   'eventObjects':ref['audit']['eventObjects'],
   'pitchedEventObjects':ref['audit']['pitchedEventObjects'],
   'deadNoteObjects':ref['audit']['deadNoteObjects'],
   'continuationOnlyObjects':ref['audit']['continuationOnlyObjects'],
   'observedMidiRange':[ref['audit']['observedMidiMin'],ref['audit']['observedMidiMax']],
   'scoringReady':False,
   'exactStepTimingFrozen':False
 },
 'uncertainties':[
   {'measure':10,'type':'ui-overlay','excludedFromNotation':True},
   {'measures':[39,40],'type':'source-annotation','text':'Probably a mistake they left in','excludeFromScoringUntilTimingNormalizationResolved':True},
   {'measure':81,'type':'detached-gray-dot','assignedToNote':False}
 ],
 'authorization':{
   'userExplicitlyRequestedMachineReadableLeadSavedToResearchBranch':True,
   'userProvidedScreenshots':True
 },
 'safety':{
   'screenshotBytesCommitted':False,
   'candidateGenerationMayReadReference':False,
   'referenceFacingScoreCallsDuringPreservation':0,
   'generatedCandidateModified':False,
   'mainOrProductionModified':False,
   'modalUsed':False,
   'cudaGpuUsed':False
 }
}
prov_path=OUTDIR/'lead-professional-reference-provenance.json'
