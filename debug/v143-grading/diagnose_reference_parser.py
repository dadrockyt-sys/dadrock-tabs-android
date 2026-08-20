#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
import re

REFERENCE = Path("public/gomyway-professional-rhythm-reference-17-113.json")
EXPECTED_TOTAL = 433
EXPECTED_BANDS = {
    (17, 32): 115,
    (33, 48): 93,
    (49, 64): 110,
    (65, 80): 50,
    (81, 96): 65,
}

measure_re = re.compile(r'"measureNumber"\s*:\s*(\d+)')
strict_step_re = re.compile(r'"quantizedStep"\s*:\s*(\d+)')
raw_step_re = re.compile(r'"quantizedStep"\s*:\s*([^,}\s]+)')

current_measure = None
hit_reserve_boundary = False
raw_occurrences = []
strict_pairs = []
rejected_tokens = []
measure_transitions = []

with REFERENCE.open("r", encoding="utf-8") as fh:
    for line_no, line in enumerate(fh, 1):
        mm = measure_re.search(line)
        if mm:
            current_measure = int(mm.group(1))
            measure_transitions.append((line_no, current_measure))
            if current_measure >= 97:
                hit_reserve_boundary = True
                break

        raw = raw_step_re.search(line)
        strict = strict_step_re.search(line)

        if raw and current_measure is not None and 17 <= current_measure <= 96:
            token = raw.group(1)
            raw_occurrences.append((current_measure, token, line_no))
            if not strict:
                rejected_tokens.append((current_measure, token, line_no))

        if strict and current_measure is not None and 17 <= current_measure <= 96:
            strict_pairs.append((current_measure, int(strict.group(1)), line_no))

pair_counts = Counter((m, s) for m, s, _ in strict_pairs)
unique_pairs = set(pair_counts)
duplicates = sorted((pair, count) for pair, count in pair_counts.items() if count > 1)

raw_by_measure = Counter(m for m, _, _ in raw_occurrences)
strict_by_measure = Counter(m for m, _, _ in strict_pairs)
unique_by_measure = Counter(m for m, _ in unique_pairs)

print("=== V143 REFERENCE PARSER DIAGNOSTIC ===")
print(f"reserve_boundary_seen={hit_reserve_boundary}")
print("reserve_payload_opened=False")
print(f"raw_quantizedStep_occurrences_17_96={len(raw_occurrences)}")
print(f"strict_integer_occurrences_17_96={len(strict_pairs)}")
print(f"unique_measure_step_pairs_17_96={len(unique_pairs)}")
print(f"expected_reference_pairs={EXPECTED_TOTAL}")
print(f"duplicate_pair_count={len(duplicates)}")
print(f"rejected_token_count={len(rejected_tokens)}")
print()

if duplicates:
    print("DUPLICATE MEASURE/STEP PAIRS")
    for (measure, step), count in duplicates:
        lines = [ln for m, s, ln in strict_pairs if m == measure and s == step]
        print(f"  measure={measure} step={step} count={count} lines={lines}")
    print()

if rejected_tokens:
    print("NON-STRICT quantizedStep TOKENS")
    for measure, token, line_no in rejected_tokens:
        print(f"  measure={measure} token={token!r} line={line_no}")
    print()

print("BAND COUNTS")
for (lo, hi), expected in EXPECTED_BANDS.items():
    raw_count = sum(c for m, c in raw_by_measure.items() if lo <= m <= hi)
    strict_count = sum(c for m, c in strict_by_measure.items() if lo <= m <= hi)
    unique_count = sum(c for m, c in unique_by_measure.items() if lo <= m <= hi)
    print(
        f"  {lo}-{hi}: raw={raw_count} strict={strict_count} "
        f"unique={unique_count} expected={expected} delta={unique_count - expected:+d}"
    )
print()

print("MEASURE COUNTS (only mismatches raw/strict/unique shown)")
for measure in range(17, 97):
    raw_count = raw_by_measure[measure]
    strict_count = strict_by_measure[measure]
    unique_count = unique_by_measure[measure]
    if not (raw_count == strict_count == unique_count):
        print(
            f"  measure={measure}: raw={raw_count} strict={strict_count} unique={unique_count}"
        )

print()
if not hit_reserve_boundary:
    raise SystemExit("FAIL: measure-97 boundary was not encountered")
if len(unique_pairs) == EXPECTED_TOTAL:
    print("RESULT=PASS: parser yields the expected 433 unique measure/step pairs")
elif len(strict_pairs) == EXPECTED_TOTAL and len(unique_pairs) != EXPECTED_TOTAL:
    print("RESULT=ROOT_CAUSE: all 433 strict events are present but set() collapses duplicate measure/step pairs")
elif len(raw_occurrences) == EXPECTED_TOTAL and len(strict_pairs) != EXPECTED_TOTAL:
    print("RESULT=ROOT_CAUSE: 433 raw events exist but strict integer regex rejects one or more quantizedStep encodings")
else:
    print("RESULT=REFERENCE_COUNT_MISMATCH: committed 17-96 payload does not expose 433 events under either parser")
