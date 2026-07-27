from pathlib import Path

path = Path('app/ai-tab/page.js')
text = path.read_text()

old_download = '''                          <a
                            href={previewPdfUrl}
                            download={`${artistName || 'DadRock'}-${songTitle || 'Tab'}-${selectedType || 'preview'}-preview.pdf`}
                            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-red-600 px-4 py-3 font-black text-white transition hover:scale-[1.01]"
                          >
                            <Download size={19} />
                            Download Preview PDF
                          </a>'''

if old_download not in text:
    raise SystemExit('Download button block not found')

text = text.replace(old_download, '', 1)

launcher_marker = '''                        <span>Click Here For Preview</span>
                        <ArrowRight size={22} />
                      </div>
                    </a>'''

replacement_launcher = '''                        <span>Click Here For Preview</span>
                        <ArrowRight size={22} />
                      </div>
                    </a>

                    <a
                      href={previewPdfUrl}
                      download={`${artistName || 'DadRock'}-${songTitle || 'Tab'}-${selectedType || 'preview'}-preview.pdf`}
                      className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-red-600 px-4 py-3 font-black text-white transition hover:scale-[1.01]"
                    >
                      <Download size={19} />
                      Download Preview PDF
                    </a>'''

if launcher_marker not in text:
    raise SystemExit('Preview launcher marker not found')

text = text.replace(launcher_marker, replacement_launcher, 1)

start_marker = '''                    <div className="p-5 sm:hidden">'''
end_marker = '''                    <iframe
                      src={`${previewPdfUrl}#toolbar=0&navpanes=0&scrollbar=1`}'''

start = text.find(start_marker)
end = text.find(end_marker, start)

if start == -1 or end == -1:
    raise SystemExit('Repeated mobile preview card not found')

text = text[:start] + text[end:]

path.write_text(text)
