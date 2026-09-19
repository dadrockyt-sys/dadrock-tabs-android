"""One-to-one exact-MIDI onset scoring; no alignment search or model access."""
import math


def score_note_onsets(predictions, targets, *, start, end, tolerance):
    if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
               for x in (start, end, tolerance)) or start < 0 or end <= start or tolerance < 0:
        raise ValueError('Invalid scoring window or tolerance')

    def normalize(rows):
        output = []
        ids = set()
        for index, row in enumerate(rows):
            midi, onset = row.get('midi'), row.get('start')
            identity = row.get('id', str(index))
            if not isinstance(identity, str) or not identity or identity in ids:
                raise ValueError('IDs must be unique nonempty strings')
            ids.add(identity)
            if isinstance(midi, bool) or not isinstance(midi, int) or not 0 <= midi <= 127:
                raise ValueError('Invalid MIDI')
            if isinstance(onset, bool) or not isinstance(onset, (int, float)) or not math.isfinite(onset) or onset < 0:
                raise ValueError('Invalid onset')
            if start <= onset < end:
                output.append({'id': identity, 'midi': midi, 'start': onset})
        return output

    predicted, reference = normalize(predictions), normalize(targets)
    matches = []
    # Ordered matching per exact pitch. Maximize count, then minimize total onset error.
    # Sorted 1-D absolute-distance matching admits an optimal noncrossing solution.
    for midi in sorted({r['midi'] for r in reference}):
        ps = sorted((p for p in predicted if p['midi'] == midi), key=lambda p: (p['start'], p['id']))
        rs = sorted((r for r in reference if r['midi'] == midi), key=lambda r: (r['start'], r['id']))
        table = [[(0, 0.0, ()) for _ in range(len(rs)+1)] for _ in range(len(ps)+1)]
        for i, p in enumerate(ps, 1):
            for j, r in enumerate(rs, 1):
                choices = [table[i-1][j], table[i][j-1]]
                delta = abs(p['start'] - r['start'])
                if delta <= tolerance:
                    count, cost, pairs = table[i-1][j-1]
                    choices.append((count+1, cost+delta, pairs+((p['id'], r['id'], p['start']-r['start']),)))
                table[i][j] = min(choices, key=lambda x: (-x[0], x[1], x[2]))
        matches.extend(table[-1][-1][2])
    tp = len(matches)
    fp, fn = len(predicted)-tp, len(reference)-tp
    return {'predictions': len(predicted), 'targets': len(reference), 'tp': tp, 'fp': fp, 'fn': fn,
            'precision': tp/len(predicted) if predicted else None,
            'recall': tp/len(reference) if reference else None,
            'f1': 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,
            'meanAbsoluteOnsetErrorSeconds': sum(abs(m[2]) for m in matches)/tp if tp else None,
            'matches': [{'predictionId': p, 'targetId': r, 'signedOnsetErrorSeconds': d} for p,r,d in matches]}
