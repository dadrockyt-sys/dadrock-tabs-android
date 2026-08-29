from pathlib import Path

path = Path('app/page.js')
text = path.read_text(encoding='utf-8')

marker = 'Open Backing Track Studio Token Manager'
if marker in text:
    print('BTS token admin link already present.')
    raise SystemExit(0)

needle = '''                <p className="text-zinc-400 mt-1 text-sm">Generate and manage complimentary PDF unlocks, testing tokens, and promotional offers.</p>'''
replacement = needle + '''\n                <a\n                  href="/admin/bts-tokens"\n                  className="mt-3 inline-flex items-center rounded-lg border border-green-500/30 bg-green-500/10 px-3 py-2 text-xs font-bold text-green-300 transition hover:bg-green-500/20"\n                >\n                  Open Backing Track Studio Token Manager →\n                </a>'''

if needle not in text:
    raise SystemExit('AI Tab token admin heading marker was not found; refusing to patch app/page.js.')

path.write_text(text.replace(needle, replacement, 1), encoding='utf-8')
print('Added separate BTS token manager link to current admin panel.')
