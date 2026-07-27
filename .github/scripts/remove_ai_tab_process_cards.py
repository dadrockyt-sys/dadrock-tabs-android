from pathlib import Path
import re

path = Path('app/ai-tab/page.js')
text = path.read_text(encoding='utf-8')
original = text

pattern = re.compile(
    r'\n\s*<div className="mt-5 grid gap-3 sm:grid-cols-4">\s*\n\s*\{PROCESS_STEPS\.map\(.*?\n\s*</div>',
    re.DOTALL,
)

text, count = pattern.subn('', text, count=1)

if count == 0:
    if 'PROCESS_STEPS.map' in text:
        raise RuntimeError('Could not safely remove the numbered process cards.')
    print('Numbered process cards are already removed.')
else:
    path.write_text(text, encoding='utf-8')
    print('Removed the numbered process cards and preserved the SEO content.')
