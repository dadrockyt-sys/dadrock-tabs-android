# V168 — External holdout candidate screening addendum

Date: 2026-08-29 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **SCREENING ONLY / NO ASSETS ADMITTED / SCORING NOT ARMED**

This addendum continues the frozen candidate-screening checkpoint. It changes no V168 policy, admission rule, provenance rule, scoring rule, or V167 result.

Current V168 reference-facing score calls: **0**.

## Updated ranking

### 1. GOAT — strongest remaining acquisition candidate

Status: **PROMISING / NOT ADMITTED / ACCESS GRANT REQUIRED / REFERENCE LAYER MUST BE CHOSEN PROSPECTIVELY**

Authoritative/public findings:
- GOAT contains 5.9 hours of unique real electric-guitar DI recordings with paired Guitar Pro tablatures and MIDI representations.
- The paper states that the data came from the main authors and two third-party content creators.
- For the collected audio/tab pairs, each song was **manually checked and aligned against the tablature to ensure every note was correct between audio and tablature**.
- Additional audio was recorded by following collected community-created tablatures exactly.
- The tablature layer is quantized. MIDI is exported from Guitar Pro.
- A separate **fine-aligned MIDI** layer is then produced using an external alignment procedure; both quantized and fine-aligned MIDI are supplied.
- The published dataset record is **Restricted** and states that access is by request, **for research purposes only**, and not for use in a commercial product.
- The restricted Zenodo dataset record currently exposes no license value in its rights field; therefore any access grant/terms must be preserved as the actual use-basis provenance.
- The paper's ethical statement says content creators were informed of applications/use cases, agreed, and were compensated; because some content consists of covers and the authors do not exclusively own all copyrights, access is research-only upon request.

### Frozen-gate interpretation

GOAT is not admitted yet.

If access is granted, the prospective professional-reference candidate must be derived from the **human-checked tablature content layer**, not silently from the provided fine-aligned MIDI layer.

Reason: the fine-aligned MIDI is explicitly the output of a separate alignment procedure. Under the frozen V168 provenance companion, we must not declare a model/algorithm-derived alignment product `derivedFromModelOrCandidateOutput=false` without establishing that claim. The human-checked Guitar Pro/tab note content has materially cleaner provenance.

Before any GOAT admission, freeze prospectively:
1. exact access grant / research-use terms;
2. exact dataset version and downloaded file SHA256 identities;
3. exact source-audio ↔ Guitar Pro/tab pair binding;
4. whether each selected reference is the quantized tab itself or a deterministic score-to-performance timing transform;
5. any timing transform algorithm and parameters **before comparative scoring**;
6. proof that candidate generation cannot access reference content;
7. a fixed song-selection rule before any Policy A/B outcome exists.

The public GOAT GitHub repository contains two audio examples with matching Guitar Pro/MIDI/text assets, but no repository `LICENSE` file was observed in the inspected tree. Those examples are therefore not a shortcut around the restricted-dataset rights gate.

### Song-selection posture if access is granted

Do not choose favorable songs after seeing results. A future selection rule must be frozen before score access—for example, all eligible independent real DI items satisfying the source/reference contract, or a deterministic metadata-only subset rule. No rule is selected at this checkpoint.

## 2. EGDB five-song real-world evaluation set — blocked

Status: **MANUAL-REFERENCE PROVENANCE PROMISING / NOT ADMITTED / SYMBOLIC REFERENCE + SOURCE-RIGHTS BLOCKED**

The ICASSP paper states that its final real-world evaluation used five guitar recordings downloaded from YouTube and **manually annotated by the authors' musician**. This is strong annotation provenance.

However, the public demo repository exposes:
- five `RealData/clipN.wav` source clips; and
- five `RealDataTranscription/clipN.wav` files used on the demo page as the **proposed model's rendered transcription output**.

The inspected public repository tree does not expose the musician's manual symbolic note-event references for these five clips. The demo page likewise presents source audio versus proposed-model audio output, not reference-event files.

In addition, the paper identifies the source recordings as third-party YouTube recordings and the demo/repository does not provide a frozen license/use grant for those exact source clips.

Therefore the five-song real-world set cannot currently satisfy both:
- exact professional-reference byte identity; and
- frozen rights/use-basis for the paired source recording.

Do not use the model-output WAVs as ground truth.

## 3. François Leduc Dataset — excluded under current frozen provenance rule

Status: **EXCLUDED FOR V168 UNDER CURRENT GATE**

The dataset contains dozens of solo-guitar audio/MIDI pairs and originates from commercially available professional transcriptions by François Leduc. The dataset is research-oriented and has strong source-score provenance.

However, the accompanying research explicitly constructs the released high-resolution MIDI by aligning existing transcribed scores to **transcription-model activations**. The project description states that the method takes a transcribed score and matches it to audio using model activations.

The frozen V168 provenance companion requires:

`professionalReference.derivedFromModelOrCandidateOutput = false`

Accordingly, the released aligned MIDI must not be admitted by weakening or reinterpreting the frozen rule after discovering a convenient dataset.

Potential raw commercial scores are a different artifact and are not admitted here; using them would require separate rights, exact audio pairing, and a prospectively frozen timing/reference conversion path.

## 4. GAPS — remains excluded under current frozen provenance rule

Status: **EXCLUDED FOR V168 UNDER CURRENT GATE**

Prior screening found its high-resolution note alignment relies on algorithmic/model-assisted alignment plus later human verification/correction. Because the frozen companion explicitly forbids model/candidate-derived reference artifacts, GAPS remains outside the current V168 admission contract even though it is a high-quality research dataset.

## EGSet12 — unchanged

EGSet12 remains **blocked**, not admitted. The authors' evaluation loader points to `jams_corrected/`, but the correction provenance/bytes were not recovered from the public repository, issues, PRs, releases, project-site tree, or inspected commit history. Do not substitute the public release JAMS by assumption.

## Current conclusion

- **GOAT is now the strongest remaining acquisition candidate.**
- It is still not admissible until the restricted research-use access is actually granted and exact bytes/terms are frozen.
- Its human-checked Guitar Pro/tab layer is the only currently defensible reference starting point; the provided fine-aligned MIDI is not automatically admissible under the frozen no-model-derived-reference rule.
- EGDB's five-song real-world set has good human annotation provenance but lacks publicly available symbolic references and frozen source-recording rights.
- François Leduc and GAPS are excluded under the existing no-model-derived-reference requirement; do not weaken the gate.
- V168 score calls remain **0**.
- No candidate generation or generic scorer adapter is armed.
- CPU only; GPU/CUDA/Modal remain unused and unauthorized.
- `main`/Production remain untouched.

## Next safe boundary

1. **Do not score.**
2. Treat GOAT access as the primary acquisition path.
3. Do not claim access, license, or byte identities until an actual dataset grant/download exists.
4. If access becomes available, inspect metadata/structure without comparative scoring and freeze a reference-source/timing-conversion rule before admission.
5. Keep EGDB, EGSet12, François Leduc, and GAPS blocked/excluded as documented unless genuinely new provenance evidence appears; do not weaken frozen requirements.
6. Save `CURRENT_STATE.md` before any access-derived manifest, reference conversion, candidate generation, or scorer code is staged.
