from pathlib import Path
import re

path = Path('app/ai-tab/page.js')
text = path.read_text()

text = text.replace('Review Your Tab Preview', 'Tab Studio Preview')

old_header = '''<div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800 px-4 py-3">
                    <div className="flex min-w-0 items-center gap-3">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-300">
                        <FileText size={20} />
                      </div>

                      <div className="min-w-0">
                        <p className="truncate text-sm font-black text-white">
                          {songTitle}
                        </p>

                        <p className="truncate text-xs text-zinc-500">
                          {artistName} ·{' '}
                          {
                            selectedTypeDetails?.title
                          }
                        </p>
                      </div>
                    </div>

                    <div className="inline-flex items-center gap-2 rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs font-bold text-amber-300">
                      <Lock size={14} />

                      Watermarked Preview
                    </div>
                  </div>'''

new_header = '''<a
                    href={previewPdfUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex w-full flex-col items-center justify-center gap-3 border-b border-zinc-800 px-4 py-5 text-center transition hover:bg-orange-500/5"
                  >
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-300">
                      <FileText size={24} />
                    </div>

                    <div className="min-w-0">
                      <p className="truncate text-base font-black text-white">
                        {songTitle}
                      </p>

                      <p className="truncate text-sm text-zinc-500">
                        {artistName} ·{' '}
                        {selectedTypeDetails?.title}
                      </p>
                    </div>

                    <span className="mt-1 inline-flex items-center gap-2 rounded-xl border border-orange-500/50 bg-orange-500/10 px-5 py-3 font-black text-orange-200">
                      Click Here For Preview
                      <ArrowRight size={19} />
                    </span>
                  </a>'''

if old_header not in text:
    raise SystemExit('Preview header block not found')
text = text.replace(old_header, new_header)

text = re.sub(
    r'''\n\s*\{!previewUnlocked && \(\n\s*<div className="pointer-events-none absolute inset-x-0 bottom-0[\s\S]*?\n\s*</div>\n\s*\)\}''',
    '',
    text,
    count=1,
)

text = text.replace('Watermarked preview ready', '{`${songTitle || \'Tab\'} PDF Preview`}')
text = text.replace('Open Preview PDF', '{`${songTitle || \'Tab\'} PDF Preview`}')

path.write_text(text)
