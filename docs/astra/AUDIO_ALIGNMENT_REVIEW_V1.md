# Audio-only timing review

`astra_backend/evaluation/build_alignment_review.py` builds a self-contained HTML review page from mono PCM16 WAV and the preserved pulse-evidence JSON. It verifies the exact WAV SHA256 and sample rate before embedding audio; rejects invalid or non-increasing pulse times. It does not accept predictions or normalized reference labels.

The page supports waveform seeking, explicit seconds, playhead capture, playback speed, quarter-note anchors, removal and draft JSON download. A reviewer must identify the first measure and quarter-note interpretation by listening and reading the source. Detected pulses are diagnostic markers only. No automatic downbeat selection, inferred beat numbering, extrapolation, score calculation or review approval occurs. Draft segments use the scoring runner's beatStart/beatEnd/timeStart/timeEnd shape, but reviewStatus remains draft and explicit unresolvedItems remain. Work is not autosaved. Export before closing.

Reproduce outside the public repository (the output embeds source audio):

```sh
python astra_backend/evaluation/build_alignment_review.py \
  --wav /private/first30.wav \
  --evidence docs/astra/GOMYWAY_AUDIO_TIMING_EVIDENCE_V1.json \
  --output /private/Gomyway-Audio-Review.html
```

Output creation is exclusive. Restore the WAV from the pinned midterm using ffmpeg `-t 30 -ac 1 -ar 22050 -c:a pcm_s16le`; the builder enforces the evidence digest. An actual build on 2026-09-20 succeeded with SHA256 `60ed11dcdea26a3773d1867671001e30d11e28e0bc9429cdb94a6575c87792cb`, 30 seconds and 33 diagnostic pulses. The generated page is retained privately, not committed to Git.

Verification: 19 focused Python tests pass (15 scorer + 4 builder). `node astra_backend/evaluation/test_alignment_review.cjs` passes actual JavaScript syntax/export-function checks, including mapping, immutable inputs and six invalid-anchor cases. A Playwright end-to-end attempt failed before opening the page because the browser executable is absent; agent-browser CLI is also absent. No browser/package installation was performed. Visual layout, actual playback and browser download behavior remain unverified. No new labels, downbeat approval, model run or Gomyway score.

Next: open the private page in a browser, verify playback/export and independently mark timing anchors while auditing the professional source. Preserve the draft; only a separate completed musical review may create a complete alignment bundle. This is an aid to resolving the current blocker, not evidence that it has been resolved.
