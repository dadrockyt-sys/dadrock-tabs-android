"""Tablet annotator v3: adds an explicit scroll/draw mode toggle."""

import run_jimmy_page_geometry_annotator_v2 as annotator


annotator.HTML = annotator.HTML.replace(
    '<div class="controls">\n<button id="previous">Previous</button>',
    '<div class="controls">\n'
    '<button id="mode" class="primary">Scroll Mode</button>'
    '<button id="previous">Previous</button>',
).replace(
    "const msg=document.getElementById('message'),progress=document.getElementById('progress'),target=document.getElementById('target');",
    "const msg=document.getElementById('message'),progress=document.getElementById('progress'),target=document.getElementById('target');\n"
    "let scrollMode=false;\n"
    "const modeButton=document.getElementById('mode');\n"
    "modeButton.onclick=()=>{\n"
    "  scrollMode=!scrollMode;\n"
    "  canvas.style.pointerEvents=scrollMode?'none':'auto';\n"
    "  modeButton.textContent=scrollMode?'Draw Mode':'Scroll Mode';\n"
    "  modeButton.className=scrollMode?'':'primary';\n"
    "  msg.className=scrollMode?'ok':'';\n"
    "  msg.textContent=scrollMode?'Scroll to the target, then tap Draw Mode.':'Draw a box around the requested symbol.';\n"
    "};",
)


if __name__ == "__main__":
    annotator.main()
