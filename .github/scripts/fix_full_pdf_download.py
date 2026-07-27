from pathlib import Path

page_path = Path('app/ai-tab/page.js')
page = page_path.read_text()

old = """              songTitle:\n                songTitle.trim(),\n\n              artistName:\n                artistName.trim(),"""
new = """              song:\n                songTitle.trim(),\n\n              artist:\n                artistName.trim(),"""

if old not in page:
    raise RuntimeError('Expected finished PDF payload block was not found')

page = page.replace(old, new, 1)

# Give users immediate visible feedback even before the network request completes.
old_status = """      setIsDownloading(true);\n\n      setStatusMessage(\n        'Creating your finished PDF and preparing email delivery...'\n      );"""
new_status = """      setIsDownloading(true);\n\n      setStatusMessage(\n        'Creating your finished PDF and preparing email delivery...'\n      );\n\n      document\n        .getElementById('download-section')\n        ?.scrollIntoView({\n          behavior: 'smooth',\n          block: 'start',\n        });"""

if old_status in page:
    page = page.replace(old_status, new_status, 1)

page_path.write_text(page)
print('Full PDF download payload repaired successfully.')
