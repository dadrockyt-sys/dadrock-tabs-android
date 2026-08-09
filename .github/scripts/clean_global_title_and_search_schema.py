from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / 'app/layout.js'
text = path.read_text(encoding='utf-8')

old_title = """  title: {\n    default: 'DadRock Tabs - Guitar & Bass Tabs for Classic Rock',\n    template: '%s | DadRock Tabs',\n  },\n"""
new_title = """  title: 'DadRock Tabs - Guitar & Bass Tabs for Classic Rock',\n"""
if old_title not in text:
    raise SystemExit('root title template block not found')
text = text.replace(old_title, new_title, 1)

old_action = """      'publisher': { '@id': 'https://dadrocktabs.com/#organization' },\n      'inLanguage': 'en',\n      'potentialAction': {\n        '@type': 'SearchAction',\n        'target': {\n          '@type': 'EntryPoint',\n          'urlTemplate': 'https://dadrocktabs.com/search?q={search_term_string}'\n        },\n        'query-input': 'required name=search_term_string'\n      }\n"""
new_action = """      'publisher': { '@id': 'https://dadrocktabs.com/#organization' },\n      'inLanguage': 'en'\n"""
if old_action not in text:
    raise SystemExit('stale SearchAction block not found')
text = text.replace(old_action, new_action, 1)

text = text.replace(
    '        {/* WebSite + Organization structured data for rich results & sitelinks search box */}',
    '        {/* WebSite + Organization structured data */}',
    1,
)

path.write_text(text, encoding='utf-8')

updated = path.read_text(encoding='utf-8')
if "template: '%s | DadRock Tabs'" in updated:
    raise SystemExit('root title template still present')
if 'SearchAction' in updated or 'search_term_string' in updated:
    raise SystemExit('stale search schema still present')
if "title: 'DadRock Tabs - Guitar & Bass Tabs for Classic Rock'" not in updated:
    raise SystemExit('homepage default title missing')

print('Global title duplication and stale search schema removed.')
