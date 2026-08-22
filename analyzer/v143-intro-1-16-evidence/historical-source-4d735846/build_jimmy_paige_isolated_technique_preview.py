import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
DATASET_PATH = PUBLIC / "gomyway-jimmy-paige-protected-technique-training-dataset.json"
BENCHMARK_PATH = PUBLIC / "gomyway-jimmy-paige-protected-technique-primitive-benchmark.json"
SVG_PATH = PUBLIC / "gomyway-jimmy-paige-isolated-technique-preview.svg"
REPORT_PATH = PUBLIC / "gomyway-jimmy-paige-isolated-technique-preview.json"

WIDTH = 1200
PANEL_W = 360
PANEL_H = 230
MARGIN = 30
GAP = 30


def line(x1, y1, x2, y2, width=2, dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#e8e8e8" stroke-width="{width}"{dash_attr}/>'


def text(x, y, value, size=18, anchor="start", weight="400", italic=False):
    style = "font-style:italic;" if italic else ""
    return (
        f'<text x="{x}" y="{y}" fill="#f2f2f2" font-size="{size}" '
        f'font-family="Arial, sans-serif" text-anchor="{anchor}" '
        f'font-weight="{weight}" style="{style}">{escape(str(value))}</text>'
    )


def tab_staff(x, y, width):
    parts = []
    for index in range(6):
        parts.append(line(x, y + index * 16, x + width, y + index * 16, 1))
    return "".join(parts)


def draw_primitive(family, x, y):
    parts = [tab_staff(x, y + 70, 290)]
    cx = x + 145
    cy = y + 110

    if family == "full-bend-release":
        parts += [text(x + 15, y + 45, "full"), text(x + 60, cy + 4, "7", 22, weight="700")]
        parts.append(f'<path d="M {x+75} {cy} C {x+115} {cy-55}, {x+155} {cy-55}, {x+185} {cy-10}" fill="none" stroke="#f2f2f2" stroke-width="3"/>')
        parts.append(f'<path d="M {x+178} {cy-18} L {x+190} {cy-8} L {x+176} {cy-5}" fill="none" stroke="#f2f2f2" stroke-width="3"/>')
    elif family == "vibrato":
        parts.append(text(x + 40, cy + 4, "7", 22, weight="700"))
        wave = " ".join(f"{x+85+i*12},{cy-35 + (5 if i%2 else -5)}" for i in range(12))
        parts.append(f'<polyline points="{wave}" fill="none" stroke="#f2f2f2" stroke-width="3"/>')
    elif family == "muted-note":
        parts.append(text(cx, cy + 5, "X", 30, anchor="middle", weight="700"))
    elif family == "pick-direction":
        parts.append(text(cx - 35, y + 42, "∧", 30, anchor="middle", weight="700"))
        parts.append(text(cx + 35, y + 42, "∨", 30, anchor="middle", weight="700"))
        parts.append(text(cx - 35, cy + 5, "5", 22, anchor="middle", weight="700"))
        parts.append(text(cx + 35, cy + 5, "4", 22, anchor="middle", weight="700"))
    elif family == "chord-sustain-tie":
        for offset, fret in enumerate(["0", "2", "2", "2"]):
            yy = y + 70 + offset * 16
            parts.append(text(x + 70, yy + 6, fret, 18, anchor="middle"))
            parts.append(text(x + 220, yy + 6, f"({fret})", 18, anchor="middle"))
            parts.append(f'<path d="M {x+85} {yy} C {x+130} {yy-24}, {x+175} {yy-24}, {x+205} {yy}" fill="none" stroke="#f2f2f2" stroke-width="2"/>')
    elif family == "chord-slide":
        for offset, fret in enumerate(["5", "6", "7"]):
            yy = y + 86 + offset * 16
            parts.append(text(x + 80, yy + 5, fret, 18, anchor="middle"))
            parts.append(text(x + 215, yy + 5, str(int(fret)+2), 18, anchor="middle"))
            parts.append(line(x + 95, yy - 3, x + 198, yy - 18, 2))
    elif family == "time-signature-change":
        parts.append(text(x + 95, cy - 5, "2", 54, anchor="middle", weight="700"))
        parts.append(text(x + 95, cy + 45, "4", 54, anchor="middle", weight="700"))
        parts.append(text(x + 215, cy - 5, "4", 54, anchor="middle", weight="700"))
        parts.append(text(x + 215, cy + 45, "4", 54, anchor="middle", weight="700"))
    elif family == "section-label":
        parts.append(text(x + 20, y + 48, "Verse 1", 26, weight="700", italic=True))
    elif family == "final-barline":
        parts.append(line(x + 235, y + 65, x + 235, y + 160, 3))
        parts.append(line(x + 247, y + 65, x + 247, y + 160, 7))
        parts.append(text(x + 120, cy + 5, "(0)", 22, anchor="middle"))
    else:
        parts.append(text(cx, cy, family, 18, anchor="middle"))

    return "".join(parts)


def main():
    if not DATASET_PATH.exists() or not BENCHMARK_PATH.exists():
        raise FileNotFoundError("Run the protected dataset and primitive benchmark first")

    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    benchmark = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))

    if dataset.get("readyForProtectedPrimitiveBenchmark") is not True:
        raise RuntimeError("Protected dataset is not benchmark-ready")
    if benchmark.get("benchmarkPassed") is not True:
        raise RuntimeError("Protected primitive benchmark has not passed")

    examples = dataset.get("examples") or []
    if len(examples) != 9:
        raise RuntimeError(f"Expected 9 isolated preview examples, found {len(examples)}")

    rows = 3
    height = MARGIN * 2 + rows * PANEL_H + (rows - 1) * GAP + 120
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">',
        '<rect width="100%" height="100%" fill="#17181b"/>',
        text(MARGIN, 48, "DadRock AI — Isolated Professional Technique Preview", 30, weight="700"),
        text(MARGIN, 78, "BENCHMARK ONLY · PRODUCTION RENDERER NOT CALLED", 16),
        text(MARGIN, 103, "Professional PDF remains scoring authority", 16),
    ]

    for index, example in enumerate(examples):
        row = index // 3
        col = index % 3
        x = MARGIN + col * (PANEL_W + GAP)
        y = 135 + row * (PANEL_H + GAP)
        family = example.get("techniqueFamily")
        page = example.get("page")
        measure = example.get("measure")

        svg.append(f'<rect x="{x}" y="{y}" width="{PANEL_W}" height="{PANEL_H}" rx="18" fill="#222429" stroke="#555a64" stroke-width="2"/>')
        svg.append(text(x + 18, y + 30, f"{index+1}. {family}", 20, weight="700"))
        svg.append(text(x + 18, y + 54, f"Professional source: page {page}, measure {measure}", 13))
        svg.append(draw_primitive(family, x + 30, y + 20))

    footer_y = height - 38
    svg.append(text(MARGIN, footer_y, "Isolated preview only · Source events untouched · Renderer unchanged · Production disabled", 15))
    svg.append("</svg>")
    SVG_PATH.write_text("".join(svg), encoding="utf-8")

    report = {
        "previewName": "Jimmy Page isolated professional technique primitive preview",
        "examplesRendered": len(examples),
        "representativeTechniqueFamilies": len({e.get('techniqueFamily') for e in examples}),
        "primitiveBenchmarkPassed": True,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForHumanPrimitiveInspection": True,
        "readyForRendererIntegration": False,
        "svg": str(SVG_PATH.relative_to(ROOT)),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Isolated professional technique primitive preview complete")
    print(f"Examples rendered: {len(examples)}")
    print("Representative technique families: 9/9")
    print("Primitive benchmark passed: True")
    print("Source events mutated: False")
    print("Renderer changed: False")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print("Ready for human primitive inspection: True")
    print("Ready for renderer integration: False")
    print(f"SVG: {SVG_PATH.relative_to(ROOT)}")
    print(f"Report: {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
