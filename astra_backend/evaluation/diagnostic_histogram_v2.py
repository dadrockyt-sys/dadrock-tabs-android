"""Correct-direction histogram ROC/PR metrics; stdlib only, no inference.

Bins are ascending score. Ties within a bin enter together. PR trapezoidal area
and step average precision are distinct and explicitly named. Frozen V5 reports
remain unchanged; their negative AUPRC is not rehabilitated by this helper.
"""
import math


def finalize_hist(acc):
    pos, neg = list(acc["pos"]), list(acc["neg"])
    if not pos or len(pos) != len(neg):
        raise ValueError("histograms must have equal nonzero length")
    for value in pos + neg:
        if isinstance(value, bool) or not math.isfinite(value) or value < 0 or int(value) != value:
            raise ValueError("histogram counts must be nonnegative integers")
    p_total, n_total = int(sum(pos)), int(sum(neg))
    tp = fp = 0
    last_recall, last_fpr, last_precision = 0.0, 0.0, 1.0
    roc = pr = ap = 0.0
    for p, n in zip(reversed(pos), reversed(neg)):
        if not p + n:
            continue
        tp += p
        fp += n
        recall = tp / p_total if p_total else 0.0
        fpr = fp / n_total if n_total else 0.0
        precision = tp / (tp + fp)
        roc += (fpr - last_fpr) * (recall + last_recall) / 2
        pr += (recall - last_recall) * (precision + last_precision) / 2
        ap += (recall - last_recall) * precision
        last_recall, last_fpr, last_precision = recall, fpr, precision
    out = {
        "schema": "astra-histogram-metrics-v2", "bins": len(pos),
        "positiveCount": p_total, "negativeCount": n_total,
        "approxAUROC": roc if p_total and n_total else None,
        "approxAUPRCTrapezoid": pr if p_total else None,
        "approxAveragePrecision": ap if p_total else None,
    }
    for name in ("approxAUROC", "approxAUPRCTrapezoid", "approxAveragePrecision"):
        if out[name] is not None and not 0 <= out[name] <= 1 + 1e-12:
            raise ValueError("invalid area")
    return out
