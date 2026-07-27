from pathlib import Path

path = Path('app/ai-tab/page.js')
text = path.read_text()

upper_old = '''                    <span className="mt-1 inline-flex items-center gap-2 rounded-xl border border-orange-500/50 bg-orange-500/10 px-5 py-3 font-black text-orange-200">
                      Click Here For Preview
                      <ArrowRight size={19} />
                    </span>
                  </a>
'''

upper_new = '''                    <span className="mt-1 inline-flex items-center gap-2 rounded-xl border border-orange-500/50 bg-orange-500/10 px-5 py-3 font-black text-orange-200">
                      Click Here For Preview
                      <ArrowRight size={19} />
                    </span>
                  </a>

                  <a
                    href={previewPdfUrl}
                    download={`${artistName || 'DadRock'}-${songTitle || 'Tab'}-${selectedType || 'preview'}-preview.pdf`}
                    className="mx-4 mb-5 flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-red-600 px-4 py-3 font-black text-white transition hover:scale-[1.01]"
                  >
                    <Download size={19} />
                    Download Preview PDF
                  </a>
'''

lower_old = '''                          <a
                            href={previewPdfUrl}
                            download={`${artistName || 'DadRock'}-${songTitle || 'Tab'}-${selectedType || 'preview'}-preview.pdf`}
                            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-red-600 px-4 py-3 font-black text-white transition hover:scale-[1.01]"
                          >
                            <Download size={19} />
                            Download Preview PDF
                          </a>
'''

if upper_old not in text:
    raise SystemExit('Upper preview launcher block not found')
if lower_old not in text:
    raise SystemExit('Lower download button block not found')

text = text.replace(upper_old, upper_new, 1)
text = text.replace(lower_old, '', 1)
path.write_text(text)
