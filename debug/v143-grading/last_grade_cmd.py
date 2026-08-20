	 python - <<'PY'
from pathlib import Path
import json
import re

CAL = Path("public/training/v143-musical-reconstruction-calibration")

candidate_path = (
    CAL /
    "fresh-17-96-correlation-safe-fixed-count-reranker-frozen-events.json"
)
reference_path = Path(
    "public/gomyway-professional-rhythm-reference-17-113.json"
)

candidate = json.loads(candidate_path.read_text(encoding="utf-8"))

pred = {
    (int(event["measure"]), int(event["step"]))
    for event in candidate["events"]
}

# Read reference only through measure 96.
# Stop immediately when the measure-97 header is encountered.
ref = set()
current_measure = None
hit_reserve_boundary = False

with reference_path.open("r", encoding="utf-8") as fh:
    for line in fh:
        match_measure = re.search(
            r'"measureNumber"\s*:\s*(\d+)',
            line,
        )

        if match_measure:
            current_measure = int(match_measure.group(1))

            if current_measure >= 97:
                hit_reserve_boundary = True
                break

        match_step = re.search(
            r'"quantizedStep"\s*:\s*(\d+)',
            line,
        )

        if (
            match_step
            and current_measure is not None
            and 17 <= current_measure <= 96
        ):
            ref.add(
                (
                    current_measure,
                    int(match_step.group(1)),
                )
            )

if len(pred) != 765:
    raise RuntimeError(
        f"Frozen candidate count mismatch: {len(pred)} != 765"
    )

if len(ref) != 433:
    raise RuntimeError(
        f"Reference parser mismatch: {len(ref)} != 433"
    )

if not hit_reserve_boundary:
    raise RuntimeError(
        "Did not encounter measure-97 boundary; refusing grade"
    )

def metrics(predicted, reference):
    tp = len(predicted & reference)
    fp = len(predicted - reference)
    fn = len(reference - predicted)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return tp, fp, fn, precision, recall, f1

base_benchmark = {
    (17, 32): (65, 71, 50),
    (33, 48): (72, 101, 21),
    (49, 64): (75, 59, 35),
    (65, 80): (37, 120, 13),
    (81, 96): (54, 111, 11),
}

print("=== V143 FIXED-COUNT BLIND GRADE 17-96 ===")
print("Frozen candidate events:", len(pred))
print("Reference events:", len(ref))
print("97-113 event payload opened: False")
print()

for lo, hi in base_benchmark:
    p = {x for x in pred if lo <= x[0] <= hi}
    r = {x for x in ref if lo <= x[0] <= hi}

    tp, fp, fn, precision, recall, f1 = metrics(p, r)

    btp, bfp, bfn = base_benchmark[(lo, hi)]
    bp = btp / (btp + bfp)
    br = btp / (btp + bfn)
    bf1 = 2 * bp * br / (bp + br)

    print(
        f"{lo}-{hi}: "
        f"N={len(p)} REF={len(r)} "
        f"TP/FP/FN={tp}/{fp}/{fn} "
        f"P={precision:.4f} R={recall:.4f} F1={f1:.4f} "
        f"BASE={bf1:.4f} DELTA={f1-bf1:+.4f}"
    )

tp, fp, fn, precision, recall, f1 = metrics(pred, ref)

base_tp, base_fp, base_fn = 303, 462, 130
base_precision = base_tp / (base_tp + base_fp)
base_recall = base_tp / (base_tp + base_fn)
base_f1 = (
    2 * base_precision * base_recall /
    (base_precision + base_recall)
)

print()
print("=== COMBINED 17-96 ===")
print(
    f"FIXED COUNT N={len(pred)} REF={len(ref)} "
    f"TP/FP/FN={tp}/{fp}/{fn} "
    f"P={precision:.4f} R={recall:.4f} F1={f1:.4f}"
)
print(f"BASE 0.27 F1: {base_f1:.4f}")
print(f"FIXED-COUNT DELTA VS BASE: {f1-base_f1:+.4f}")
print("OLD SEQUENCE F1: 0.4973")
print("97-113 event payload opened: False")
PY

