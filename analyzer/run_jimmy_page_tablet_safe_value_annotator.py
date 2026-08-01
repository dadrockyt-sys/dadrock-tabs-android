import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
QUEUE_PATH = PUBLIC / "gomyway-jimmy-paige-professional-value-annotation-queue.json"
PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"
SAVE_PATH = PUBLIC / "gomyway-jimmy-paige-professional-value-human-annotations.json"
HOST = "0.0.0.0"
PORT = 8765

PDF_PAGE_RANGES = [
    (1, 14, 1),
    (15, 26, 2),
    (27, 42, 3),
    (43, 56, 4),
    (57, 75, 5),
    (76, 89, 6),
    (90, 108, 7),
    (109, 113, 8),
]


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def pdf_page_for_measure(measure: int) -> int:
    for start, end, page in PDF_PAGE_RANGES:
        if start <= measure <= end:
            return page
    return 8


def flatten_review_pages(queue: dict) -> list[dict]:
    pages = []
    for batch in queue.get("batches", []):
        for page in batch.get("tabletPages", []):
            pages.append(
                {
                    "sectionName": batch.get("sectionName"),
                    "priority": batch.get("priority"),
                    "batchIndex": batch.get("batchIndex"),
                    **page,
                }
            )
    return pages


def html_page() -> str:
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>DadRock Professional Value Annotator</title>
<style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,Segoe UI,sans-serif}
*{box-sizing:border-box}body{margin:0;background:#111317;color:#f5f5f5}
header{position:sticky;top:0;z-index:20;background:#171a20;border-bottom:1px solid #343944;padding:10px}
h1{font-size:18px;margin:0 0 4px}.sub{font-size:12px;color:#b9c0cc}
.controls{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:9px}
button,select,input,textarea{font:inherit;border-radius:10px;border:1px solid #495160;background:#222731;color:#fff}
button{min-height:48px;font-weight:800;padding:10px}button.primary{background:#ff7a18;border-color:#ff983f;color:#111}
button.ok{background:#2f8f55;border-color:#55c77f}button:disabled{opacity:.45}
main{padding:10px;display:grid;gap:10px}.card{background:#191d24;border:1px solid #363d49;border-radius:14px;padding:10px}
.status{padding:9px;border-radius:9px;background:#252b35;font-size:13px}.status.saved{background:#173b28;color:#bff5cf}
iframe{width:100%;height:58vh;border:0;border-radius:10px;background:white}
.measure{border-top:1px solid #343b46;padding-top:10px;margin-top:10px}.measure:first-child{border-top:0;margin-top:0;padding-top:0}
.measure h3{margin:0 0 7px;font-size:17px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}
label{font-size:11px;color:#c9d0db;display:grid;gap:4px}input,select{width:100%;min-height:42px;padding:8px}
textarea{width:100%;min-height:76px;padding:8px;resize:vertical}.event{padding:8px;margin:8px 0;background:#222731;border-radius:10px}
.event-head{display:flex;justify-content:space-between;align-items:center;gap:8px}.danger{background:#4a2020;border-color:#874040}
.footer-actions{position:sticky;bottom:0;background:#171a20;border-top:1px solid #343944;padding:10px;display:grid;grid-template-columns:1fr 1fr;gap:8px}
@media(min-width:900px){main{grid-template-columns:1.1fr .9fr;align-items:start}.review{max-height:72vh;overflow:auto}.controls{grid-template-columns:repeat(4,1fr)}}
</style>
</head>
<body>
<header>
<h1>DadRock AI — Professional Value Annotator</h1>
<div class="sub">Professional PDF is the scoring authority. Candidate values are unverified prefill only. Production remains disabled.</div>
<div class="controls">
<button id="previous">Previous Page</button><button id="next">Next Page</button>
<button id="add-event">Add Event</button><button id="confirm" class="primary">Confirm & Auto-Save</button>
</div>
</header>
<main>
<section class="card"><div id="page-title"></div><iframe id="pdf"></iframe></section>
<section class="card review"><div id="status" class="status">Loading…</div><div id="measures"></div></section>
</main>
<div class="footer-actions"><button id="save" class="ok">Save Current Page</button><button id="export">Download Saved JSON</button></div>
<script>
const fields=['positionInMeasure','durationSteps','stringIndex','fret','midiPitch','technique'];
let state={pages:[],pageIndex:0,annotations:{},dirty:false};
const el=id=>document.getElementById(id);
async function api(path,options={}){const r=await fetch(path,options);if(!r.ok)throw new Error(await r.text());return r.json()}
function page(){return state.pages[state.pageIndex]}
function measureNumbers(){const p=page();const out=[];for(let m=p.measureStart;m<=p.measureEnd;m++)out.push(m);return out}
function ensureMeasure(m){const key=String(m);if(!state.annotations[key])state.annotations[key]={measureNumber:m,status:'pending-human-review',events:[],notes:''};return state.annotations[key]}
function eventHtml(m,e,i){return `<div class="event" data-m="${m}" data-i="${i}"><div class="event-head"><strong>Event ${i+1}</strong><button class="danger remove" type="button">Remove</button></div><div class="grid">${fields.map(f=>`<label>${f}<input data-field="${f}" value="${e[f]??''}"></label>`).join('')}</div></div>`}
function render(){const p=page();if(!p)return;el('page-title').innerHTML=`<strong>${p.sectionName}</strong> · measures ${p.measureStart}–${p.measureEnd} · priority ${p.priority}`;el('pdf').src=`/gomyway-professional-reference.pdf#page=${p.pdfPage}&zoom=page-width`;
el('measures').innerHTML=measureNumbers().map(m=>{const a=ensureMeasure(m);return `<div class="measure" data-measure="${m}"><h3>Measure ${m}</h3><div class="events">${a.events.map((e,i)=>eventHtml(m,e,i)).join('')}</div><button class="add-one" type="button">+ Event for measure ${m}</button><label>Reviewer notes<textarea class="notes">${a.notes??''}</textarea></label></div>`}).join('');
el('previous').disabled=state.pageIndex===0;el('next').disabled=state.pageIndex===state.pages.length-1;bindInputs();setStatus(state.dirty?'Unsaved changes':'Ready',false)}
function bindInputs(){document.querySelectorAll('.event input').forEach(input=>input.oninput=()=>{const box=input.closest('.event');const a=ensureMeasure(Number(box.dataset.m));const e=a.events[Number(box.dataset.i)];let v=input.value;if(['positionInMeasure'].includes(input.dataset.field)&&v!=='')v=Number(v);if(['durationSteps','stringIndex','fret','midiPitch'].includes(input.dataset.field)&&v!=='')v=parseInt(v,10);e[input.dataset.field]=v;markDirty()});
document.querySelectorAll('.remove').forEach(b=>b.onclick=()=>{const box=b.closest('.event');ensureMeasure(Number(box.dataset.m)).events.splice(Number(box.dataset.i),1);markDirty();render()});
document.querySelectorAll('.add-one').forEach(b=>b.onclick=()=>{const m=Number(b.closest('.measure').dataset.measure);ensureMeasure(m).events.push({positionInMeasure:0,durationSteps:1,stringIndex:'',fret:'',midiPitch:'',technique:'picked-note'});markDirty();render()});
document.querySelectorAll('.notes').forEach(t=>t.oninput=()=>{ensureMeasure(Number(t.closest('.measure').dataset.measure)).notes=t.value;markDirty()})}
function markDirty(){state.dirty=true;setStatus('Unsaved changes',false)}function setStatus(text,saved){el('status').textContent=text;el('status').className='status'+(saved?' saved':'')}
async function save(confirm=false){const payload={pageIndex:state.pageIndex,measures:Object.fromEntries(measureNumbers().map(m=>[String(m),ensureMeasure(m)])),confirm};setStatus('Saving…',false);const r=await api('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});state.dirty=false;if(confirm)measureNumbers().forEach(m=>state.annotations[String(m)].status='human-confirmed');setStatus(`Saved immediately · ${r.confirmedMeasureCount} measures confirmed`,true)}
async function move(delta){if(state.dirty)await save(false);state.pageIndex=Math.max(0,Math.min(state.pages.length-1,state.pageIndex+delta));render();window.scrollTo(0,0)}
el('previous').onclick=()=>move(-1);el('next').onclick=()=>move(1);el('save').onclick=()=>save(false);el('confirm').onclick=()=>save(true);el('add-event').onclick=()=>{const m=measureNumbers()[0];ensureMeasure(m).events.push({positionInMeasure:0,durationSteps:1,stringIndex:'',fret:'',midiPitch:'',technique:'picked-note'});markDirty();render()};el('export').onclick=()=>location.href='/api/export';
(async()=>{const boot=await api('/api/bootstrap');state.pages=boot.pages;state.annotations=boot.annotations;state.pageIndex=boot.resumePageIndex||0;render()})().catch(e=>setStatus(e.message,false));
</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, data: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload, status: int = 200) -> None:
        self.send_bytes(json.dumps(payload).encode("utf-8"), "application/json", status)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self.send_bytes(html_page().encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/api/bootstrap":
            queue = load_json(QUEUE_PATH, {})
            if queue.get("annotationQueueReady") is not True:
                self.send_json({"error": "Annotation queue is not ready"}, 409)
                return
            saved = load_json(SAVE_PATH, {"annotations": {}, "resumePageIndex": 0})
            pages = flatten_review_pages(queue)
            for page in pages:
                page["pdfPage"] = pdf_page_for_measure(page["measureStart"])
            self.send_json({"pages": pages, "annotations": saved.get("annotations", {}), "resumePageIndex": saved.get("resumePageIndex", 0)})
            return
        if path == "/api/export":
            payload = load_json(SAVE_PATH, {"annotations": {}})
            data = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Disposition", 'attachment; filename="gomyway-professional-value-human-annotations.json"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        target = PUBLIC / path.lstrip("/")
        if target.exists() and target.is_file() and PUBLIC in target.resolve().parents:
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            self.send_bytes(target.read_bytes(), content_type)
            return
        self.send_json({"error": "Not found"}, 404)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/save":
            self.send_json({"error": "Not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            incoming = json.loads(self.rfile.read(length).decode("utf-8"))
            saved = load_json(SAVE_PATH, {"annotations": {}, "resumePageIndex": 0})
            annotations = saved.setdefault("annotations", {})
            confirm = incoming.get("confirm") is True
            for key, value in incoming.get("measures", {}).items():
                if confirm:
                    value["status"] = "human-confirmed"
                annotations[str(key)] = value
            saved["resumePageIndex"] = incoming.get("pageIndex", 0)
            saved["professionalPdfRemainsScoringAuthority"] = True
            saved["candidateValuesAreUnverifiedPrefillOnly"] = True
            saved["sourceEventsMutated"] = False
            saved["rendererChanged"] = False
            saved["productionRendererCalled"] = False
            saved["productionOutputCreated"] = False
            saved["productionPromotionAllowed"] = False
            save_json(SAVE_PATH, saved)
            confirmed = sum(1 for row in annotations.values() if row.get("status") == "human-confirmed")
            self.send_json({"saved": True, "confirmedMeasureCount": confirmed})
        except Exception as error:
            self.send_json({"error": str(error)}, 400)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    if not QUEUE_PATH.exists():
        raise FileNotFoundError(f"Missing queue: {QUEUE_PATH.relative_to(ROOT)}")
    queue = load_json(QUEUE_PATH, {})
    if queue.get("annotationQueueReady") is not True:
        raise RuntimeError("Annotation queue has not passed")
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Missing professional PDF: {PDF_PATH.relative_to(ROOT)}")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Tablet-safe professional value annotator ready on port {PORT}")
    print("Every save is written immediately and atomically.")
    print("Professional PDF remains scoring authority.")
    print("Candidate values are unverified prefill only.")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAnnotator stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
