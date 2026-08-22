import json
import mimetypes
import shutil
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"
QUEUE_PATH = PUBLIC / "gomyway-jimmy-paige-human-geometry-annotation-queue.json"
PAGE_DIR = PUBLIC / "jimmy-professional-pages"
HOST = "0.0.0.0"
PORT = 8765


def render_pages() -> list[Path]:
    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(PAGE_DIR.glob("page-*.png"))
    if len(existing) >= 8:
        return existing

    for old in PAGE_DIR.glob("page-*.png"):
        old.unlink()

    try:
        import fitz  # PyMuPDF

        document = fitz.open(PDF_PATH)
        outputs = []
        for index, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
            output = PAGE_DIR / f"page-{index}.png"
            pixmap.save(output)
            outputs.append(output)
        return outputs
    except Exception:
        pass

    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm:
        prefix = PAGE_DIR / "page"
        subprocess.run(
            [pdftoppm, "-png", "-r", "140", str(PDF_PATH), str(prefix)],
            check=True,
        )
        outputs = []
        for index, source in enumerate(sorted(PAGE_DIR.glob("page-*.png")), start=1):
            target = PAGE_DIR / f"page-{index}.png"
            if source != target:
                source.rename(target)
            outputs.append(target)
        return outputs

    raise RuntimeError(
        "Could not render PDF pages. Install PyMuPDF with "
        "'python -m pip install pymupdf' and run this script again."
    )


HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Jimmy Professional Technique Annotator</title>
<style>
  :root { color-scheme: dark; font-family: Arial, sans-serif; }
  * { box-sizing: border-box; }
  body { margin: 0; background: #0b0b0d; color: #f5f5f5; }
  header { position: sticky; top: 0; z-index: 20; padding: 12px; background: #151519; border-bottom: 1px solid #34343b; }
  h1 { margin: 0 0 5px; font-size: 18px; }
  .status { font-size: 13px; color: #c9c9d1; }
  main { max-width: 1100px; margin: auto; padding: 12px; }
  .toolbar { display: grid; gap: 8px; grid-template-columns: 1fr 1fr; margin-bottom: 10px; }
  button { min-height: 45px; border: 1px solid #555; border-radius: 9px; background: #26262d; color: white; font-weight: 700; padding: 8px; }
  button.primary { background: #9a3d11; border-color: #d76a2b; }
  button:disabled { opacity: .45; }
  .card { background: #17171c; border: 1px solid #36363d; border-radius: 12px; padding: 10px; margin-bottom: 10px; }
  .target { font-size: 16px; font-weight: 800; }
  .hint { margin-top: 4px; font-size: 13px; color: #b7b7c0; }
  .canvas-wrap { position: relative; width: 100%; overflow: auto; border: 1px solid #444; background: #000; touch-action: none; }
  #pageImage { width: 100%; display: block; user-select: none; -webkit-user-drag: none; }
  #overlay { position: absolute; inset: 0; width: 100%; height: 100%; touch-action: none; }
  .progress { font-weight: 700; color: #8ee68e; }
  .warning { color: #ffbf69; }
  .done { color: #8ee68e; }
  @media (min-width: 720px) { .toolbar { grid-template-columns: repeat(4, 1fr); } }
</style>
</head>
<body>
<header>
  <h1>DadRock AI — Professional Technique Annotator</h1>
  <div id="status" class="status">Loading annotation queue…</div>
</header>
<main>
  <section class="card">
    <div id="target" class="target"></div>
    <div id="hint" class="hint">Drag a rectangle tightly around the named professional notation symbol. Then tap Confirm.</div>
  </section>
  <div class="toolbar">
    <button id="previous">Previous</button>
    <button id="clear">Clear Box</button>
    <button id="confirm" class="primary">Confirm Annotation</button>
    <button id="save">Save All to Queue</button>
  </div>
  <div class="canvas-wrap" id="wrap">
    <img id="pageImage" alt="Professional PDF page" draggable="false" />
    <canvas id="overlay"></canvas>
  </div>
  <section class="card">
    <div>Progress: <span id="progress" class="progress">0/9</span></div>
    <div id="message" class="hint"></div>
  </section>
</main>
<script>
const techniqueLabels = {
  'full-bend-release': 'full bend-and-release curve',
  'vibrato': 'vibrato marking',
  'muted-note': 'muted X note',
  'pick-direction': 'pick-direction symbol',
  'chord-sustain-tie': 'chord sustain ties',
  'chord-slide': 'chord slide marks',
  'time-signature-change': 'time-signature change',
  'section-label': 'section heading',
  'final-barline': 'final barline'
};
let payload;
let index = 0;
let box = null;
let dragging = false;
let start = null;
const img = document.getElementById('pageImage');
const canvas = document.getElementById('overlay');
const ctx = canvas.getContext('2d');
const status = document.getElementById('status');
const target = document.getElementById('target');
const progress = document.getElementById('progress');
const message = document.getElementById('message');

function rows() { return payload.queue || payload.annotationQueue || []; }
function current() { return rows()[index]; }
function completed() { return rows().filter(r => r.humanConfirmed === true).length; }

function fitCanvas() {
  canvas.width = img.clientWidth;
  canvas.height = img.clientHeight;
  draw();
}
function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (!box) return;
  ctx.lineWidth = 3;
  ctx.strokeStyle = '#ff7a2f';
  ctx.fillStyle = 'rgba(255,122,47,.17)';
  ctx.fillRect(box.x, box.y, box.w, box.h);
  ctx.strokeRect(box.x, box.y, box.w, box.h);
}
function show() {
  const row = current();
  target.textContent = `${index + 1} of ${rows().length}: Page ${row.page}, measure ${row.measure} — ${techniqueLabels[row.techniqueFamily] || row.techniqueFamily}`;
  img.src = `/jimmy-professional-pages/page-${row.page}.png`;
  box = null;
  if (row.geometry && Number.isFinite(row.geometry.xStartNormalized)) {
    const apply = () => {
      box = {
        x: row.geometry.xStartNormalized * canvas.width,
        y: row.geometry.yStartNormalized * canvas.height,
        w: (row.geometry.xEndNormalized - row.geometry.xStartNormalized) * canvas.width,
        h: (row.geometry.yEndNormalized - row.geometry.yStartNormalized) * canvas.height
      };
      draw();
    };
    img.onload = () => { fitCanvas(); apply(); };
  } else {
    img.onload = fitCanvas;
  }
  status.textContent = 'Professional PDF remains the scoring authority. Renderer and production output remain disabled.';
  progress.textContent = `${completed()}/${rows().length}`;
  document.getElementById('previous').disabled = index === 0;
  message.textContent = row.humanConfirmed ? 'This annotation is confirmed. You may redraw it or continue.' : 'Pending human confirmation.';
}
function point(event) {
  const rect = canvas.getBoundingClientRect();
  const source = event.touches ? event.touches[0] : event;
  return { x: Math.max(0, Math.min(canvas.width, source.clientX - rect.left)), y: Math.max(0, Math.min(canvas.height, source.clientY - rect.top)) };
}
function begin(event) { event.preventDefault(); dragging = true; start = point(event); box = {x:start.x,y:start.y,w:0,h:0}; draw(); }
function move(event) { if (!dragging) return; event.preventDefault(); const p=point(event); box={x:Math.min(start.x,p.x),y:Math.min(start.y,p.y),w:Math.abs(p.x-start.x),h:Math.abs(p.y-start.y)}; draw(); }
function end(event) { if (!dragging) return; event.preventDefault(); dragging=false; }
canvas.addEventListener('mousedown', begin); canvas.addEventListener('mousemove', move); canvas.addEventListener('mouseup', end);
canvas.addEventListener('touchstart', begin, {passive:false}); canvas.addEventListener('touchmove', move, {passive:false}); canvas.addEventListener('touchend', end, {passive:false});
window.addEventListener('resize', fitCanvas);

document.getElementById('clear').onclick = () => { box=null; draw(); };
document.getElementById('previous').onclick = () => { if (index>0) { index--; show(); } };
document.getElementById('confirm').onclick = () => {
  if (!box || box.w < 5 || box.h < 5) { message.textContent = 'Draw a visible box first.'; message.className='hint warning'; return; }
  const row = current();
  row.geometry = {
    xStartNormalized: box.x / canvas.width,
    yStartNormalized: box.y / canvas.height,
    xEndNormalized: (box.x + box.w) / canvas.width,
    yEndNormalized: (box.y + box.h) / canvas.height
  };
  row.humanConfirmed = true;
  row.status = 'human-confirmed';
  row.verification = {...(row.verification || {}), confirmedAgainstProfessionalPdf: true, reviewer: 'Stephen McNally'};
  message.className='hint done';
  message.textContent='Annotation confirmed.';
  progress.textContent=`${completed()}/${rows().length}`;
  if (index < rows().length - 1) { index++; setTimeout(show, 250); }
};
document.getElementById('save').onclick = async () => {
  message.className='hint'; message.textContent='Saving…';
  const response = await fetch('/api/save', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
  const result = await response.json();
  if (!response.ok) { message.className='hint warning'; message.textContent=result.error || 'Save failed.'; return; }
  message.className='hint done';
  message.textContent=`Saved ${result.completed}/${result.total} confirmed annotations to the queue file.`;
};

fetch('/api/queue').then(r => r.json()).then(data => { payload=data; show(); }).catch(error => { status.textContent=error.message; });
</script>
</body>
</html>'''


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self.send_bytes(HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/api/queue":
            self.send_bytes(QUEUE_PATH.read_bytes(), "application/json")
            return
        requested = (PUBLIC / path.lstrip("/")).resolve()
        if PUBLIC.resolve() not in requested.parents or not requested.is_file():
            self.send_bytes(b"Not found", "text/plain", 404)
            return
        content_type = mimetypes.guess_type(requested.name)[0] or "application/octet-stream"
        self.send_bytes(requested.read_bytes(), content_type)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/save":
            self.send_bytes(b'{"error":"Not found"}', "application/json", 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            rows = payload.get("queue") or payload.get("annotationQueue") or []
            completed = sum(row.get("humanConfirmed") is True for row in rows)
            QUEUE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            response = json.dumps({"saved": True, "completed": completed, "total": len(rows)}).encode("utf-8")
            self.send_bytes(response, "application/json")
        except Exception as error:
            response = json.dumps({"error": str(error)}).encode("utf-8")
            self.send_bytes(response, "application/json", 400)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Missing professional PDF: {PDF_PATH}")
    if not QUEUE_PATH.exists():
        raise FileNotFoundError(f"Missing annotation queue: {QUEUE_PATH}")

    pages = render_pages()
    print("Jimmy professional technique annotator ready")
    print(f"Rendered pages available: {len(pages)}")
    print(f"Annotation queue: {QUEUE_PATH.relative_to(ROOT)}")
    print(f"Open the forwarded Codespaces URL for port {PORT}")
    print("Use the browser tool to draw and confirm all nine geometry boxes.")
    print("Press Ctrl+C only after Save All to Queue reports 9/9.")

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAnnotator stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
