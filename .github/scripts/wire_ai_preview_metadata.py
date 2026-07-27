from pathlib import Path

path = Path('app/ai-tab/page.js')
text = path.read_text(encoding='utf-8')
original = text

text = text.replace(
    "  const requestPreviewPdf =\n    async (tabContent) => {",
    "  const requestPreviewPdf =\n    async (tabContent, analysisMetadata = {}) => {",
    1,
)

old_body = """  generatedTab:\n    tabContent,\n\n            previewSystems: 4,"""
new_body = """  generatedTab:\n    tabContent,\n\n  tuning:\n    analysisMetadata.tuning || 'Standard Tuning',\n\n  tempo:\n    analysisMetadata.tempo || 120,\n\n  timeSignature:\n    analysisMetadata.timeSignature || '4/4',\n\n  keySignature:\n    analysisMetadata.keySignature || '',\n\n            previewSystems: 4,"""

if old_body not in text:
    raise RuntimeError('Could not find the preview request body marker.')
text = text.replace(old_body, new_body, 1)

old_call = """        await requestPreviewPdf(\n          tabContent\n        );"""
new_call = """        await requestPreviewPdf(\n          tabContent,\n          analyzerData\n        );"""

if old_call not in text:
    raise RuntimeError('Could not find the preview PDF call marker.')
text = text.replace(old_call, new_call, 1)

required = [
    'analysisMetadata.tuning',
    'analysisMetadata.tempo',
    'analysisMetadata.timeSignature',
    'analysisMetadata.keySignature',
    'tabContent,\n          analyzerData',
]

for marker in required:
    if marker not in text:
        raise RuntimeError(f'Missing expected marker after repair: {marker}')

if text == original:
    raise RuntimeError('No page.js changes were made.')

path.write_text(text, encoding='utf-8')
print('Wired analyzer metadata into the polished tab preview request.')
