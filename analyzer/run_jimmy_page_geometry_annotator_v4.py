"""Tablet annotator v4: auto-saves the final barline when drawing ends."""

import run_jimmy_page_geometry_annotator_v3 as v3


annotator = v3.annotator

annotator.HTML = annotator.HTML.replace(
    "function end(e){if(!dragging)return;e.preventDefault();dragging=false;try{canvas.releasePointerCapture(e.pointerId)}catch{}}",
    "async function end(e){"
    "if(!dragging)return;"
    "e.preventDefault();dragging=false;"
    "try{canvas.releasePointerCapture(e.pointerId)}catch{}"
    "const r=current();"
    "if(r&&r.techniqueFamily==='final-barline'&&box&&box.w>=5&&box.h>=5){"
    "r.geometry={xStartNormalized:box.x/canvas.width,yStartNormalized:box.y/canvas.height,xEndNormalized:(box.x+box.w)/canvas.width,yEndNormalized:(box.y+box.h)/canvas.height};"
    "r.humanConfirmed=true;r.status='human-confirmed';"
    "r.verification={...(r.verification||{}),confirmedAgainstProfessionalPdf:true,reviewer:'Stephen McNally'};"
    "msg.className='';msg.textContent='Final barline detected — auto-saving…';"
    "try{const out=await saveNow();progress.textContent=`${out.completed}/${out.total}`;msg.className='ok';msg.textContent=`Final barline saved automatically: ${out.completed}/${out.total}.`;document.getElementById('status').textContent='All annotations saved.';}"
    "catch(error){msg.className='warn';msg.textContent=error.message;}"
    "}"
    "}",
)


if __name__ == "__main__":
    annotator.main()
