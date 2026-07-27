from pathlib import Path
import re

path = Path('app/ai-tab/page.js')
text = path.read_text(encoding='utf-8')
original = text

# Remove the complete numbered PROCESS_STEPS grid when it still exists.
complete_block = re.compile(
    r'\n\s*<div className="mt-5 grid gap-3 sm:grid-cols-4">\s*'
    r'\{PROCESS_STEPS\.map\(.*?\n\s*</div>',
    re.DOTALL,
)
text = complete_block.sub('', text, count=1)

# Repair the malformed fragment left by the earlier removal. The old pattern
# stopped at the first nested </div>, leaving the end of the map callback in JSX.
orphan_fragment = re.compile(
    r'\n\s*<h3 className="text-sm font-bold text-white">\s*'
    r'\{step\.title\}\s*'
    r'</h3>\s*'
    r'<p className="mt-2 text-xs leading-5 text-zinc-500">\s*'
    r'\{step\.description\}\s*'
    r'</p>\s*'
    r'</div>\s*'
    r'\)\s*'
    r'\}\)\}\s*'
    r'</div>',
    re.DOTALL,
)
text = orphan_fragment.sub('', text, count=1)

# Safety checks: neither the map nor its orphaned callback may remain.
if 'PROCESS_STEPS.map' in text:
    raise RuntimeError('The numbered process-card map is still present.')

if '{step.title}' in text or '{step.description}' in text:
    raise RuntimeError('Orphaned process-card JSX is still present.')

if text == original:
    print('Numbered process cards are already removed and JSX is clean.')
else:
    path.write_text(text, encoding='utf-8')
    print('Removed numbered process cards and repaired the orphaned JSX fragment.')
