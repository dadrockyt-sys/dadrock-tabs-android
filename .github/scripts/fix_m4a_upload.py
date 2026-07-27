from pathlib import Path

path = Path("app/ai-tab/page.js")
text = path.read_text(encoding="utf-8")
original = text

old_accept = 'accept=".mp3,.wav,.m4a,.aac,audio/mpeg,audio/wav,audio/x-m4a,audio/aac"'
new_accept = 'accept="audio/*,.mp3,.wav,.m4a,.aac"'

if old_accept in text:
    text = text.replace(old_accept, new_accept, 1)
elif new_accept not in text:
    raise RuntimeError("Could not locate the audio upload accept attribute")

if text == original:
    print("Audio picker already accepts Android M4A files.")
else:
    path.write_text(text, encoding="utf-8")
    print("Enabled Android and Samsung file pickers to select M4A audio.")
