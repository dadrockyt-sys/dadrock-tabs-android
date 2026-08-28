from pathlib import Path

path = Path('app/page.js')
text = path.read_text()

if 'Open JPG Tab Studio' in text:
    raise SystemExit(0)

marker = '          {/* Tab Studio Token Management - Admin Function 3 */}\n'
if marker not in text:
    raise SystemExit('Admin insertion marker not found')

block = '''          {/* Personal JPG Tab Studio */}
          <div className="bg-zinc-900 border border-orange-500/25 rounded-xl p-6 mb-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <FileText className="w-5 h-5 text-orange-400" />
                  Personal JPG Tab PDF Studio
                </h2>
                <p className="text-zinc-400 mt-1 text-sm max-w-2xl">
                  Assemble your JPG tab pages into a professional DadRock PDF. Original images stay on your device and are embedded directly with proportional scaling only — no OCR, AI redraw, cropping, or measure reflow.
                </p>
              </div>
              <a
                href="/admin/tab-studio"
                className="inline-flex min-h-11 shrink-0 items-center justify-center rounded-lg bg-orange-600 px-5 py-3 text-sm font-black text-white hover:bg-orange-500"
              >
                Open JPG Tab Studio
              </a>
            </div>
          </div>

'''

text = text.replace(marker, block + marker, 1)
path.write_text(text)
