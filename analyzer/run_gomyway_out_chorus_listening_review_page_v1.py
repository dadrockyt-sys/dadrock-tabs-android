from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PACK_DIR = (
    REPO_ROOT
    / "public"
    / "training"
    / "gomyway-out-chorus-listening-window-pack-v1"
)
MANIFEST_PATH = PACK_DIR / "manifest.json"
OUTPUT_PATH = PACK_DIR / "index.html"

LABELS = (
    "",
    "real-rhythm-articulation",
    "carried-note-or-sustain",
    "percussion-or-transient-leak",
    "duplicate-onset",
    "uncertain",
)


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"Missing listening-pack manifest: {MANIFEST_PATH.relative_to(REPO_ROOT)}"
        )
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def audio_tag(relative_path: str, label: str) -> str:
    src = escape(relative_path, quote=True)
    return (
        '<div class="audio-row">'
        f'<div class="audio-label">{escape(label)}</div>'
        f'<audio controls preload="metadata" src="{src}"></audio>'
        "</div>"
    )


def main() -> None:
    manifest = load_manifest()
    items = manifest.get("items") or manifest.get("reviewItems") or []
    if not items:
        raise ValueError("Listening-pack manifest contains no review items.")

    cards = []
    for item in items:
        measure = int(item.get("measureNumber") or item.get("measure"))
        step = int(item.get("candidateStep") or item.get("step"))
        key = f"m{measure:03d}-s{step:02d}"
        folder = item.get("folder") or key
        band = item.get("confidenceBand") or "unknown"
        target = item.get("targetSeconds") or item.get("targetTimeSeconds")

        options = "".join(
            f'<option value="{escape(label)}">{escape(label or "Choose a judgment")}</option>'
            for label in LABELS
        )

        cards.append(
            f"""
<section class="card" data-key="{key}" data-measure="{measure}" data-step="{step}">
  <h2>Measure {measure}, step {step}</h2>
  <p><strong>Target:</strong> {escape(str(target))} s &nbsp; <strong>Evidence:</strong> {escape(str(band))}</p>
  <div class="grid">
    <div>
      <h3>Tight windows</h3>
      {audio_tag(f"{folder}/other-stem-tight.wav", "Separated other stem")}
      {audio_tag(f"{folder}/full-mix-tight.wav", "Full mix")}
    </div>
    <div>
      <h3>Context windows</h3>
      {audio_tag(f"{folder}/other-stem-context.wav", "Separated other stem")}
      {audio_tag(f"{folder}/full-mix-context.wav", "Full mix")}
    </div>
    <div>
      <h3>Measure windows</h3>
      {audio_tag(f"{folder}/other-stem-measure.wav", "Separated other stem")}
      {audio_tag(f"{folder}/full-mix-measure.wav", "Full mix")}
    </div>
  </div>
  <label class="field-label" for="label-{key}">Judgment</label>
  <select id="label-{key}" class="judgment">{options}</select>
  <label class="field-label" for="notes-{key}">Notes</label>
  <textarea id="notes-{key}" class="notes" rows="3" placeholder="What do you hear at the target?"></textarea>
</section>
"""
        )

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Out-Chorus Listening Review</title>
<style>
  :root {{ color-scheme: dark; font-family: system-ui, sans-serif; }}
  body {{ margin: 0; background: #111; color: #f3f3f3; }}
  main {{ max-width: 1100px; margin: 0 auto; padding: 20px; }}
  h1 {{ margin-bottom: 6px; }}
  .intro {{ color: #c8c8c8; margin-bottom: 20px; }}
  .card {{ border: 1px solid #444; border-radius: 14px; padding: 18px; margin: 18px 0; background: #1b1b1b; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
  .audio-row {{ margin: 10px 0 16px; }}
  .audio-label {{ font-size: .9rem; color: #bbb; margin-bottom: 5px; }}
  audio {{ width: 100%; }}
  .field-label {{ display: block; margin-top: 14px; margin-bottom: 6px; font-weight: 700; }}
  select, textarea {{ width: 100%; box-sizing: border-box; border-radius: 8px; border: 1px solid #555; background: #0d0d0d; color: #fff; padding: 10px; }}
  .actions {{ position: sticky; bottom: 0; background: rgba(17,17,17,.96); border-top: 1px solid #444; padding: 14px 0; display: flex; gap: 10px; flex-wrap: wrap; }}
  button {{ border: 0; border-radius: 999px; padding: 12px 18px; font-weight: 700; cursor: pointer; }}
  #export {{ background: #f59e0b; color: #111; }}
  #copy {{ background: #ddd; color: #111; }}
  #status {{ align-self: center; color: #a7f3d0; }}
</style>
</head>
<body>
<main>
  <h1>Out-Chorus Listening Review</h1>
  <p class="intro">Review the separated stem first, then the full mix. Use context and measure windows only when the tight clip is ambiguous. Nothing is changed automatically.</p>
  {''.join(cards)}
  <div class="actions">
    <button id="export" type="button">Download judgments JSON</button>
    <button id="copy" type="button">Copy judgments JSON</button>
    <span id="status"></span>
  </div>
</main>
<script>
function collect() {{
  const decisions = [...document.querySelectorAll('.card')].map(card => ({{
    measureNumber: Number(card.dataset.measure),
    candidateStep: Number(card.dataset.step),
    judgment: card.querySelector('.judgment').value,
    notes: card.querySelector('.notes').value.trim(),
    reviewedBy: 'user',
    automaticDecisionAllowed: false
  }}));
  return {{
    schemaVersion: 1,
    reviewType: 'out-chorus-listening-adjudication',
    decisions,
    candidateEventsModified: false,
    professionalReferenceModified: false,
    productionPromotionAllowed: false,
    protectedBaselinesChanged: false
  }};
}}

document.getElementById('export').addEventListener('click', () => {{
  const blob = new Blob([JSON.stringify(collect(), null, 2) + '\n'], {{type: 'application/json'}});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'gomyway-out-chorus-listening-judgments-v1.json';
  link.click();
  URL.revokeObjectURL(link.href);
  document.getElementById('status').textContent = 'Downloaded.';
}});

document.getElementById('copy').addEventListener('click', async () => {{
  await navigator.clipboard.writeText(JSON.stringify(collect(), null, 2));
  document.getElementById('status').textContent = 'Copied.';
}});
</script>
</body>
</html>
"""

    OUTPUT_PATH.write_text(html, encoding="utf-8")

    print("Out-Chorus listening review page V1 complete")
    print("Review items:", len(items))
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
