
## V154 three-part professional reference set — RECEIVED / IDENTITY FROZEN — 2026-08-27 UTC
- Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Status: **Rhythm + Bass + Lead references are all received and their source identities are frozen. No note-by-note reference content has been committed from the user uploads.**
- Rhythm reference: existing `main:public/Professionalexample.jpg`; frozen Git blob **`16106197cc1269cca0b3c443908d5ef75e8b4d3e`**. Research-branch receipt: `debug/v154-cpu-autonomous/reference-receipts/rhythm-existing-professionalexample-20260827.json`; receipt Git blob **`258eb10fe44951d5f1f5969959ff0ca69bd852db`**. Do not modify or duplicate the image on the research branch.
- Bass reference: user-provided **17 screenshots**, visible measure coverage **1–113**; frozen set SHA256 **`abd1748066966ceb93fe40bf8c8df3168f6c871ba006e44d28f8840184e3cde3`**. Receipt: `debug/v154-cpu-autonomous/reference-receipts/bass-user-upload-20260827.json`; receipt Git blob **`0cd7a2e451ae4ea17b4ba15e6c2e2508f27518fd`**. The visible measure-88 `Timing mishap here` annotation remains an uncertainty flag; do not silently repair it in the reference.
- Lead reference: user-provided **22 screenshots**, visible measure coverage **1–113**, opening tempo **quarter = 129**, time signature **4/4**; frozen set SHA256 **`de2f20c330e52aca6125e29ca2cf5c4b719406fc267a98d43d98f3ab1453ff3c`**. Receipt: `debug/v154-cpu-autonomous/reference-receipts/lead-user-upload-20260827.json`; receipt Git blob **`e4cfa0a3c1f9c53bcdcb5b6ae8d73f9def5f7937`**. A visible `Probably a mistake they left in` annotation near measures 39–40 remains an uncertainty flag; green UI selection highlights are interface overlays, not notation.
- Three-part identity manifest: `debug/v154-cpu-autonomous/reference-receipts/reference-set-manifest-20260827.json`; creation commit **`4eae3fa541c1cbede282db20c113a22f7b906fbb`**.
- Reference-use boundary remains strict: **candidate generation/transcription cannot read Rhythm, Bass, or Lead references. Freeze candidate outputs first; open normalized references only at the scoring boundary. No post-score retuning of the scored candidate and no silent variant search.**
- Copyright/storage boundary: user-uploaded Bass/Lead screenshot bytes and derived note-by-note reference data remain private/ephemeral and are not committed to the public repo. Public repo may keep only scorer logic, schemas, hashes/manifests, uncertainty flags, and aggregate results.
- Target architecture remains **CPU-only, no human correction**: source separation -> broad `Other` stem for combined Rhythm+Lead -> combined guitar note/onset transcription -> musical Rhythm/Lead role separation -> string/fret assignment -> technique inference -> PDF; Bass remains an independent stem/transcription/scoring path.
- Modal/L4/CUDA/GPU execution still requires fresh explicit user authorization; CPU work/scoring is at assistant discretion. `main` and Production remain untouched.

### Next exact scientific steps
1. Normalize the three frozen references into the V154 scoring contract **privately/ephemerally**, preserving blank measures, rests, bends/slides/techniques where the scorer can represent them, and all uncertainty annotations.
2. Before opening any normalized reference during scoring, preregister the **broad-Other CPU benchmark**: frozen source-separation model/settings, frozen note-transcriber/settings, timing grid, matching tolerance, and hard success gates.
3. Execute CPU source separation with **Other = combined guitar acoustic source** and Bass separate; no attempt to acoustically separate Rhythm from Lead first.
4. Freeze the combined-guitar and Bass transcription outputs before reference access.
5. Score **combined guitar recognition first** against the union of Rhythm+Lead, using timing-aware pitch F1 (primary ±0.5 grid step; gross ±2 diagnostic). This decides whether the acoustic frontend actually hears the guitar notes.
6. Score Bass independently with the same timing-aware note metrics.
7. Only after note recognition is frozen, perform reference-free musical Rhythm/Lead role separation and score conditional role accuracy.
8. Only after notes+roles are stable, assign strings/frets and techniques and score position/technique accuracy.
9. Generate/evaluate professional PDF only after transcription gates are met; notation quality must not hide upstream recognition errors.
10. Do not resume one-event Gold-guided V153-style micro-correction as the main path. V154 is an architecture benchmark/reset, not another candidate tweak.
