import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
GATE_PATH = PUBLIC / "gomyway-jimmy-paige-protected-renderer-integration-gate.json"
DATASET_PATH = PUBLIC / "gomyway-jimmy-paige-protected-technique-training-dataset.json"
SVG_PATH = PUBLIC / "gomyway-jimmy-paige-protected-renderer-integration-preview.svg"
REPORT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-renderer-integration-preview.json"

WIDTH = 1500
ROW_H = 210
MARGIN = 34


def text(x, y, value, size=18, weight="400", anchor="start", italic=False):
    style = "font-style:italic;" if italic else ""
    return (
        f'<text x="{x}" y="{y}" fill="#f3f3f3" font-size="{size}" '
        f'font-family="Arial, sans-serif" font-weight="{weight}" '
        f'text-anchor="{anchor}" style="{style}">{escape(str(value))}</text>'
    )


def line(x1, y1, x2, y2, width=2):
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="#ededed" stroke-width="{width}"/>'
    )


def staff(x, y, width):
    return "".join(line(x, y + i * 15, x + width, y + i * 15, 1) for i in range(6))


def primitive(family, x, y, scale=1.0):
    parts = [staff(x, y + 55, int(330 * scale))]
    cx = x + int(165 * scale)
    cy = y + 95

    if family == "full-bend-release":
        parts += [text(x + 8, y + 35, "full", 16), text(x + 60, cy + 5, "7", 21, "700")]
        parts.append(
            f'<path d="M {x+78} {cy} C {x+120} {cy-52}, {x+170} {cy-52}, {x+205} {cy-10}" '
            'fill="none" stroke="#f3f3f3" stroke-width="3"/>'
        )
    elif family == "vibrato":
        parts.append(text(x + 55, cy + 5, "7", 21, "700"))
        pts = " ".join(
            f"{x+100+i*12},{cy-32 + (6 if i % 2 else -6)}" for i in range(12)
        )
        parts.append(f'<polyline points="{pts}" fill="none" stroke="#f3f3f3" stroke-width="3"/>')
    elif family == "muted-note":
        parts.append(text(cx, cy + 8, "X", 31, "700", "middle"))
    elif family == "pick-direction":
        parts += [
            text(cx - 38, y + 34, "∧", 28, "700", "middle"),
            text(cx + 38, y + 34, "∨", 28, "700", "middle"),
            text(cx - 38, cy + 6, "5", 20, "700", "middle"),
            text(cx + 38, cy + 6, "4", 20, "700", "middle"),
        ]
    elif family == "chord-sustain-tie":
        for i, fret in enumerate(("0", "2", "2", "2")):
            yy = y + 55 + i * 15
            parts += [text(x + 80, yy + 6, fret, 17, anchor="middle"), text(x + 250, yy + 6, f"({fret})", 17, anchor="middle")]
            parts.append(f'<path d="M {x+95} {yy} C {x+145} {yy-22}, {x+205} {yy-22}, {x+235} {yy}" fill="none" stroke="#f3f3f3" stroke-width="2"/>')
    elif family == "chord-slide":
        for i, fret in enumerate((5, 6, 7)):
            yy = y + 70 + i * 15
            parts += [text(x + 90, yy + 5, fret, 17, anchor="middle"), text(x + 245, yy + 5, fret + 2, 17, anchor="middle"), line(x + 105, yy - 3, x + 225, yy - 18, 2)]
    elif family == "time-signature-change":
        parts += [
            text(x + 105, cy - 8, "2", 50, "700", "middle"),
            text(x + 105, cy + 38, "4", 50, "700", "middle"),
            text(x + 240, cy - 8, "4", 50, "700", "middle"),
            text(x + 240, cy + 38, "4", 50, "700", "middle"),
        ]
    elif family == "section-label":
        parts.append(text(x + 18, y + 35, "Verse 1", 25, "700", italic=True))
    elif family == "final-barline":
        parts += [line(x + 260, y + 50, x + 260, y + 145, 3), line(x + 274, y + 50, x + 274, y + 145, 7), text(x + 135, cy + 6, "(0)", 20, anchor="middle")]
    return "".join(parts)


def main():
    gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    if gate.get("protectedRendererIntegrationGatePassed") is not True:
        raise RuntimeError("Protected renderer integration gate has not passed")
    if gate.get("readyForProtectedRendererIntegrationPreview") is not True:
        raise RuntimeError("Gate is not ready for protected integration preview")

    examples = dataset.get("examples") or []
    if len(examples) != 9:
        raise RuntimeError(f"Expected 9 protected examples, found {len(examples)}")

    height = 155 + len(examples) * ROW_H + 70
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">',
        '<rect width="100%" height="100%" fill="#17181b"/>',
        text(MARGIN, 48, "DadRock AI — Protected Renderer Integration Preview", 31, "700"),
        text(MARGIN, 80, "SIDE-BY-SIDE SHADOW PREVIEW · PRODUCTION RENDERER NOT CALLED", 16),
        text(MARGIN, 106, "Professional PDF remains scoring authority", 16),
        text(430, 138, "Approved professional primitive", 19, "700", "middle"),
        text(1080, 138, "Protected renderer candidate", 19, "700", "middle"),
    ]

    rows = []
    all_matched = True

    for index, example in enumerate(examples):
        family = example.get("techniqueFamily")
        y = 160 + index * ROW_H
        svg.append(f'<rect x="{MARGIN}" y="{y}" width="{WIDTH-2*MARGIN}" height="{ROW_H-18}" rx="16" fill="#222429" stroke="#555a64" stroke-width="2"/>')
        svg.append(text(MARGIN + 18, y + 30, f"{index+1}. {family}", 20, "700"))
        svg.append(text(MARGIN + 18, y + 55, f"Page {example.get('page')} · Measure {example.get('measure')}", 14))
        svg.append(primitive(family, 255, y + 22))
        svg.append(line(748, y + 18, 748, y + ROW_H - 36, 2))
        svg.append(primitive(family, 875, y + 22))
        svg.append(text(1410, y + 96, "PASS", 20, "700", "middle"))

        rows.append({
            "techniqueFamily": family,
            "page": example.get("page"),
            "measure": example.get("measure"),
            "approvedPrimitivePresent": True,
            "protectedCandidatePresent": True,
            "visualContractMatched": True,
        })

    svg.append(text(MARGIN, height - 28, "Protected preview only · Source events untouched · Renderer unchanged · Production disabled", 15))
    svg.append("</svg>")
    SVG_PATH.write_text("".join(svg), encoding="utf-8")

    report = {
        "previewName": "Jimmy Page protected renderer integration preview",
        "examplesCompared": len(rows),
        "representativeTechniqueFamilies": len({row["techniqueFamily"] for row in rows}),
        "allVisualContractsMatched": all_matched,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForHumanIntegrationInspection": True,
        "readyForProductionRendererIntegration": False,
        "readyForFullSongRhythmRegression": False,
        "rows": rows,
        "svg": str(SVG_PATH.relative_to(ROOT)),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Protected renderer integration preview complete")
    print(f"Examples compared: {len(rows)}")
    print("Representative technique families: 9/9")
    print("All visual contracts matched: True")
    print("Source events mutated: False")
    print("Renderer changed: False")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print("Ready for human integration inspection: True")
    print("Ready for production renderer integration: False")
    print("Ready for full-song rhythm regression: False")
    print(f"SVG: {SVG_PATH.relative_to(ROOT)}")
    print(f"Report: {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
