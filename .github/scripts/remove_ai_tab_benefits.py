from pathlib import Path
import re

path = Path("app/ai-tab/page.js")
text = path.read_text(encoding="utf-8")
original = text

# Remove only the benefits section that renders BENEFITS.map.
pattern = re.compile(
    r"\n\s*<section className=\"px-5 py-6 sm:px-8\">"
    r"(?:(?!</section>).)*?"
    r"\{BENEFITS\.map\("
    r".*?"
    r"\n\s*</section>"
    r"(?=\n\s*<section className=\"border-t border-zinc-800 bg-black/20 px-5 py-6 sm:px-8\">)",
    re.DOTALL,
)

text, removed = pattern.subn("", text, count=1)

if removed == 0:
    if "{BENEFITS.map" in text:
        raise RuntimeError("Could not safely locate the AI tab benefits section")
    print("Benefits section is already removed.")
elif text == original:
    print("No changes needed.")
else:
    path.write_text(text, encoding="utf-8")
    print("Removed the redundant AI tab benefits section.")
