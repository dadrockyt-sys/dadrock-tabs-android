from pathlib import Path

TARGET = Path("lib/v7MeasureGridOverlay.js")

OLD_FUNCTION = r'''function bendRenderKey(fragment, marker, rowNumber, transcriptionType) {
  const sourceIndex =
    marker?.sourceEventIndex ??
    marker?.bendEventIndex ??
    fragment?.sourceEventIndex ??
    fragment?.bendEventIndex;
  const targetIndex =
    marker?.targetEventIndex ??
    marker?.releaseEventIndex ??
    fragment?.targetEventIndex ??
    fragment?.releaseEventIndex;
  const markerIndex = marker?.measureGridMarkerIndex ?? fragment?.markerIndex;
  const stringIndex = resolvedStringIndex(marker, fragment, transcriptionType);
  const bendFret = marker?.bendFret ?? fragment?.bendFret ?? '';
  const releaseFret = marker?.releaseFret ?? fragment?.releaseFret ?? '';

  if (sourceIndex != null || targetIndex != null) {
    return `events:${rowNumber}:${sourceIndex ?? ''}:${targetIndex ?? ''}:${stringIndex}`;
  }

  return [
    'marker',
    rowNumber,
    markerIndex ?? '',
    stringIndex,
    bendFret,
    releaseFret,
    finiteNumber(fragment?.rowStartRatio).toFixed(4),
    finiteNumber(fragment?.rowEndRatio).toFixed(4),
  ].join(':');
}
'''

NEW_FUNCTION = r'''function bendMusicalIdentity(fragment, marker, rowNumber, transcriptionType) {
  const stringIndex = resolvedStringIndex(marker, fragment, transcriptionType);
  const bendFret = cleanAscii(marker?.bendFret ?? fragment?.bendFret, '');
  const releaseFret = cleanAscii(marker?.releaseFret ?? fragment?.releaseFret, '');
  const startRatio = clamp(finiteNumber(fragment?.rowStartRatio), 0, 1);
  const endRatio = clamp(finiteNumber(fragment?.rowEndRatio), startRatio, 1);

  return {
    rowNumber,
    stringIndex,
    bendFret,
    releaseFret,
    startRatio,
    endRatio,
  };
}

function isSameMusicalBend(left, right) {
  if (!left || !right) return false;
  if (left.rowNumber !== right.rowNumber) return false;
  if (left.stringIndex !== right.stringIndex) return false;
  if (left.bendFret !== right.bendFret) return false;
  if (left.releaseFret !== right.releaseFret) return false;

  // Diagnostic adapters may emit two marker records for one physical bend.
  // Treat them as the same bend when their printable positions overlap.
  const startDistance = Math.abs(left.startRatio - right.startRatio);
  const endDistance = Math.abs(left.endRatio - right.endRatio);
  const overlaps =
    left.startRatio <= right.endRatio + 0.018 &&
    right.startRatio <= left.endRatio + 0.018;

  return overlaps && startDistance <= 0.035 && endDistance <= 0.055;
}
'''

OLD_STATE = "  const renderedBends = new Set();\n"
NEW_STATE = "  const renderedBends = [];\n"

OLD_LOOP = r'''      if (type === 'bend-release') {
        const key = bendRenderKey(fragment, marker, rowNumber, transcriptionType);
        if (renderedBends.has(key)) continue;
        renderedBends.add(key);

        drawBendRelease(
'''

NEW_LOOP = r'''      if (type === 'bend-release') {
        const identity = bendMusicalIdentity(
          fragment,
          marker,
          rowNumber,
          transcriptionType
        );
        if (renderedBends.some((bend) => isSameMusicalBend(bend, identity))) {
          continue;
        }
        renderedBends.push(identity);

        drawBendRelease(
'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label}; found {count}.")
    return source.replace(old, new, 1)


def main() -> None:
    if not TARGET.exists():
        raise FileNotFoundError(f"Target not found: {TARGET}")

    source = TARGET.read_text(encoding="utf-8")
    source = replace_once(source, OLD_FUNCTION, NEW_FUNCTION, "bendRenderKey block")
    source = replace_once(source, OLD_STATE, NEW_STATE, "renderedBends state")
    source = replace_once(source, OLD_LOOP, NEW_LOOP, "bend rendering loop")
    TARGET.write_text(source, encoding="utf-8")

    print("V7 bend musical-position deduplication applied successfully 💚")
    print("Protected: polished template, chord lanes, measure grid, events, and analyzer output.")


if __name__ == "__main__":
    main()
