#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_MANIFEST = Path('/tmp/gomyway-full-song-v7-measure-grid-proof-manifest.json')


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f'Required manifest not found: {path}')
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'Expected JSON object in {path}')
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', default=str(DEFAULT_MANIFEST))
    args = parser.parse_args()

    manifest = load_json(Path(args.manifest))
    pdf_path = Path(str(manifest.get('outputPdf') or ''))
    checks = {
        'proofPassed': manifest.get('passed') is True,
        'sourceMeasureGridPassed': manifest.get('sourceMeasureGridPassed') is True,
        'fourFourPreserved': int(manifest.get('beatsPerMeasure') or 0) == 4,
        'sixMeasuresPerRowPreserved': int(manifest.get('measuresPerRow') or 0) == 6,
        'all113MeasuresPreserved': int(manifest.get('measureCount') or 0) == 113,
        'all19RowsRendered': int(manifest.get('rowCount') or 0) == 19,
        'fiveProofPagesPresent': int(manifest.get('pageCount') or 0) == 5,
        'all103MarkersPreserved': int(manifest.get('markerCount') or 0) == 103,
        'all143FragmentsRendered': int(manifest.get('fragmentCount') or 0) == 143,
        'proofPdfExists': pdf_path.is_file(),
        'proofPdfNonEmpty': pdf_path.is_file() and pdf_path.stat().st_size > 2000,
        'productionEventsUnaffected': manifest.get('affectsProductionEvents') is False,
        'generatedTabUnaffected': manifest.get('affectsGeneratedTab') is False,
        'productionPdfUnaffected': manifest.get('affectsProductionPdf') is False,
        'protectedBaselinesUnchanged': manifest.get('protectedBaselinesChanged') is False,
    }

    print('JIMMY PAIGE V7 MEASURE-GRID PROOF PDF GUARD')
    print('=' * 72)
    for name, passed in checks.items():
        print('PASS' if passed else 'FAIL', name)
    print('Tempo:', manifest.get('tempoBpm'), 'BPM')
    print('Measures:', manifest.get('measureCount'))
    print('Rows:', manifest.get('rowCount'))
    print('Pages:', manifest.get('pageCount'))
    print('Markers:', manifest.get('markerCount'))
    print('Fragments:', manifest.get('fragmentCount'))
    print('Proof PDF:', pdf_path)

    if not all(checks.values()):
        raise SystemExit('\nV7 measure-grid proof PDF regression detected. Do not integrate.')

    print('\nV7 MEASURE-GRID PROOF PDF PRESERVED 💚')
    print('All 113 measures render in 4/4 with six measures per row.')
    print('All 143 barline-aware notation fragments remain read-only.')
    print('Production events, generated tab, and real PDF rendering remain untouched.')


if __name__ == '__main__':
    main()
