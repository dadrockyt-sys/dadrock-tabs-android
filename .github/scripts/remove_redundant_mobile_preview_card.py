from pathlib import Path

path = Path('app/ai-tab/page.js')
text = path.read_text()

start_marker = '                    <div className="p-5 sm:hidden">'
end_marker = '                    <iframe\n                      src={`${previewPdfUrl}#toolbar=0&navpanes=0&scrollbar=1`}'

start = text.find(start_marker)
end = text.find(end_marker, start)

if start == -1:
    raise SystemExit('Redundant mobile preview card start not found')
if end == -1:
    raise SystemExit('Desktop iframe marker not found')

text = text[:start] + text[end:]
path.write_text(text)
