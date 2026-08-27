prov_path.write_text(json.dumps(provenance,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')

cp=Path('docs/checkpoints/CURRENT_STATE.md')
text=cp.read_text(encoding='utf-8')
text=text.replace(
 'Active phase: **V154 broad-Other CPU recognition output is COMPLETE / FROZEN / STRUCTURAL-QC PASS. Rhythm is preserved machine-readably; Bass screenshots have been re-provided and the complete Bass visual reference is now preserved machine-readably. Lead still needs to be re-provided before three-part scoring normalization. Professional-reference scoring has NOT run.**',
 'Active phase: **V154 broad-Other CPU recognition output is COMPLETE / FROZEN / STRUCTURAL-QC PASS. Rhythm, Bass, and Lead are now preserved machine-readably. Bass and Lead remain visual-order references without frozen exact 16-step scorer timing. Professional-reference scoring has NOT run.**')
text=text.replace(
 '- Bass screenshot bytes are now re-provided and identity-matched; its visual-order machine-readable transcription is preserved under `research/v154-professional-references/`. Lead screenshot bytes remain the current missing reference input. Exact 16-step Bass timing is intentionally not frozen yet, so the Bass file is not scorer-ready.',
 '- Bass is preserved under `research/v154-professional-references/` with its canonical bytes identity-matched. Lead has now also been re-provided and preserved visually machine-readably. The active-chat Lead copies are platform-rendered/re-encoded, so their byte hashes differ from the earlier frozen upload receipt; the 22-page order, measures 1–113, tempo/time-signature opening, green UI overlay, and measures 39–40 source annotation visually corroborate the frozen Lead identity. Exact 16-step Bass/Lead timing is intentionally not frozen yet, so those files are not scorer-ready.')
text=text.replace(
 '- Professional reference note data opened this continuation: **YES — Bass only, for explicit user-authorized research preservation; no scoring performed. Rhythm was already preserved. Lead remains unopened/unavailable.**',
 '- Professional reference note data opened this continuation: **YES — Bass and Lead, for explicit user-authorized research preservation; no scoring performed. Rhythm was already preserved.**')
text=text.replace(
 '2. Do not perform professional-reference scoring yet. Bass is now preserved visually machine-readably but does not have frozen 16-step scorer timing; Lead screenshots still need to be re-provided and preserved.\n3. After Lead is preserved, run a dedicated reference-normalization pass that freezes exact scorer-ready `(measure, step, MIDI)` identities for Rhythm/Lead/Bass without consulting or altering the frozen generated candidate. Then score this exact combined Guitar first and Bass second **exactly once** with `score_frontend_reference.py`.',
 '2. Do not perform professional-reference scoring yet. Bass and Lead are preserved visually machine-readably but do not have frozen exact 16-step scorer timing.\n3. Run a dedicated three-part reference-normalization pass that freezes exact scorer-ready `(measure, step, MIDI)` identities for Rhythm/Lead/Bass without consulting or altering the frozen generated candidate. Then score this exact combined Guitar first and Bass second **exactly once** with `score_frontend_reference.py`.')
text=text.replace(
 '- Current missing professional input is Lead. Once Lead screenshots are re-provided and preserved, freeze exact three-part scoring timing identity before the one-time reference-facing score.',
 '- Lead is now preserved beside Rhythm and Bass. Next freeze exact three-part scoring timing identity before the one-time reference-facing score.')
marker='## V154 professional Lead preservation — COMPLETE VISUAL MACHINE-READABLE / TIMING NOT YET SCORER-NORMALIZED'
if marker not in text:
    lines=[
      '', '', marker,
      '- User re-provided all 22 Lead pages in two batches (Lead 1–11 and Lead 12–22) and explicitly requested machine-readable preservation on research branch `v143-contextual-prune-lobo`.',
      f'- Prior frozen Lead receipt remains `debug/v154-cpu-autonomous/reference-receipts/lead-user-upload-20260827.json`, 22 pages / measures 1–113 / opening quarter=129 / 4/4 / frozen set SHA256 `{prev_set}`.',
      '- The active-chat copies are platform-rendered/re-encoded and therefore are **not falsely claimed as byte-identical** to the earlier upload. Current rendered-copy hashes, sizes, dimensions, page-order mapping, and the previous frozen identity are recorded in `research/v154-professional-references/lead-source-set-receipt.json`. Screenshot bytes are **not committed**.',
      f'- Complete visual machine-readable Lead reference: `research/v154-professional-references/lead-professional-reference-machine-readable.json`; SHA256 `{sha}`; Git blob `{blob}`.',
      f'- Coverage: measures 1–113 / 113 measure objects; {ref["audit"]["eventObjects"]} event objects; {ref["audit"]["pitchedEventObjects"]} pitched event objects; {ref["audit"]["deadNoteObjects"]} dead-note objects; {ref["audit"]["continuationOnlyObjects"]} tie/sustain/bend-continuation-only objects; observed MIDI {ref["audit"]["observedMidiMin"]}–{ref["audit"]["observedMidiMax"]}; tuning/MIDI mapping errors 0.',
      '- Measure 10 green selection highlight is ignored as interface UI. The visible measures 39–40 annotation `Probably a mistake they left in` is preserved as source uncertainty and is not silently repaired. The detached gray dot at measure 81 remains unassigned because its notation/UI meaning is ambiguous.',
      '- Chord stacks preserve simultaneous string/fret/MIDI identities through `chordGroup`; solo bends/slides/slurs/vibrato and visible picking marks are preserved as flags/raw labels where legible.',
      '- This Lead file intentionally contains **no `step` onset fields**. It preserves visual note/string/fret/MIDI/technique order but is **not yet V154 scorer-normalized**; exact timing must be frozen in a dedicated normalization pass before scoring.',
      '- Provenance: `research/v154-professional-references/lead-professional-reference-provenance.json`.',
      '- Candidate generation remains frozen and reference-blind. Reference-facing score calls remain `0`; generated candidate unchanged; `main`/Production unchanged; Modal/L4/CUDA/GPU not used.',
      '- Rhythm ✅ Bass ✅ Lead ✅. Next action is exact three-part timing normalization, then the preregistered one-time reference-facing score.',
      ''
    ]
