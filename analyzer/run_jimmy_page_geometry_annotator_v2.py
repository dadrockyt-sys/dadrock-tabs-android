import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
QUEUE_PATH = PUBLIC / "gomyway-jimmy-paige-human-geometry-annotation-queue.json"
PAGE_DIR = PUBLIC / "jimmy-professional-pages"
HOST = "0.0.0.0"
PORT = 8765

HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>DadRock Geometry Annotator v2</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0b0b0d;color:#fff;font-family:Arial,sans-serif}header{position:sticky;top:0;z-index:50;background:#151519;padding:10px;border-bottom:1px solid #444}.controls{position:sticky;top:64px;z-index:49;display:grid;grid-template-columns:1fr 1fr;gap:8px;background:#101014;padding:8px}.controls button{min-height:58px;border-radius:10px;border:1px solid #666;font-size:17px;font-weight:800;color:#fff;background:#292930}.controls .primary{background:#a84416;border-color:#ff7a2f}.card{padding:10px;background:#17171c;border-bottom:1px solid #333}.wrap{position:relative;width:100%;background:#000;overflow:auto}.wrap img{display:block;width:100%;user-select:none;-webkit-user-drag:none}.wrap canvas{position:absolute;inset:0;width:100%;height:100%;touch-action:none}.ok{color:#8ee68e}.warn{color:#ffbf69}
</style>
</head>
<body>
<header><strong>DadRock AI — Tablet-Safe Annotator</strong><div id="status">Loading…</div></header>
<div class="card"><div id="target"></div><div id="message">Draw a box around the requested symbol.</div></div>
<div class="controls">
<button id="previous">Previous</button><button id="clear">Clear Box</button>
<button id="confirm" class="primary">Confirm & Auto-Save</button><button id="save">Save Again</button>
</div>
<div class="wrap"><img id="img" draggable="false"><canvas id="canvas"></canvas></div>
<div class="card">Progress: <strong id="progress">0/9</strong></div>
<script>
const labels={'full-bend-release':'full bend-and-release curve','vibrato':'vibrato marking','muted-note':'muted X note','pick-direction':'pick-direction symbol','chord-sustain-tie':'chord sustain ties','chord-slide':'chord slide marks','time-signature-change':'time-signature change','section-label':'section heading','final-barline':'final barline'};
let payload,index=0,box=null,start=null,dragging=false;
const img=document.getElementById('img'),canvas=document.getElementById('canvas'),ctx=canvas.getContext('2d');
const msg=document.getElementById('message'),progress=document.getElementById('progress'),target=document.getElementById('target');
function rows(){return payload.queue||payload.annotationQueue||[]}
function current(){return rows()[index]}
function completed(){return rows().filter(r=>r.humanConfirmed===true).length}
function draw(){ctx.clearRect(0,0,canvas.width,canvas.height);if(!box)return;ctx.lineWidth=4;ctx.strokeStyle='#ff7a2f';ctx.fillStyle='rgba(255,122,47,.2)';ctx.fillRect(box.x,box.y,box.w,box.h);ctx.strokeRect(box.x,box.y,box.w,box.h)}
function sizeCanvas(){canvas.width=img.clientWidth;canvas.height=img.clientHeight;draw()}
function show(){const r=current();target.textContent=`${index+1} of ${rows().length}: Page ${r.page}, measure ${r.measure} — ${labels[r.techniqueFamily]||r.techniqueFamily}`;img.onload=()=>{sizeCanvas();if(r.geometry&&Number.isFinite(r.geometry.xStartNormalized)){box={x:r.geometry.xStartNormalized*canvas.width,y:r.geometry.yStartNormalized*canvas.height,w:(r.geometry.xEndNormalized-r.geometry.xStartNormalized)*canvas.width,h:(r.geometry.yEndNormalized-r.geometry.yStartNormalized)*canvas.height};draw()}else box=null};img.src=`/jimmy-professional-pages/page-${r.page}.png?${Date.now()}`;progress.textContent=`${completed()}/${rows().length}`;msg.textContent=r.humanConfirmed?'Already saved. Redraw only if needed.':'Pending confirmation.';document.getElementById('previous').disabled=index===0}
function point(e){const rect=canvas.getBoundingClientRect();return{x:Math.max(0,Math.min(canvas.width,e.clientX-rect.left)),y:Math.max(0,Math.min(canvas.height,e.clientY-rect.top))}}
canvas.addEventListener('pointerdown',e=>{e.preventDefault();canvas.setPointerCapture(e.pointerId);dragging=true;start=point(e);box={x:start.x,y:start.y,w:0,h:0};draw()});
canvas.addEventListener('pointermove',e=>{if(!dragging)return;e.preventDefault();const p=point(e);box={x:Math.min(start.x,p.x),y:Math.min(start.y,p.y),w:Math.abs(p.x-start.x),h:Math.abs(p.y-start.y)};draw()});
function end(e){if(!dragging)return;e.preventDefault();dragging=false;try{canvas.releasePointerCapture(e.pointerId)}catch{}}
canvas.addEventListener('pointerup',end);canvas.addEventListener('pointercancel',end);window.addEventListener('resize',sizeCanvas);
async function saveNow(){const res=await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const out=await res.json();if(!res.ok)throw new Error(out.error||'Save failed');return out}
document.getElementById('clear').onclick=()=>{box=null;draw()};
document.getElementById('previous').onclick=()=>{if(index>0){index--;show()}};
document.getElementById('confirm').onclick=async()=>{if(!box||box.w<5||box.h<5){msg.className='warn';msg.textContent='Draw a larger visible box first.';return}const r=current();r.geometry={xStartNormalized:box.x/canvas.width,yStartNormalized:box.y/canvas.height,xEndNormalized:(box.x+box.w)/canvas.width,yEndNormalized:(box.y+box.h)/canvas.height};r.humanConfirmed=true;r.status='human-confirmed';r.verification={...(r.verification||{}),confirmedAgainstProfessionalPdf:true,reviewer:'Stephen McNally'};msg.className='';msg.textContent='Saving this annotation…';try{const out=await saveNow();progress.textContent=`${out.completed}/${out.total}`;msg.className='ok';msg.textContent=`Saved immediately: ${out.completed}/${out.total}.`;if(index<rows().length-1){index++;setTimeout(show,350)}}catch(e){msg.className='warn';msg.textContent=e.message}};
document.getElementById('save').onclick=async()=>{try{const out=await saveNow();msg.className='ok';msg.textContent=`Queue saved: ${out.completed}/${out.total}.`;progress.textContent=`${out.completed}/${out.total}`}catch(e){msg.className='warn';msg.textContent=e.message}};
fetch('/api/queue').then(r=>r.json()).then(d=>{payload=d;const first=rows().findIndex(r=>r.humanConfirmed!==true);index=first===-1?rows().length-1:first;show()}).catch(e=>document.getElementById('status').textContent=e.message);
</script>
</body></html>'''

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
            self.send_bytes(HTML.encode(), "text/html; charset=utf-8")
            return
        if path == "/api/queue":
            self.send_bytes(QUEUE_PATH.read_bytes(), "application/json")
            return
        requested = (PUBLIC / path.lstrip("/")).resolve()
        if PUBLIC.resolve() not in requested.parents or not requested.is_file():
            self.send_bytes(b"Not found", "text/plain", 404)
            return
        self.send_bytes(requested.read_bytes(), mimetypes.guess_type(requested.name)[0] or "application/octet-stream")

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/save":
            self.send_bytes(b'{"error":"Not found"}', "application/json", 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode())
            rows = payload.get("queue") or payload.get("annotationQueue") or []
            completed = sum(row.get("humanConfirmed") is True for row in rows)
            QUEUE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            self.send_bytes(json.dumps({"saved": True, "completed": completed, "total": len(rows)}).encode(), "application/json")
        except Exception as error:
            self.send_bytes(json.dumps({"error": str(error)}).encode(), "application/json", 400)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    if not QUEUE_PATH.exists():
        raise FileNotFoundError(QUEUE_PATH)
    if not PAGE_DIR.exists():
        raise FileNotFoundError(PAGE_DIR)
    print("Tablet-safe annotator ready on port 8765")
    print("Every confirmation is saved immediately.")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAnnotator stopped.")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
