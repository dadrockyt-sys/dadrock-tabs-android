from pathlib import Path

path = Path('app/ai-tab/page.js')
text = path.read_text(encoding='utf-8')

old = '''                    <iframe
                      src={`${previewPdfUrl}#toolbar=0&navpanes=0&scrollbar=1`}
                      title={`${songTitle} tab preview`}
                      className="h-[520px] w-full bg-white sm:h-[680px]"
                    />'''

new = '''                    <div className="p-5 sm:hidden">
                      <div className="rounded-2xl border border-zinc-700 bg-black/40 p-5 text-center">
                        <FileText
                          size={38}
                          className="mx-auto text-orange-300"
                        />

                        <h3 className="mt-3 text-lg font-black text-white">
                          Watermarked preview ready
                        </h3>

                        <p className="mt-2 text-sm leading-6 text-zinc-400">
                          Android browsers cannot reliably display a temporary PDF inside the page. Open it in a new tab or download it to your device.
                        </p>

                        <div className="mt-5 grid gap-3">
                          <a
                            href={previewPdfUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex w-full items-center justify-center gap-2 rounded-xl border border-orange-500/50 bg-orange-500/10 px-4 py-3 font-black text-orange-200 transition hover:bg-orange-500/20"
                          >
                            <FileText size={19} />
                            Open Preview PDF
                          </a>

                          <a
                            href={previewPdfUrl}
                            download={`${artistName || 'DadRock'}-${songTitle || 'Tab'}-${selectedType || 'preview'}-preview.pdf`}
                            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-red-600 px-4 py-3 font-black text-white transition hover:scale-[1.01]"
                          >
                            <Download size={19} />
                            Download Preview PDF
                          </a>
                        </div>
                      </div>
                    </div>

                    <iframe
                      src={`${previewPdfUrl}#toolbar=0&navpanes=0&scrollbar=1`}
                      title={`${songTitle} tab preview`}
                      className="hidden h-[680px] w-full bg-white sm:block"
                    />'''

if old not in text:
    if 'Download Preview PDF' in text:
        print('Mobile PDF preview controls already applied.')
    else:
        raise RuntimeError('Could not find the existing preview iframe block.')
else:
    text = text.replace(old, new, 1)
    path.write_text(text, encoding='utf-8')
    print('Added mobile open and download controls for the watermarked preview PDF.')
