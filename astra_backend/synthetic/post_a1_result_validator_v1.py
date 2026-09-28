#!/usr/bin/env python3
"""Pure-Python prospective result validator for post-A1 experiments.

This helper does not import torch or instantiate models. It validates normalized
result JSON structure before any scientific gate is interpreted.
"""
from __future__ import annotations

import json
import math
import numbers
from pathlib import Path

FRACTION_KEYS = {
    "stateAdmission",
    "jointAdmission",
    "onsetPrecision",
    "onsetRecall",
    "onsetF1",
}


class ValidationError(ValueError):
    pass


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise ValidationError(f"{label}: expected real number, not boolean/non-number")
    value = float(value)
    if not math.isfinite(value):
        raise ValidationError(f"{label}: non-finite")
    return value


def _fraction(value, label):
    value = _number(value, label)
    if not 0.0 <= value <= 1.0:
        raise ValidationError(f"{label}: fraction outside [0,1]")
    return value


def validate_result(
    result,
    *,
    expected_schema,
    expected_seeds,
    expected_steps_per_model,
    expected_model_count,
    expected_total_steps,
    expected_identities,
):
    if not isinstance(result, dict):
        raise ValidationError("result must be object")
    if result.get("schema") != expected_schema:
        raise ValidationError("schema mismatch")
    if result.get("identities") != expected_identities:
        raise ValidationError("identity mismatch")

    rows = result.get("rows")
    if not isinstance(rows, list):
        raise ValidationError("rows must be list")
    seeds = [r.get("seed") for r in rows if isinstance(r, dict)]
    if len(rows) != len(expected_seeds) or len(seeds) != len(rows):
        raise ValidationError("row count mismatch")
    if any(isinstance(s, bool) or not isinstance(s, int) for s in seeds):
        raise ValidationError("seed must be integer")
    if len(set(seeds)) != len(seeds):
        raise ValidationError("duplicate seed")
    if set(seeds) != set(expected_seeds):
        raise ValidationError("missing or extra seed")

    for row in rows:
        seed = row["seed"]
        steps = row.get("optimizerSteps")
        if isinstance(steps, bool) or not isinstance(steps, int) or steps != expected_steps_per_model:
            raise ValidationError(f"seed {seed}: optimizerSteps mismatch")

        for domain in ("ordinary", "challenge"):
            block = row.get(domain)
            if not isinstance(block, dict):
                raise ValidationError(f"seed {seed} {domain}: missing block")
            cand = block.get("candidate")
            comp = block.get("comparator")
            delta = block.get("delta")
            if not all(isinstance(x, dict) for x in (cand, comp, delta)):
                raise ValidationError(
                    f"seed {seed} {domain}: candidate/comparator/delta required"
                )

            for key in FRACTION_KEYS:
                cv = _fraction(cand.get(key), f"seed {seed} {domain} candidate {key}")
                bv = _fraction(comp.get(key), f"seed {seed} {domain} comparator {key}")
                dv = _number(delta.get(key), f"seed {seed} {domain} delta {key}")
                if not math.isclose(dv, cv - bv, rel_tol=0.0, abs_tol=1e-12):
                    raise ValidationError(
                        f"seed {seed} {domain}: inconsistent delta {key}"
                    )

            for who, metrics in (("candidate", cand), ("comparator", comp)):
                count = metrics.get("negativeFpEvents")
                seconds = _number(
                    metrics.get("negativeSeconds"),
                    f"seed {seed} {domain} {who} negativeSeconds",
                )
                rate = _number(
                    metrics.get("negativeFpPerSecond"),
                    f"seed {seed} {domain} {who} negativeFpPerSecond",
                )
                if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                    raise ValidationError(
                        f"seed {seed} {domain} {who}: invalid negativeFpEvents"
                    )
                if seconds <= 0 or rate < 0:
                    raise ValidationError(
                        f"seed {seed} {domain} {who}: invalid negative duration/rate"
                    )
                if not math.isclose(rate, count / seconds, rel_tol=0.0, abs_tol=1e-12):
                    raise ValidationError(
                        f"seed {seed} {domain} {who}: inconsistent negative FP rate"
                    )

    execution = result.get("execution")
    if not isinstance(execution, dict):
        raise ValidationError("execution missing")

    model_count = execution.get("modelCount")
    total_steps = execution.get("optimizerStepsTotal")
    if (
        isinstance(model_count, bool)
        or not isinstance(model_count, int)
        or model_count != expected_model_count
    ):
        raise ValidationError("modelCount mismatch")
    if (
        isinstance(total_steps, bool)
        or not isinstance(total_steps, int)
        or total_steps != expected_total_steps
    ):
        raise ValidationError("optimizerStepsTotal mismatch")
    if total_steps != sum(r["optimizerSteps"] for r in rows):
        raise ValidationError("optimizerStepsTotal inconsistent with rows")

    return True


def validate_file(path, **kwargs):
    return validate_result(json.loads(Path(path).read_text()), **kwargs)
