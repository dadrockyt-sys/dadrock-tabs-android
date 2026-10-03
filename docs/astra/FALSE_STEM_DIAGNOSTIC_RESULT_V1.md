# False-Stem Diagnostic Result V1

Date: 2026-10-02
Run ID: 37084524274
Status: SUCCESSFUL DIAGNOSTIC PASS

Artifact:
- id: 11260511674
- digest: `sha256:d7960c731d3815f49654bc1edec3aacaf9cf64232c535bc03e0ed016779f4470`

## Known absent-target cases

Four guitar/bass claims are known absent in the frozen S0 truth:

- S0M07 bass: effectively silent, ~6.36e-12 mean-square energy, YAMNet guitar=0, bass=0
- S0M08 guitar: effectively silent, ~6.74e-12, YAMNet guitar=0, bass=0
- S0M09 bass: effectively silent, ~2.77e-12, YAMNet guitar=0, bass=0
- S0M10 guitar: substantial false stem, ~0.00493 energy, YAMNet guitar=0.2053, bass=0.2171

The first three are trivial near-silent false outputs and require no destructive cleanup.

## S0M10 hard false-stem pattern

S0M10 guitar:
- target actually absent
- guitar evidence 0.2053
- bass evidence 0.2171
- bass wins by only 0.01175
- energy 0.00493

S0M10 bass:
- target actually present
- guitar evidence 0.1513
- bass evidence 0.2018
- bass wins by 0.05048
- energy 0.00412

The two stems therefore:
- are both bass-leaning;
- have similar energy (guitar false stem is only ~0.79 dB above the bass stem);
- identify each other as strongest overlap competitors.

This is qualitatively different from the strongest successful dual guitar+bass fixtures, where the pair is usually complementary:
- S0M01 guitar strongly guitar-leaning, bass bass-leaning;
- S0M02 guitar guitar-leaning, bass bass-leaning;
- S0M05 guitar guitar-leaning, bass bass-leaning;
- S0M06 guitar guitar-leaning, bass bass-leaning.

## Important counterexamples

Pair-level rules must remain conservative:
- S0M03 guitar is a real target but almost entirely missed and has zero YAMNet evidence.
- S0M11 bass is a real target but almost entirely missed and has zero evidence.
- S0M12 bass is real but slightly guitar-leaning (0.3390 vs 0.3313).
- S0M12 guitar is real but extremely low-evidence.

Therefore a pair detector must distinguish:
- duplicate-class conflict, where both substantial outputs favor the same class;
- missing-target uncertainty, where one stem is near-silent;
- ambiguous but legitimate pairs.

## Decision

Do not reassign audio yet.

Next experiment: a pair-level duplicate-class detector that reports:
1. guitar/bass evidence winner for each of the two stems;
2. absolute string evidence for each;
3. energy balance between the two stems;
4. mutual-overlap relationship;
5. one of:
   - complementary_pair
   - duplicate_guitar_candidate
   - duplicate_bass_candidate
   - missing_or_silent_member
   - ambiguous_pair

The first pass must remain diagnostic only. S0M10 should be tested as the key duplicate-bass-pattern case, while S0M03, S0M11 and S0M12 protect against destructive false positives.
