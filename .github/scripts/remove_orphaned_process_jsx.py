from pathlib import Path
import re

path = Path('app/ai-tab/page.js')
text = path.read_text(encoding='utf-8')
original = text

# Remove the malformed leftover process-card JSX that begins with the
# orphaned step title and ends immediately before the status message block.
pattern = re.compile(
    r'\n\s*<h3 className="text-sm font-bold text-white">\s*'
    r'\{step\.title\}\s*'
    r'</h3>\s*'
    r'<p className="mt-2 text-xs leading-5 text-zinc-500">\s*'
    r'\{step\.description\}\s*'
    r'</p>\s*'
    r'</div>\s*'
    r'\)\s*'
    r'\}\)\}\s*'
    r'</div>\s*'
    r'(?=\{statusMessage\s*&&\s*\()',
    re.DOTALL,
)

text, count = pattern.subn('\n', text, count=1)

# Fallback: use stable markers if formatting changed.
if count == 0 and '{step.title}' in text:
    start = text.rfind('\n', 0, text.index('{step.title}'))
    status_index = text.index('{statusMessage && (', text.index('{step.title}'))
    text = text[:start] + '\n' + text[status_index:]
    count = 1

if '{step.title}' in text or '{step.description}' in text:
    raise RuntimeError('Orphaned process-card JSX still remains in page.js')

if count == 0:
    raise RuntimeError('Could not locate the malformed process-card JSX block')

path.write_text(text, encoding='utf-8')
print('Removed malformed process-card JSX and restored valid page structure.')
