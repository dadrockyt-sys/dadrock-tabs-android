"""Joint one-to-one exact-MIDI onset scoring across multiple requested guitar roles."""
from __future__ import annotations

import math


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _normalize_rows(rows, *, role, start, end):
    require(isinstance(rows, list), f'{role} targets must be a list')
    out = []
    ids = set()
    for index, row in enumerate(rows):
        require(isinstance(row, dict), f'{role} target must be an object')
        identity = row.get('id', f'{role}-{index}')
        require(isinstance(identity, str) and identity and identity not in ids, f'{role} target IDs must be unique')
        ids.add(identity)
        midi = row.get('midi')
        onset = row.get('start')
        require(isinstance(midi, int) and not isinstance(midi, bool) and 0 <= midi <= 127, 'Invalid target MIDI')
        require(_finite(onset) and onset >= 0, 'Invalid target onset')
        if start <= onset < end:
            out.append({'id': identity, 'midi': midi, 'start': float(onset), 'role': role})
    return out


def _normalize_predictions(rows, *, start, end):
    require(isinstance(rows, list), 'predictions must be a list')
    out = []
    ids = set()
    for index, row in enumerate(rows):
        require(isinstance(row, dict), 'prediction must be an object')
        identity = row.get('id', str(index))
        require(isinstance(identity, str) and identity and identity not in ids, 'Prediction IDs must be unique')
        ids.add(identity)
        midi = row.get('midi')
        onset = row.get('start')
        require(isinstance(midi, int) and not isinstance(midi, bool) and 0 <= midi <= 127, 'Invalid prediction MIDI')
        require(_finite(onset) and onset >= 0, 'Invalid prediction onset')
        if start <= onset < end:
            out.append({'id': identity, 'midi': midi, 'start': float(onset)})
    return out


def _score(predicted, reference, tolerance):
    matches = []
    for midi in sorted({r['midi'] for r in reference}):
        ps = sorted((p for p in predicted if p['midi'] == midi), key=lambda p: (p['start'], p['id']))
        rs = sorted((r for r in reference if r['midi'] == midi), key=lambda r: (r['start'], r['id']))
        table = [[(0, 0.0, ()) for _ in range(len(rs) + 1)] for _ in range(len(ps) + 1)]
        for i, p in enumerate(ps, 1):
            for j, r in enumerate(rs, 1):
                choices = [table[i - 1][j], table[i][j - 1]]
                delta = abs(p['start'] - r['start'])
                if delta <= tolerance:
                    count, cost, pairs = table[i - 1][j - 1]
                    choices.append((count + 1, cost + delta, pairs + ((p['id'], r['id'], p['start'] - r['start']),)))
                table[i][j] = min(choices, key=lambda x: (-x[0], x[1], x[2]))
        matches.extend(table[-1][-1][2])
    return matches


def score_role_aware_note_onsets(predictions, targets_by_role, *, start, end, tolerance):
    require(all(_finite(x) for x in (start, end, tolerance)) and 0 <= start < end and tolerance >= 0,
            'Invalid scoring window or tolerance')
    require(isinstance(targets_by_role, dict) and targets_by_role, 'targets_by_role must be a non-empty object')

    predicted = _normalize_predictions(predictions, start=start, end=end)
    reference = []
    role_targets = {}
    global_ids = set()
    for role in sorted(targets_by_role):
        require(isinstance(role, str) and role, 'role names must be non-empty strings')
        rows = _normalize_rows(targets_by_role[role], role=role, start=start, end=end)
        for row in rows:
            require(row['id'] not in global_ids, 'Target IDs must be globally unique across roles')
            global_ids.add(row['id'])
        role_targets[role] = rows
        reference.extend(rows)

    collisions = []
    roles = sorted(role_targets)
    for i, left_role in enumerate(roles):
        for right_role in roles[i + 1:]:
            for left in role_targets[left_role]:
                for right in role_targets[right_role]:
                    if left['midi'] == right['midi'] and abs(left['start'] - right['start']) <= tolerance:
                        collisions.append({
                            'leftRole': left_role, 'leftId': left['id'],
                            'rightRole': right_role, 'rightId': right['id'],
                            'midi': left['midi'],
                            'onsetDeltaSeconds': left['start'] - right['start'],
                        })
    require(not collisions, 'AMBIGUOUS_CROSS_ROLE_TARGET_COLLISION')

    matches = _score(predicted, reference, tolerance)
    target_by_id = {row['id']: row for row in reference}
    joint_matches = [{
        'predictionId': prediction_id,
        'targetId': target_id,
        'role': target_by_id[target_id]['role'],
        'midi': target_by_id[target_id]['midi'],
        'signedOnsetErrorSeconds': signed_error,
    } for prediction_id, target_id, signed_error in matches]

    tp = len(matches)
    fp = len(predicted) - tp
    fn = len(reference) - tp
    by_role = {}
    for role in roles:
        role_tp = sum(1 for row in joint_matches if row['role'] == role)
        role_count = len(role_targets[role])
        by_role[role] = {
            'targets': role_count,
            'tp': role_tp,
            'fn': role_count - role_tp,
            'recall': role_tp / role_count if role_count else None,
        }

    return {
        'predictions': len(predicted),
        'targets': len(reference),
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'precision': tp / len(predicted) if predicted else None,
        'recall': tp / len(reference) if reference else None,
        'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
        'meanAbsoluteOnsetErrorSeconds': sum(abs(row['signedOnsetErrorSeconds']) for row in joint_matches) / tp if tp else None,
        'byRole': by_role,
        'crossRoleCollisionCount': 0,
        'matches': joint_matches,
    }
