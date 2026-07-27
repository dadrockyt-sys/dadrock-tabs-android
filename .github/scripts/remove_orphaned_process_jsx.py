from pathlib import Path

path = Path('app/ai-tab/page.js')
text = path.read_text(encoding='utf-8')
original = text

orphan = '''
                      <h3 className="text-sm font-bold text-white">
                        {step.title}
                      </h3>

                      <p className="mt-2 text-xs leading-5 text-zinc-500">
                        {step.description}
                      </p>
                    </div>
                  )
                )}

              </div>
'''

if orphan in text:
    text = text.replace(orphan, '\n', 1)

if '{step.title}' in text or '{step.description}' in text:
    raise RuntimeError('Orphaned process-card JSX still remains in page.js')

if text == original:
    print('No orphaned process JSX found.')
else:
    path.write_text(text, encoding='utf-8')
    print('Removed orphaned process-card JSX that caused the Turbopack parse error.')
